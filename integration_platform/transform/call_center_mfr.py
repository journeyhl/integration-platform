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
            PhoneRevPreStaging = data_extract['PhoneRevPreStaging'],
            AdPhonePriorityDates = data_extract['AdPhonePriorityDates'],
            AdVersionProduct = data_extract['AdVersionProduct'],
            CallCounts = data_extract['CallCounts'],
            AdDetailVersion = data_extract['AdDetailVersion']
        )
        call_counts = self.aggregate_call_counts()
        phone_revenue_staging = self.__phone_revenue_staging__()
        bp = 'here'
        lineamt_calc = self.__lineamt_calc__()
        bp = 'here'
        phone_revenue = self.__phone_revenue__()
        bp = 'here'
        inter_mfr = self.mfr_inter1_match_and_filter()
        inter_mfr_with_rownum = self.mfr_inter2_pre_aggr()

        inter_mfr_aggregated = self.mfr_inter3_aggregate()

        bp = 'here'


    def __phone_revenue_staging__(self):
        '''`phone_revenue_staging`(self):
        ---
        <hr>
        
        Joins PhoneRevPreStaging and InventorySummary_Product on InventoryCD, then registers DataFrame as PhoneRevStaging in self.:attr:`~sql_context`
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
        '''
        self.logger.info(f'Querying for PhoneRevStaging...')
        self.df_phone_rev_staging = self.sql_context.execute(
            query="""
            select s.*
                , ip.Product
            from PhoneRevPreStaging s
            inner join InventorySummary_Product ip on s.InventoryCD = ip.InventoryCD
            """
        ).collect()
        self.sql_context.register('PhoneRevStaging', self.df_phone_rev_staging)
        self.logger.info(f'PhoneRevStaging registered with {self.df_phone_rev_staging.height} rows.')
        return self.df_phone_rev_staging

    def __lineamt_calc__(self):
        '''`__lineamt_calc__`(self):
        ---
        <hr>
        
        Registers LineAmtCalc in self.:attr:`~sql_context`
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
            
        <hr>
        
        Returns
        ---
        :return `variablename` (_type_): _description_
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
            """
        ).collect()
        self.sql_context.register('LineAmtCalc', self.df_lineamt_calc)
        self.logger.info(f'LineAmtCalc registered with {self.df_lineamt_calc.height} rows.')
        bp = 'here'
        return self.df_lineamt_calc

    def __phone_revenue__(self):
        '''`__phone_revenue__`(self):
        ---
        <hr>
        
        Joins PhoneRevStaging and LineAmtCalc on OrderNbr, then registers DataFrame as PhoneRevenue in self.:attr:`~sql_context`
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
            
        <hr>
        
        Returns
        ---
        :return self.:attr:`~df_phone_revenue` (_pl.DataFrame_): PhoneRevStaging left join LineAmtCalc on OrderNbr
        '''
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
                , s.LineAmt + case when c.LineAmt_calc is null then 0 else c.LineAmt_calc end LineAmtCalculated
                , s.Agent 
                , s.Value
                , s.Product
                , s.Priority
            from PhoneRevStaging s
            left join LineAmtCalc c on s.OrderNbr = c.OrderNbr
            where Priority = 1
            """
        ).collect() 
        
        
        self.sql_context.register('PhoneRevenue', self.df_phone_revenue)
        self.logger.info(f'PhoneRevenue registered with {self.df_phone_revenue.height} rows.')
        bp = 'here'
        return self.df_phone_revenue


    def mfr_inter1_match_and_filter(self):
        bp = 'here'
        self.logger.info(f'Compling Intermediate MFRAllocated query...')
        self.inter_mfr_allocated = self.sql_context.execute(
query="""
select case when c.Date = s.OrderDate and (a.MFRProduct = s.Product or a.Product = s.Product or a.MFRProduct = c.SkillProduct or c.RawSkill in('SA-Internet', 'SA-Fusion')) 
                then 1
            when c.Date = s.OrderDate and a.MFRProduct != s.Product and a.Product != s.Product and a.MFRProduct != c.SkillProduct 
                then 2
            when c.Date != s.OrderDate and (a.MFRProduct = s.Product or a.Product = s.Product or a.MFRProduct = c.SkillProduct) 
                then 3
            when c.Date != s.OrderDate and a.MFRProduct != s.Product and a.Product != s.Product and a.MFRProduct != c.SkillProduct 
                then 4
            else 5 
       end MatchRank
     , (s.OrderDate - c.Date) DaysBetweenCallOrder
     , *
from CallCounts c 
inner join PhoneRevenue s on c.CustomerPhone_ANI = s.Phone 
inner join AdPhonePriorityDates p on c.DNIS = p.TFN
inner join AdDetailVersion a on p.AdCode = a.AdCode
where c.Date <= s.OrderDate 
  and s.OrderDate <= c.Date + interval '14 days'
  and c.Date >= p.StartDate 
  and c.Date <= p.EndDate
  and c.Abandoned != 0
order by OrderDate desc, OrderNbr
""").collect()
        self.sql_context.register('IntermediateMFRAllocated', self.inter_mfr_allocated)
        self.logger.info(f'IntermediateMFRAllocated registered with {self.inter_mfr_allocated.height} rows.')
        return self.inter_mfr_allocated




    def mfr_inter2_pre_aggr(self):
        bp = 'here'
        self.inter_mfr_rownum = self.sql_context.execute(
            query="""
with Inter_MFRAllocated_rownum as(
select row_number() over(partition by a.OrderNbr order by a.MatchRank, a.DaysBetweenCallOrder) RowNum
     , *
from IntermediateMFRAllocated a
)
select case when RowNum = 1
                then a.LineAmtCalculated
            else 0 end LineAmtCalc
     , case when RowNum = 1
                then 1
            else 0 end OrderCount
     , *
from Inter_MFRAllocated_rownum a
"""
        ).collect()
        test = self.inter_mfr_rownum.to_dicts()
        self.sql_context.register(name='IntermediateMFRAllocated_RowNum', frame=self.inter_mfr_rownum)
        return self.inter_mfr_rownum



    def mfr_inter3_aggregate(self):
        bp = 'here'
        self.inter_mfr_aggregated = self.sql_context.execute(
            query="""
select a.AdCode
     , a.PrimaryAdName
     , a.SecondaryAdName
     , a.StartDate
     , a.AdVersionID
     , a.PrimaryVersionName 
     , a.SecondaryVersionName 
     , a.Category
     , a.Product
     , a.DNIS
     , a.Date 
     , a.AcctCD
     , a.Name 
     , a.CustomerPhone_ANI
     , a.OrderDate
     , a.OrderNbr
     , c.Calls
     , a.RowNum
     , a.LineAmtCalc
     , a.OrderCount
     , a.RowNum
from IntermediateMFRAllocated_RowNum a
left join CallCountsAggregated c on a.DNIS = c.DNIS and a.CustomerPhone_ANI = c.CustomerPhone_ANI and a.Date = c.Date
"""
        ).collect()
        test = self.inter_mfr_aggregated.to_dicts()
        self.sql_context.register(name = 'MFRAllocatedAggregated', frame=self.inter_mfr_aggregated)
        return self.inter_mfr_aggregated


    def aggregate_call_counts(self):
        self.call_counts_agg = self.sql_context.execute(
            query="""
with TopLevel as(
select Date
     , CustomerPhone_ANI
     , DNIS
     , count(distinct SessionID) Calls
     , Year
     , Month
     , FinPeriod
from CallCounts
group by Date, CustomerPhone_ANI, DNIS, Year, Month, FinPeriod
)
select *
from TopLevel
"""
        ).collect()
        self.sql_context.register(name='CallCountsAggregated', frame=self.call_counts_agg)
        return self.call_counts_agg


    def _format_tables_(self):
        dfs = {**self.data_extract, 'LineAmtCalc': self.df_lineamt_calc, 'PhoneRevStaging': self.df_phone_rev_staging, 'PhoneRevenue': self.df_phone_revenue}
        printstr = ''
        for key, df in dfs.items():
            printstr += f'----------------------------------\n{key}\n----------------------------------'
            print(f'----------------------------------\n{key}\n----------------------------------')
            for col in df.columns:
                printstr += f'\n{col}'
                print(f'{col}')
            print('\n')
            printstr += '\n'
        # pyperclip.copy(printstr)
        bp = 'here', 
