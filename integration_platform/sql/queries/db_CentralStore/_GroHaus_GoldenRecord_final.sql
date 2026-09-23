
with TopLevel as(
select distinct g.GoldenID
	 , coalesce(g.Email, hc.Email, kph_e.Email, kph_p.Email, kph_hs.Email) Email
	 , coalesce(kpp_e.Consent, kpp_p.Consent, kpp_hs.Consent) Consent
	 , coalesce(kps_e.Mkt_Email_Consent, kps_p.Mkt_Email_Consent, kps_hs.Mkt_Email_Consent) Mkt_Email_Consent
	 , coalesce(kpp_e.SMSAttentiveSignup, kpp_p.SMSAttentiveSignup, kpp_hs.SMSAttentiveSignup) SecondaryConsent
	 , coalesce(hc.FirstName, g.FirstName, kph_e.FirstName, kph_p.FirstName, kph_hs.FirstName) FirstName
	 , coalesce(hc.LastName, g.LastName, kph_e.LastName, kph_p.LastName, kph_hs.LastName) LastName
	 , coalesce(hc.PhoneNumberFmt, g.Phone, kph_e.PhoneNumber, kph_p.PhoneNumber, kph_hs.PhoneNumber) PhoneNumber
	 , coalesce(g.City, hc.ShippingCity, hc.BillingCity) City
	 , coalesce(g.State, hc.ShippingState, hc.BillingState) State
	 , (select min(value) from (values(d2c_1st_e.DatePlaced), (d2c_1st_p.DatePlaced))  as t(value)) as FirstPurchaseDate
	 , (select max(value) from (values(d2c_rcnt_e.DatePlaced), (d2c_rcnt_p.DatePlaced)) as t(value)) as LastPurchaseDate
	 , coalesce(d2c_1st_p.ItemClassDesc, d2c_1st_e.ItemClassDesc) FirstPurchaseItem
	 , coalesce(d2c_rcnt_p.ItemClassDesc, d2c_rcnt_e.ItemClassDesc) LastPurchaseItem
	 , case when d2c_rcnt_e.PartProdAccFee != 'No Orders' or d2c_rcnt_p.PartProdAccFee != 'No Orders' then 
	   (select max(value) from(values(d2c_rcnt_e.OrdersAsc), (d2c_rcnt_p.OrdersAsc)) as t(value)) else 0 end Orders
from ucmi.tbl_Customers_Golden g
inner join ucmi.tbl_CustomerLinks_HubSpot h on g.GoldenID = h.GoldenID
inner join ucmiraw.HubspotCustomers hc on h.HsRecordID = hc.RecordID
left join klaviyo.ProfileProperties kpp_hs on replace(hc.HubspotLink, 'https://app.hubspot.com/contacts/5053729/contact/', '') = kpp_hs.HubspotRecordID
left join klaviyo.ProfileHeader kph_hs on kpp_hs.ID = kph_hs.ID
left join klaviyo.ProfileSubscriptions kps_hs on kpp_hs.ID = kps_hs.ID
left join klaviyo.ProfileHeader kph_p on hc.PhoneNumberFmt = kph_p.PhoneNumber
left join klaviyo.ProfileProperties kpp_p on kph_p.ID = kpp_p.ID
left join klaviyo.ProfileSubscriptions kps_p on kpp_p.ID = kps_p.ID
left join klaviyo.ProfileHeader kph_e on hc.Email = kph_e.Email
left join klaviyo.ProfileProperties kpp_e on kph_e.ID = kpp_e.ID
left join klaviyo.ProfileSubscriptions kps_e on kpp_e.ID = kps_e.ID
left join analytics.JHL_D2CCustomerOrderHistory d2c_rcnt_p on g.Phone = d2c_rcnt_p.Phone and d2c_rcnt_p.OrdersDesc_Phone = 1 and d2c_rcnt_p.PartProdAccFee != 'No Orders'
left join analytics.JHL_D2CCustomerOrderHistory d2c_rcnt_e on g.Email = d2c_rcnt_e.Email and d2c_rcnt_e.OrdersDesc_Email = 1 and d2c_rcnt_e.PartProdAccFee != 'No Orders'
left join analytics.JHL_D2CCustomerOrderHistory d2c_1st_p on g.Phone = d2c_1st_p.Phone and d2c_1st_p.OrdersAsc_Phone = 1 and d2c_1st_p.PartProdAccFee != 'No Orders'
left join analytics.JHL_D2CCustomerOrderHistory d2c_1st_e on g.Email = d2c_1st_e.Email and d2c_1st_e.OrdersAsc_Email = 1 and d2c_1st_e.PartProdAccFee != 'No Orders'

)
select t.GoldenID
	 , t.Email
	 , t.Consent
	 , t.Mkt_Email_Consent
	 , t.SecondaryConsent
	 , t.FirstName
	 , t.LastName
	 , t.PhoneNumber
	 , t.City
	 , t.State
	 , case when Orders > 0 then 1 else 0 end HasPurchased
	 , t.FirstPurchaseDate
	 , t.FirstPurchaseItem
	 , t.LastPurchaseDate
	 , t.LastPurchaseItem
	 , null PurchaseChannel
	 , Orders NumberOfPurchases
	 , null CustomerType
from TopLevel t
where Mkt_Email_Consent is not null and Consent is not null and SecondaryConsent is not null

