import polars as pl
import logging
from datetime import datetime, timedelta

class Transform:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass


    def landing(self, data_extract: dict[str, pl.DataFrame]):
        self.data_extract = data_extract
        self.raw_b2b_sales = data_extract['raw_b2b_sales']
        self.int_b2b_sales = data_extract['int_b2b_sales']
        self.b2b_customer_order_history = data_extract['b2b_customer_order_history']
        self.customer_age = data_extract['customer_age']
        self.sql = pl.SQLContext(
            raw_B2BSalesSummary = self.raw_b2b_sales,
            int_B2BSalesSummary = self.int_b2b_sales,
            B2BCustomerOrderHistory = self.b2b_customer_order_history,
            B2BCustomerAgeCategory = self.customer_age,
        )
        sales_by_customer = self.sales_by_metric(['b.CustomerID', 'b.CustomerType'])
        sales_by_customer_type = self.sales_by_metric(['b.CustomerType'])
        customers_with_age = self.new_with_parts()

        data_transformed = {
            'analytics.raw_B2BSalesSummary': self.raw_b2b_sales,
            'analytics.int_B2BSalesSummary': self.int_b2b_sales,
            'analytics.int_B2BCustomerOrderHistory': self.b2b_customer_order_history,
            'analytics.int_B2BCustomerAgeCategory': self.customer_age,
            'analytics.JHL_B2BRevenueByCustomer': sales_by_customer,
            'analytics.JHL_B2BRevenueByCustomerType': sales_by_customer_type

        }
        bp = 'here'
        return data_transformed
    

    def sales_by_metric(self, metric_name: list):
        grouped_metric_name = [metric.split(' as ')[0] if ' as ' in metric else metric for metric in metric_name]
        metric_str = ', '.join(metric_name)
        grouped_metric_str  = ', '.join(grouped_metric_name)
        self.logger.info(f'Querying for aggregated sales by {metric_str}')
        aggregated_sales = self.sql.execute(
            query=f"""
        with TopLevel as(
        select {metric_str}
             , FinPeriod
             , count(distinct OrderNbr) Orders
             , sum(Total_Qty) UnitsSold
             , cast(sum(s.Total_Revenue) as decimal(18,2)) Booked
             , cast(sum(case when s.Shipped = 1 then s.Total_Revenue else 0 end) as decimal(18,2)) Shipped
        from raw_B2BSalesSummary s
        inner join B2BCustomerAgeCategory b on s.CustomerID = b.CustomerID
        group by FinPeriod, {grouped_metric_str}
        )
        select *
             , t.UnitsSold/t.Orders UnitsPerOrder
             , t.Booked/Orders AverageOrderValue
        from TopLevel t
        """).collect()
        # self.sql.register(name='int_SalesSummaryB2B', frame=aggregated_sales)
        self.logger.info(f'{len(aggregated_sales)} rows returned by Calls by {metric_str} query')
        return aggregated_sales


    










    
    def new_with_parts(self):
        self.logger.info(f'Querying new customers for further customer type distinction...')
        new_with_orders = self.customer_age.sql(
            query="""
select *
from self
where CustomerType = 'New' and LastOrder is not null
"""
        )
        new_with_orders_dict = new_with_orders.to_dicts()
        bp = 'here'