import logging
import polars as pl
class Transform:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass
    
    def landing(self, data_extract: dict[str, pl.DataFrame]):
        self.data_extract = data_extract
        self.sql_context = pl.SQLContext(
            InventorySummary_Product = data_extract['InventorySummary_Product'],
            PhoneRevPreStaging = data_extract['PhoneRevPreStaging']
        )
        self.phone_revenue_staging()
        bp = 'here'
        self.lineamt_calc()
        bp = 'here'

        self.phone_revenue()
        bp = 'here'



    def phone_revenue_staging(self):
        self.df_phone_rev_staging = self.sql_context.execute(
query="""
select s.*
     , ip.Product
from PhoneRevPreStaging s
inner join InventorySummary_Product ip on s.InventoryCD = ip.InventoryCD
""").collect()
        self.sql_context.register('PhoneRevStaging', self.df_phone_rev_staging)


    def lineamt_calc(self):
        '''`lineamt_calc`(self):
        ---
        <hr>
        
        Registers LineAmtCalc to SQLContext
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
        '''
        self.logger.info(f'Querying for LineAmt_Calc...')
        self.df_lineamt_calc = self.sql_context.execute(
query="""
with TopLevel as(
select OrderNbr, sum(LineAmt) LineAmt_calc
from PhoneRevStaging
where Priority != 1
group by OrderNbr
)
select *
from TopLevel
""").collect()
        self.sql_context.register('LineAmtCalc', self.df_lineamt_calc)
        self.logger.info(f'LineAmtCalc registered with {self.df_lineamt_calc.height} rows.')
        bp = 'here'


        
    def phone_revenue(self):
        self.logger.info(f'Querying for PhoneRevenue...')
        self.df_phone_revenue = self.sql_context.execute(
query="""
select s.AcctCD 
     , s.Name 
     , s.Phone 
     , s.OrderNbr 
     , s.LineNbr 
     , s.OrderDate 
     , s.OrderStatus 
     , s.InventoryCD 
     , s.Descr 
	 , s.LineAmt
	 , s.LineAmt + c.LineAmt_calc Test
     , s.Agent 
	 , s.Value
	 , s.Product
	 , s.Priority
from PhoneRevStaging s
left join LineAmtCalc c on s.OrderNbr = c.OrderNbr
where Priority = 1
""").collect()
        self.sql_context.register('PhoneRevenue', self.df_phone_revenue)
        self.logger.info(f'PhoneRevenue registered with {self.df_phone_revenue.height} rows.')
        bp = 'here'
