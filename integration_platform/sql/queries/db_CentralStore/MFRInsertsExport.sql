select mws.category
, ad_code
, DNIS
, ad_name
, ad_name_2nd
, ad_version_id
, version_name
, version_name_2nd
, product
, start_date
, sum(amt_spent) amt_spent
, sum(circulation) circulation
, sum(calls) calls
, sum(order_count) order_count
, sum(prorata_amt) prorata_amt
, sum(mws.line_amt ) line_amt
, sum(line_amt_prorata) line_amt_prorata
from analytics.mfr_with_spend mws
where mws.start_date >= '2025-07-01'
and mws.order_date >= '2000-01-01'
and order_date <= CAST(GETDATE()-1 AS DATE)
and category = 'Inserts'
group by
 category
, ad_code
, DNIS
, ad_name
, ad_name_2nd
, ad_version_id
, version_name
, version_name_2nd
, product
, start_date
