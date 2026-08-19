from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.b2b_cohorts import B2BCohorts
import logging
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
import uuid
class Transform:
    def __init__(self, pipeline: B2BCohorts):
        self.pipeline = pipeline        
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.customers = {}
        self.no_orders = []
        self.cohorts = {
            'New': [],
            'Existing': [],
            'Dormant': [],
            'Reactivated': [],
            'Lost': [],
            'New Parts & Accessories': [],
            'Existing Parts & Accessories Only': [],
            'Product Dormant - P&A Active': [],
            'Product Lost - P&A Active': [],
        }
        self.all_customers = []
        pass


    def landing(self, data_extract: dict[str, pl.DataFrame]):
        order_history = data_extract['order_history'].to_dicts()
        bp = 'here'
        self.logger.info(f'Iterating through order history query')
        self.now = datetime.now(ZoneInfo('America/New_York')).date()
        for i, order in enumerate(order_history):
            self.initial_iterator(order=order)
        self.customer_landing()
        self.assign_cohorts()
        self.all_customers.extend([
            {
                **customer, 
                'Cohort': 'Never Ordered',
                'AnchorDate': None,
                'AnchorType': None,
                'LastProductDate': None,
                'LastPADate': None,
                'MonthsSinceProduct': None,
                'MonthsSincePA': None,
                'CustomerCreated': customer['CreatedOn']
             } 
            for customer in self.no_orders])
        self.__postgame__()
        return self.all_customers

    def __postgame__(self):
        report_str = '\n'.join([f'{k}: {len(v)} customers ({round(round(len(v)/len(self.customers), 4) * 100, 2)}%)' for k, v in self.cohorts.items()])
        self.logger.info(f"\nTransformation report:\n{report_str}")

        

    def initial_iterator(self, order: dict):
        ''':class:`~Transform`.:meth:`~initial_iterator`
        ---
        
        Handles the main iterative functions that would take place in the :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform.landing` method

        For each order, checks self.:attr:`~customers` to determine if that customer has any orders. If not, creates a list and registers first entry. If so, appends to list

        Parameters
        ---
        :param (*dict*) `order`: dictionary of order data, recent orders first
        
        <hr>
        
        Sets
        ---
         #### self.:attr:`~customers`

         #### self.:attr:`~no_orders`

        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform.landing`
        
          - Called for each order to determine which CustomerID it should fall under
        '''
        bp = 'here'
        if self.customers.get(order['CustomerID']) == None:        
            if order['PartProdAccFee'] != 'No Orders':
                self.customers[order['CustomerID']] = [order]
            else:
                self.no_orders.append({'CustomerID': order['CustomerID'], 'Customer': order['AccountName'], 'CreatedOn': order['CreatedOn']})
        else:
            if order['PartProdAccFee'] != 'No Orders':
                self.customers[order['CustomerID']].append(order)
            else:
                self.no_orders.append({'CustomerID': order['CustomerID'], 'Customer': order['AccountName'], 'CreatedOn': order['CreatedOn']})


    def customer_landing(self):
        ''':class:`~Transform`.:meth:`~customer_landing`
        ---
        
        After putting all distinct customers in a dictionary (CustomerID is key value), iterate through each of the orders found and check for a gap of a year or more. If there is a gap, filter the orders before the order after the gap out.
        
        Logic is as follows:
            - **For each *customer***, then **for each of their *orders***, check the date. 
                - If we aren't on the last list item
                    - Grab the next order in the list and get its date. Since we're sorted by DatePlaced desc, the next order is stepping back in time
                    - Check the difference in days between the current order and last order
                    - If greater than a year, then stop list at current order and break
                - If we are on the last list item
                    - Keep list unchanged

        <hr>
        
        Sets
        ---
         #### Modifies self.:attr:`~customers`

        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform.landing`
        
          - Only called after :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform.initial_iterator` is called and fills self.:attr:`~customers`
        '''
        bp = 'here'
        total = len(self.customers)
        for i, (customer, orders) in enumerate(self.customers.items()):
            orders.sort(key=lambda o: o['DatePlaced'], reverse=True)
            self.log_prefix = f'{customer}, {i+1}/{total}: '
            self.logger.info(f'{self.log_prefix}{len(orders)} orders')
            for j, order in enumerate(orders):
                self.log_prefix = f'{customer}, {i+1}/{total} ({j+1}/{len(orders)}): '
                bp = 'here'
                order_date = order['DatePlaced']
                prior_order_date = orders[j+1]['DatePlaced'] if j+1 < len(orders) else None
                diff = (order_date - prior_order_date).days  if prior_order_date != None else None
                if diff == None:
                    break
                elif diff >= 365:
                    self.customers[customer] = orders[:j+1]
                    self.logger.info(f'{self.log_prefix}Gap found! Trimming orders to {len(orders)}')
                    break
                bp = 'here'
            self.customers[customer].sort(key=lambda x: x['DatePlaced'])
            bp = 'here'
        bp = 'here'


    def assign_cohorts(self):
        ''':class:`~Transform`.:meth:`~assign_cohorts`
        ---

        Walks each customer's cycle-trimmed, ascending-sorted order history (built by self.:meth:`~customer_landing`) forward in time to compute the aggregates needed to classify their current relationship cycle, then hands them to self.:meth:`~_classify_cohort_` to get the final cohort.

        Logic is as follows:
            - **For each *customer***, then **for each of their *orders*** (oldest to newest):
                - If the order is a product order:
                    - If no product order has been seen yet this cycle, this order becomes the anchor as **New** - covers a first-ever product purchase, a Lost customer's return, and a Parts & Accessories-only customer's first product purchase (Fix 1)
                    - Else if 6+ months have passed since the last product order, this order becomes the anchor as **Reactivated**
                    - Mark `has_product_history = True` and update `last_product_date`
                - Else (Parts & Accessories order): update `last_pa_date`
            - Convert `anchor_date`, `last_product_date`, and `last_pa_date` into calendar-month distances from the reporting date (self.:attr:`~now`)
            - Pass the aggregates to self.:meth:`~_classify_cohort_` and record the resulting cohort

        <hr>

        Sets
        ---
        self.:attr:`~cohorts`
        self.:attr:`~all_customers`

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform.landing`

          - Only called after self.:meth:`~customer_landing` has trimmed each customer's orders down to their current relationship cycle

        ## Downstream Calls (Methods/Functions called)

         ### :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform._months_between_`

          - Called to convert the anchor, last-product, and last-P&A dates into calendar-month distances from the reporting date

         ### :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform._classify_cohort_`

          - Called once per customer with the computed aggregates to determine the final cohort
        '''
        total = len(self.customers)
        for i, (customer, orders) in enumerate(self.customers.items()):
            self.log_prefix = f'{customer}, {i+1}/{total}: '
            anchor_date = orders[0]['DatePlaced']
            created_on = orders[0]['CreatedOn']
            anchor_type = 'New Parts & Accessories'
            has_product_history = False
            last_product_date = None
            last_pa_date = None

            for order in orders:
                order_date = order['DatePlaced']
                is_product = order['PartProdAccFee'] != 'Parts/Accessories'
                if is_product:
                    if not has_product_history:
                        anchor_date, anchor_type = order_date, 'New'
                    elif self._months_between_(last_product_date, order_date) >= 6:
                        anchor_date, anchor_type = order_date, 'Reactivated'
                    has_product_history = True
                    last_product_date = order_date
                else:
                    last_pa_date = order_date

            months_since_product = self._months_between_(last_product_date, self.now) if last_product_date else None
            months_since_pa = self._months_between_(last_pa_date, self.now) if last_pa_date else None
            months_since_anchor = self._months_between_(anchor_date, self.now)
            
            cohort = self._classify_cohort_(
                has_product_history=has_product_history,
                months_since_product=months_since_product,
                months_since_pa=months_since_pa,
                months_since_anchor=months_since_anchor,
                anchor_type=anchor_type,
                last_product_date=last_product_date,
                last_pa_date=last_pa_date,
            ) or ''
            self.logger.info(f'{self.log_prefix}{cohort}')
            customer_cohort = {
                'CustomerID': customer,
                'Cohort': cohort,
                'AnchorDate': anchor_date,
                'AnchorType': anchor_type,
                'LastProductDate': last_product_date,
                'LastPADate': last_pa_date,
                'MonthsSinceProduct': months_since_product,
                'MonthsSincePA': months_since_pa,
                'CustomerCreated': created_on
            }
            self.cohorts[cohort].append(customer_cohort)
            self.all_customers.append(customer_cohort)
            bp = 'here'


    def _months_between_(self, start_date, end_date):
        delta = relativedelta(end_date, start_date)
        return delta.years * 12 + delta.months


    def _classify_cohort_(self, has_product_history: bool, months_since_product: int | None, months_since_pa: int | None, months_since_anchor: int, anchor_type: str, last_product_date, last_pa_date: datetime | None):
        ''':class:`~Transform`.:meth:`~_classify_cohort_`
        ---

        Applies the Step B cohort decision tree (first match wins) to one customer's current-cycle aggregates, as computed by self.:meth:`~assign_cohorts`: checks for total inactivity first (**Lost**), then whether the customer is still inside their anchor's 12-month window without having tripped the relevant dormancy threshold early (returns `anchor_type` as-is), then branches on whether the customer has any product history at all to pick between the Parts & Accessories-only cohorts and the product-history cohorts.

        Parameters
        ---
        :param (*bool*) `has_product_history`: Whether at least one product transaction has occurred within the current relationship cycle
        :param (*int | None*) `months_since_product`: Calendar-month distance from the last in-cycle product transaction to the reporting date; `None` if no product transaction occurred this cycle
        :param (*int | None*) `months_since_pa`: Calendar-month distance from the last in-cycle Parts & Accessories transaction to the reporting date; `None` if no Parts & Accessories transaction occurred this cycle
        :param (*int*) `months_since_anchor`: Calendar-month distance from the anchor transaction (whichever transaction most recently opened a New / Reactivated / New Parts & Accessories clock) to the reporting date
        :param (*str*) `anchor_type`: The status opened by the anchor transaction - one of `'New'`, `'Reactivated'`, `'New Parts & Accessories'`
        :param (*date | None*) `last_product_date`: Date of the last in-cycle product transaction, or `None` if there wasn't one
        :param (*date | None*) `last_pa_date`: Date of the last in-cycle Parts & Accessories transaction, or `None` if there wasn't one

        <hr>

        Returns
        ---
        :return `cohort` (*str*): One of the nine cohort names used as keys in self.:attr:`~cohorts`

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.b2b_cohorts.Transform`.:meth:`~integration_platform.transform.b2b_cohorts.Transform.assign_cohorts`

          - Called once per customer, after the current-cycle aggregates have been computed, to get the final cohort
        '''
        no_product_activity = months_since_product is None or months_since_product >= 12
        no_pa_activity = months_since_pa is None or months_since_pa >= 12
        if no_product_activity and no_pa_activity:
            return 'Lost'

        if months_since_anchor < 12:
            if anchor_type == 'New Parts & Accessories':
                if months_since_pa is not None and months_since_pa < 6:
                    return anchor_type
            elif months_since_product is not None and months_since_product < 6:
                return anchor_type

        if not has_product_history:
            assert months_since_pa is not None  # non-empty cycle with no product orders => at least one P&A order
            return 'Existing Parts & Accessories Only' if months_since_pa < 6 else 'Dormant'

        assert months_since_product is not None  # has_product_history True => last_product_date was set
        if months_since_product < 6:
            return 'Existing'
        elif months_since_product < 12:
            pa_since_product = last_pa_date != None and last_pa_date > last_product_date and months_since_pa != None and months_since_pa > 6
            if not pa_since_product or (months_since_pa != None and months_since_pa > 6):
                return 'Dormant'
            else:
                'Product Dormant - P&A Active'
        else:
            return 'Product Lost - P&A Active'









