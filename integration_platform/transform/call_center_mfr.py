import logging
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo
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
            CallCounts = data_extract['CallCounts'],
            AdDetailVersion = data_extract['AdDetailVersion']
        )

        adphone_full = self.ad_table_joins()
        aggregate_call_counts = self._aggregate_call_counts_()
        phone_revenue_staging = self._phone_revenue_staging_()
        lineamt_calc = self._lineamt_calc_()
        phone_revenue = self._phone_revenue_()
        inter_mfr_matched = self.mfr_inter1_match_and_filter()
        inter_mfr_rownum = self.mfr_inter2_pre_aggr()
        inter_mfr_allocated = self.mfr_inter3_aggregate()

        acu_mfr_allocated = self.allocate_mfr_match_acu_view()
        mfr_allocated = self.allocate_mfr()



        calls_by_skill_month        = self.calls_by_metric(metric_name=['RawSkill', 'SkillProduct'], timeframe='Month')
        calls_by_agent_month        = self.calls_by_metric(metric_name=["coalesce(Agent, '-') as Agent"], timeframe='Month')
        calls_by_skill_agent_month  = self.calls_by_metric(metric_name=['RawSkill', 'SkillProduct', "coalesce(Agent, '-') as Agent"], timeframe='Month')
        calls_by_dept_month         = self.calls_by_metric(metric_name=["coalesce(Department, '-') as Department"], timeframe='Month')
        calls_by_skill_dept_month   = self.calls_by_metric(metric_name=['RawSkill', 'SkillProduct', "coalesce(Department, '-') as Department"], timeframe='Month')
        calls_by_business_hr_month  = self.calls_by_metric(metric_name=['DuringBusinessHours'], timeframe='Month')
        agents_by_month             = self.agents_by(metric_name=['Month'])

        calls_by_skill_day          = self.calls_by_metric(metric_name=['RawSkill', 'SkillProduct'], timeframe='Date')
        calls_by_agent_day          = self.calls_by_metric(metric_name=["coalesce(Agent, '-') as Agent"], timeframe='Date')
        calls_by_skill_agent_day    = self.calls_by_metric(metric_name=['RawSkill', 'SkillProduct', "coalesce(Agent, '-') as Agent"], timeframe='Date')
        calls_by_dept_day           = self.calls_by_metric(metric_name=["coalesce(Department, '-') as Department"], timeframe='Date')
        calls_by_skill_dept_day     = self.calls_by_metric(metric_name=['RawSkill', 'SkillProduct', "coalesce(Department, '-') as Department"], timeframe='Date')
        calls_by_business_hr_day    = self.calls_by_metric(metric_name=['DuringBusinessHours'], timeframe='Date')
        agents_by_day               = self.agents_by(metric_name=['Date', 'DuringBusinessHours'])

        # Department

        bp = 'here'
        dataframes = {
            **data_extract,
            'adphone_full': adphone_full,
            'aggregate_call_counts': aggregate_call_counts,
            'phone_revenue_staging': phone_revenue_staging,
            'lineamt_calc': lineamt_calc,
            'phone_revenue': phone_revenue,
            'inter_mfr_matched': inter_mfr_matched,
            'inter_mfr_rownum': inter_mfr_rownum,
            'inter_mfr_allocated': inter_mfr_allocated,
            'acu_mfr_allocated': acu_mfr_allocated,
            'mfr_allocated': mfr_allocated,
            'calls_by_skill_month': calls_by_skill_month,
            'calls_by_skill_day': calls_by_skill_day,
            'calls_by_agent_month': calls_by_agent_month,
            'calls_by_agent_day': calls_by_agent_day,
            'calls_by_skill_agent_month': calls_by_skill_agent_month,
            'calls_by_skill_agent_day': calls_by_skill_agent_day,
            'calls_by_dept_month': calls_by_dept_month,
            'calls_by_dept_day': calls_by_dept_day,
            'calls_by_skill_dept_month': calls_by_skill_dept_month,
            'calls_by_skill_dept_day': calls_by_skill_dept_day,
            'calls_by_business_hr_month': calls_by_business_hr_month,
            'calls_by_business_hr_day': calls_by_business_hr_day,
            'agents_by_month': agents_by_month,
            'agents_by_day': agents_by_day
        }
        dicts = {
            key: dataframe.to_dicts() for key, dataframe in dataframes.items()
        }

        data_transformed = {
            'dataframes': dataframes,
            'dicts': dicts            
        }
        return data_transformed

    #region Aggregation by_
    def calls_by_metric(self, metric_name: list, timeframe: str = 'Date'):
        ''':meth:`~calls_by_metric` (self, metric_name: *str = 'RawSkill'*, timeframe: *str = 'Date'*):
        ---
        <hr>
        
        Given the field name of a metric and a timeframe (Date/Month), return an aggregated count of calls by **metric_name**, grouped by the timeframe specified
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `metric_name`: The name of the metric to aggregate calls for in the given timeframe
        :param (*str*) `timeframe`: ***Date*** or ***Month***. The timeframe in which we will aggregate calls for
        
        <hr>
        
        Returns
        ---
        :return `calls_by_` (_pl.DataFrame_):  polars DataFrame of aggregated calls by the passed metric, grouped by timeframe
        '''
        if timeframe == 'Month':
            timeframe = 'Month, Year, FinPeriod'
        else:
            timeframe = f'{timeframe}, Month, Year, FinPeriod'
        grouped_metric_name = [metric.split(' as ')[0] if ' as ' in metric else metric for metric in metric_name]
        metric_str = ', '.join(metric_name)
        grouped_metric_str  = ', '.join(grouped_metric_name)
        calls_by_ = self.sql_context.execute(
            query=f"""
        with TopLevel as(
        select {metric_str}
            , count(distinct SessionID) Calls
            , {timeframe}
        from CallCounts
        group by {timeframe}, {grouped_metric_str}
        )
        select *
        from TopLevel
        """).collect().with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        self.logger.info(f'{len(calls_by_)} rows returned by Calls by {metric_name} & {timeframe} query')
        return calls_by_
    
    def agents_by(self, metric_name: list):
        if 'Month' in metric_name:
            metric_name = ['Year', 'FinPeriod'] + metric_name
        elif 'Date' in metric_name:
            metric_name = ['Year', 'FinPeriod', 'Month'] + metric_name
        metrics_group_by = ', '.join(metric_name)
        agents_by_ = self.sql_context.execute(
            query=f"""
        with TopLevel as(
        select {metrics_group_by}
             , count(distinct coalesce(Agent, '-')) Agents
        from CallCounts
        group by {metrics_group_by}
        )
        select *
        from TopLevel
        """).collect().with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        self.logger.info(f'{len(agents_by_)} rows returned by Agents by {metrics_group_by} query')
        return agents_by_
    #endregion


    def ad_table_joins(self):
        bp = 'here'
        self.adphone_full = self.sql_context.execute(
            query="""
        select p.*
             , v.Category
             , v.PrimaryAdName
             , v.SecondaryAdName
             , v.Product
             , v.AdVersionID
             , v.PrimaryVersionName
             , v.SecondaryVersionName
        from AdPhonePriorityDates p
        left join AdDetailVersion v on p.AdCode = v.AdCode and p.StartDate = v.StartDate
"""
        ).collect().with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        self.sql_context.register(name='adphone_full', frame=self.adphone_full)
        self.logger.info(f'adphone_full registered with {self.adphone_full.height} rows.')
        return self.adphone_full


    #region aggregate call counts
    def _aggregate_call_counts_(self) -> pl.DataFrame:
        '''`_aggregate_call_counts_`(self):
        ---
        <hr>
        
        Counts distinct SessionIDs from CallCounts query and groups by Date, ANI, and DNIS
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
        
        <hr>
        
        Returns
        ---
        :return self.:attr:`~call_counts_agg` (_pl.DataFrame_): Count of distinct SessionIDs or Calls
        '''        
        self.call_counts_agg = self.sql_context.execute(
            query="""
        with TopLevel as(
        select Date
            , CustomerPhone_ANI
            , DNIS
            , count(distinct SessionID) Calls
            
        from CallCounts
        group by Date, CustomerPhone_ANI, DNIS
        )
        select *
        from TopLevel
        """).collect()
        self.sql_context.register(name='CallCountsAggregated', frame=self.call_counts_agg)
        return self.call_counts_agg
    #endregion

    #region Phone Revenue staging
    def _phone_revenue_staging_(self) -> pl.DataFrame:
        '''`_phone_revenue_staging_`(self):
        ---
        <hr>
        
        - Joins PhoneRevPreStaging and InventorySummary_Product on InventoryCD, then registers DataFrame as PhoneRevStaging in self.:attr:`~sql_context`
        - Covers the inventory portion of the PhoneRevStaging CTE in the ***acu.MFRAllocated*** view definition

        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
            
        <hr>
        
        Returns
        ---
        :return self.:attr:`~df_phone_rev_staging` (_pl.DataFrame_): PhoneRevPreStaging joined with InventorySummary_Product
        '''
        self.logger.info(f'Querying for PhoneRevStaging...')
        self.df_phone_rev_staging = self.sql_context.execute(
            query="""
        select s.*
            , ip.Product
        from PhoneRevPreStaging s
        inner join InventorySummary_Product ip on s.InventoryCD = ip.InventoryCD
        """).collect()
        self.sql_context.register('PhoneRevStaging', self.df_phone_rev_staging)
        self.logger.info(f'PhoneRevStaging registered with {self.df_phone_rev_staging.height} rows.')
        return self.df_phone_rev_staging
    #endregion

    #region LineAmount calculations
    def _lineamt_calc_(self) -> pl.DataFrame:
        '''`_lineamt_calc_`(self):
        ---
        <hr>
        
        - Registers LineAmtCalc in self.:attr:`~sql_context`
        - Instead of doing LineAmtCalc in the PhoneRevenue CTE in the ***acu.MFRAllocated*** view definition, do the calculation as such, then join in :meth:`~_phone_revenue_`
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
            
        <hr>
        
        Returns
        ---
        :return self.:attr:`~df_lineamt_calc` (_pl.DataFrame_): Summarized LineAmt from all rows with a Priority value != 1, grouped by OrderNbr
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
        return self.df_lineamt_calc
    #endregion

    #region Phone Revenue
    def _phone_revenue_(self) -> pl.DataFrame:
        ''':meth:`~_phone_revenue_` (self):
        ---
        <hr>
        
        - Joins PhoneRevStaging and LineAmtCalc on OrderNbr, then registers DataFrame as PhoneRevenue in self.:attr:`~sql_context`
        - Looking at the view definition of ***acu.MFRAllocated***, this is a combination of the 3rd and 4th CTEs, PhoneRevStaging and PhoneRevenue.

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
        """).collect()
        self.sql_context.register('PhoneRevenue', self.df_phone_revenue)
        self.logger.info(f'PhoneRevenue registered with {self.df_phone_revenue.height} rows.')
        return self.df_phone_revenue
    #endregion

    #region MFR inter step1, Match & Filter
    def mfr_inter1_match_and_filter(self) -> pl.DataFrame:
        '''`mfr_inter1_match_and_filter`(self):
        ---
        <hr>

        - Looking at the ***acu.MFRAllocated*** view def, all mfr_inter methods will refer to final query which defines the view by querying all of the prior CTEs
        - ### Does MatchRank case statement and gets the datediff of the Call Date and the Order Date
        - #### Does main filtering:
            - CallDate is before or on OrderDate
            - OrderDate is within 14 days of the CallDate
            - CallDate is after the advertisement's StartDate
            - CallDate is before the advertisement's EndDate
            - The call was not abandoned
        - This method's main goal is to do the bulky case statement portion to make downstream queries more readable

        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`            
        
        <hr>
        
        Returns
        ---
        :return self.:attr:`~inter_mfr_matched` (_pl.DataFrame_): Intermediate version of MFRAllocated, with the case statement for MatchRank and the DaysBetweenCallOrder values added
        '''        
        bp = 'here'
        self.logger.info(f'Compling first intermediate MFRAllocated query...Determining MatchRank and DaysBetweenCallOrder values and filtering based upon dates')
        self.inter_mfr_matched = self.sql_context.execute(
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
            , (cast(cast(s.OrderDate as date) as bigint) - cast(cast(c.Date as date) as bigint)) DaysBetweenCallOrder
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
        self.sql_context.register('IntermediateMFRAllocated_Match', self.inter_mfr_matched)
        self.logger.info(f'IntermediateMFRAllocated_Match registered with {self.inter_mfr_matched.height} rows.')
        test = self.inter_mfr_matched.to_dicts()
        return self.inter_mfr_matched
    #endregion

    #region MFR inter step2, Case statements
    def mfr_inter2_pre_aggr(self) -> pl.DataFrame:
        '''`mfr_inter2_pre_aggr`(self, ):
        ---
        <hr>
        
        - Looking at the ***acu.MFRAllocated*** view def, all mfr_inter methods will refer to final query which defines the view by querying all of the prior CTEs
        - ### Added Fields:
            - RowNum
                - How good of a match the call to order is 
                    - See case statement in :meth:`~mfr_inter1_match_and_filter`
            - LineAmtCalc
                - Summarized LineAmt value from multiline orders.
                    - For example, Customer calls in for Air Elite ad. They order an Air elite ($2895) and and upwalker ($745). We match the Air Elite call to the Air Elite order, and  LineAmtCalc would be 2895 + 745 = 3640
                    - Same goes for multiple items. Customer calls PSC phone number, buys $3299 PSC, $295 replacement box, and a $55 controller. LineAmtCalc = $3649
            - OrderCount
                - If the order counts or not
                    - Say we have multiple matches, resulting in rows with RowNum values of 1 and 2. OrderCount will take the best match, aka 1.
                    - RowNum values of 2 and 4, OrderCount = 1 for RowNum = 2
                    
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
         
        <hr>
        
        Returns
        ---
        :return self.:attr:`~inter_mfr_rownum` (_pl.DataFrame_): Intermediate version of MFRAllocated, with the case statement for MatchRank and the DaysBetweenCallOrder values added
        '''        
        self.logger.info(f'Compling second intermediate MFRAllocated query...Determining RowNum, LineAmtCalc, and OrderCount values')
        self.inter_mfr_rownum = self.sql_context.execute(
            query="""
        with Inter_MFRAllocated_rownum as(
        select row_number() over(partition by a.OrderNbr order by a.MatchRank, a.DaysBetweenCallOrder) RowNum
            , *
        from IntermediateMFRAllocated_Match a
        )
        select case when RowNum = 1
                        then a.LineAmtCalculated
                    else 0 end LineAmtCalc
            , case when RowNum = 1
                        then 1
                    else 0 end OrderCount
            , *
        from Inter_MFRAllocated_rownum a
        """).collect()
        self.sql_context.register(name='IntermediateMFRAllocated_RowNum', frame=self.inter_mfr_rownum)
        self.logger.info(f'IntermediateMFRAllocated_RowNum registered with {self.inter_mfr_rownum.height} rows.')
        return self.inter_mfr_rownum
    #endregion

    #region MFR inter step3, Aggregation
    def mfr_inter3_aggregate(self) -> pl.DataFrame:
        '''`mfr_inter3_aggregate`(self):
        ---
        <hr>
        
        - Looking at the ***acu.MFRAllocated*** view def, all mfr_inter methods will refer to final query which defines the view by querying all of the prior CTEs
        - Performs an inner join to the CallCountsAggregated DataFrame to get the summarized call values
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
        
        Returns
        ---
        :return self.:attr:`~inter_mfr_allocated` (_pl.DataFrame_): Intermediate version of MFRAllocated, joined with CallCountsAggregated
        '''        
        self.logger.info(f'Compling third and final intermediate MFRAllocated query...Joining CallCountsAggregated')
        self.inter_mfr_allocated = self.sql_context.execute(
            query="""
        select c.Calls
             , a.*
        from IntermediateMFRAllocated_RowNum a
        inner join CallCountsAggregated c on a.DNIS = c.DNIS and a.CustomerPhone_ANI = c.CustomerPhone_ANI and a.Date = c.Date
        order by a.Date desc, a.OrderNbr, a.OrderCount desc, a.RowNum
        """).collect()
        self.sql_context.register(name = 'IntermediateMFRAllocated', frame=self.inter_mfr_allocated)
        self.logger.info(f'IntermediateMFRAllocated registered with {self.inter_mfr_allocated.height} rows.')
        return self.inter_mfr_allocated
    #endregion


    #region Matching acu.MFRAllocated
    def allocate_mfr_match_acu_view(self) -> pl.DataFrame:
        '''`allocate_mfr_match_acu_view`(self):
        ---
        <hr>
        
        - Looking at the ***acu.MFRAllocated*** view def, all mfr_inter methods will refer to final query which defines the view by querying all of the prior CTEs
        - Matches the view definition of ***acu.MFRAllocated*** exactly
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
        
        Returns
        ---
        :return self.:attr:`~acu_mfr_allocated_view` (_pl.DataFrame_): acu.MFRAllocated as a DataFrame
        '''        
        self.logger.info(f'Compiling acuMFRAllocated DataFrame...Matching the view definition of acu.MFRAllocated')
        self.acu_mfr_allocated_view = self.sql_context.execute(
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
            , a.LineAmtCalc
            , a.OrderCount
            , a.RowNum
        from IntermediateMFRAllocated_RowNum a
        inner join CallCountsAggregated c on a.DNIS = c.DNIS and a.CustomerPhone_ANI = c.CustomerPhone_ANI and a.Date = c.Date
        order by a.Date desc, a.OrderNbr, a.OrderCount desc, a.RowNum
        """).collect().with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        self.sql_context.register(name = 'acuMFRAllocated', frame=self.acu_mfr_allocated_view)
        self.logger.info(f'acuMFRAllocated registered with {self.acu_mfr_allocated_view.height} rows.')
        return self.acu_mfr_allocated_view
    #endregion

    def allocate_mfr(self) -> pl.DataFrame:
        self.mfr_allocated = self.sql_context.execute(
            query="""
        select a.*
            , c.Calls
        from IntermediateMFRAllocated_RowNum a
        inner join CallCountsAggregated c on a.DNIS = c.DNIS and a.CustomerPhone_ANI = c.CustomerPhone_ANI and a.Date = c.Date
        order by a.Date desc, a.OrderNbr, a.OrderCount desc, a.RowNum
        """).collect().with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked')).drop(['Agent:s', 'Priority:p', 'AdCode:a', 'Product:a', 'StartDate:a'])
        self.sql_context.register(name = 'MFRAllocated', frame=self.mfr_allocated)
        self.logger.info(f'MFRAllocated registered with {self.mfr_allocated.height} rows.')
        return self.mfr_allocated



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





#region not in use

    #region Allocate MFR
    def allocate_mfr_ordercount_eq1(self) -> pl.DataFrame:
        '''`allocate_mfr`(self):
        ---
        <hr>
        
        - Looking at the ***acu.MFRAllocated*** view def, all mfr_inter methods will refer to final query which defines the view by querying all of the prior CTEs
        - Filters out all non counted orders and keeps all extra columns
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~landing`
        
        Returns
        ---
        :return self.:attr:`~mfr_allocated` (_pl.DataFrame_): Intermediate version of MFRAllocated, joined with CallCountsAggregated
        '''        
        self.logger.info(f'Compiling final MFRAllocated DataFrame...Filtering to rows with OrderCount value of 1')
        self.mfr_allocated = self.sql_context.execute(
            query="""
        select *
        from IntermediateMFRAllocated a
        where a.OrderCount = 1
        """).collect()
        self.sql_context.register(name='MFRAllocated', frame=self.mfr_allocated)
        self.logger.info(f'MFRAllocated registered with {self.mfr_allocated.height} rows.')
        return self.mfr_allocated
    #endregion

#endregion