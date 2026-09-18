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

)
select *
from TopLevel
where Mkt_Email_Consent is not null and Consent is not null and SecondaryConsent is not null
