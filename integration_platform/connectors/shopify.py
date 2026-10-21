import logging
from integration_platform.config.settings import SHOPIFY
from datetime import date, timedelta
import requests
import time
import json
class ShopifyAPI:
    def __init__(self, pipeline):
        self.pipeline = pipeline    
        if type(pipeline) == str:            
            self.logger = logging.getLogger(f'{pipeline}.ShopifyAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.ShopifyAPI')
        self.domain = SHOPIFY['domain']
        self.version = SHOPIFY['version']
        self.token = SHOPIFY['token']
        self.key = SHOPIFY['key']
        self.secret = SHOPIFY['secret']
        self.url = f'https://{self.domain}/admin/api/{self.version}/graphql.json'
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token
        }
        self.since = date(2024, 1, 1).isoformat()         # or: (date.today() - timedelta(days=90)).isoformat()
        self.until = (date.today() - timedelta(days=1)).isoformat()  # yesterday
        self._set_shopql_()
        self.session = requests.Session()
        pass


    #MARK: post
    def post(self, url: str = '', headers: dict = {}, payload: dict = {}):
        url = self.url if url == '' else url
        headers = self.headers if headers == {} else headers
        payload = {"query": self.graphql_query, "variables": {"shopifyql": self.shopifyql}} if payload == {} else payload
        try:
            response = self.session.post(url = url, headers = headers, json = payload)
            response.raise_for_status()
        except Exception as e:
            bp = 'here'
        try:
            data = response.json()
        except Exception as e:
            bp = 'here'
        return data


    #MARK: _set_shopql_
    def _set_shopql_(self):
        self.shopifyql = f"""
        FROM sales
          SHOW gross_sales, net_sales
          WHERE is_canceled_order = false
          GROUP BY order_name, day, order_utm_source, utm_source
          TIMESERIES day
          HAVING gross_sales__last_click != 0
          SINCE '2026-01-01' UNTIL '2026-04-23'
          ORDER BY day ASC
        """.strip()

        self.graphql_query = """
        query SalesUtmReport($shopifyql: String!) {
        shopifyqlQuery(query: $shopifyql) {
            tableData {
            columns { name displayName dataType }
            rows
            }
            parseErrors
        }
        }
        """

        self.shopql_bulk_customers = """
{
  customers {
    edges { node {
      id firstName lastName
      defaultEmailAddress { emailAddress marketingState }
      defaultPhoneNumber { phoneNumber }
      tags note createdAt numberOfOrders
      amountSpent { amount currencyCode }
      addressesV2 { edges { node { id address1 city province zip country } } }
      metafields { edges { node { id namespace key value } } }
      orders { edges { node { id name createdAt totalPriceSet { shopMoney { amount } } } } }
    } }
  }
}
"""

    #MARK: get_customers_bulk
    def get_customers_bulk(self) -> list[dict]:
        ''':class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI.get_customers_bulk`
        ---
        
        Runs ShopQL to pull all shopify customers and their data via bulk process. It get the `operation_id`, then waits for the results to be ready. Once ready, the results are returned as a list
        
        Returns
        ---
        :return `results` (list[dict]): list of customer records if there are any. Empty list if not
        
        <hr>
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI._start_bulk_query_`
        
          - Sends ShopQL query to Shopify and starts running bulk query
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI._wait_for_bulk_query_`
           
          - After starting the bulk query, poll the current operation for the url to the results until one is available or timeout (1hr)
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI._download_bulk_results_`
           
          - Once the url has been returned from :meth:`~integration_platform.connectors.shopify.ShopifyAPI._wait_for_bulk_query_`, load contents to a list of dicts
        '''        
        operation_id = self._start_bulk_query_(self.shopql_bulk_customers)
        url = self._wait_for_bulk_query_()
        if url:
            results = self._download_bulk_results_(url=url)
            return results
        return []

    #MARK: _start_bulk_query_
    def _start_bulk_query_(self, inner_query: str) -> str:
        ''':class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI._start_bulk_query_`
        ---
        
        Given a ShopQL query, begin executing a bulk query via ShopifyAPI
        
        Parameters
        ---
        :param (*str*) `inner_query`: inner section of ShopQL query to send to Shopify
        
        Returns
        ---
        :return `operation_id` (str): Unique ID of bulk query operation
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI.get_customers_bulk`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI.post`
        
          - **Post**s payload to shopify
        '''        
        mutation = '''
        mutation($q: String!) {
        bulkOperationRunQuery(query: $q) {
            bulkOperation { id status }
            userErrors { field message }
        }
        }'''
        data = self.post(payload={'query': mutation, 'variables': {'q': inner_query}})
        result = data['data']['bulkOperationRunQuery']
        if result['userErrors']:
            raise RuntimeError(f'Bulk op rejected: {result['userErrors']}')
        self.logger.info(f'Started bulk op {result['bulkOperation']['id']}')
        operation_id = result['bulkOperation']['id']
        return operation_id
    
    #MARK: _wait_for_bulk_query_
    def _wait_for_bulk_query_(self, poll_seconds: int = 10, timeout: int = 3600) -> str | None:
        ''':class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI._wait_for_bulk_query_`
        ---
        
        After starting a bulk query operation, this method is called while the results are being compiled. Method waits until results are ready or timeout window is hit (default = 1hr)
        
        Parameters
        ---        
                
           ### ***Optional***
        :param (*int = 10*) `poll_seconds`: How often we should poll shopify to see if the results are ready
        :param (*int = 3600*) `timeout`: How long should we try to wait for results
        
        Returns
        ---
        :return `url` (str | None): Url to results, or None if no url is found
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI.get_customers_bulk`
        
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI._wait_for_bulk_query_`
        
          - Checks to see if bulk query operation is complete
        '''        
        poll = '{ currentBulkOperation(type: QUERY) { id status errorCode objectCount url } }'
        start = time.time()
        while time.time() - start < timeout:
            op = self.post(payload={'query': poll})['data']['currentBulkOperation']
            if op['status'] == 'COMPLETED':
                url = op.get('url')
                return url
            elif op['status'] == 'RUNNING':
                count = op['objectCount']
                error = op['errorCode']
                self.logger.info(f'Operation still running...{f'{count} objects' if count else f'Error! {error}' if error else ''}')
            if op['status'] in ('FAILED', 'CANCELED', 'EXPIRED'):
                raise RuntimeError(f'Bulk op {op['status']}: {op['errorCode']}')
            time.sleep(poll_seconds)
        raise TimeoutError('Bulk op did not finish in time')
    
    #MARK: _download_bulk_results_
    def _download_bulk_results_(self, url: str) -> list[dict]:
        ''':class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI._download_bulk_results_`
        ---
        
        Once we've received a url from :meth:`~integration_platform.connectors.shopify.ShopifyAPI._wait_for_bulk_query_`, retrieve the results found at the passed url
        
        Parameters
        ---
        :param (*str*) `url`: url to retrieve results from
        
        Returns
        ---
        :return `customers` (list[dict]): list of customer records and data
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.shopify.ShopifyAPI`.:meth:`~integration_platform.connectors.shopify.ShopifyAPI.get_customers_bulk`
        '''        
        customers, children = {}, []
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                obj = json.loads(line)
                if '__parentId' in obj:
                    children.append(obj)
                else:
                    customers[obj['id']] = {**obj, 'addresses': [], 'metafields': [], 'orders': []}
        for c in children:
            kind = c['id'].split('/')[3]    #gid://shopify/Order/123 -> 'Order'
            key = {'Order': 'orders', 'MailingAddress': 'addresses', 'Metafield': 'metafields'}[kind]
            customers[c['__parentId']][key].append(c)
        customers = list(customers.values())
        return customers