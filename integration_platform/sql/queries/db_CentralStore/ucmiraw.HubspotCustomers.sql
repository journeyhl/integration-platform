
if not exists(
    select *
    from sys.schemas s
    where s.name = 'ucmiraw'
)
begin
    exec('create schema ucmiraw');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'HubspotCustomers' and s.name = 'ucmiraw'
)
begin
    create table ucmiraw.HubspotCustomers(
    RecordID varchar(10) not null primary key,
    FirstName varchar(55),
    LastName varchar(55),
    Email varchar(255),
    PhoneNumberFmt varchar(10),
    Contactowner varchar(55),
    LastActivityDate Date,
    LeadStatus varchar(35),
    Marketingcontactstatus varchar(35),
    CreateDate Date,
    HubspotLink varchar(65),
    AcumaticaOrderNumbers varchar(255),
    BillingAddress varchar(155),
    BillingCity varchar(35),
    BillingState varchar(25),
    BillingZip varchar(12),
    LastContacted varchar(55),
    LastModifiedDate Date,
    LeadSource varchar(55),
    ShippingAddress varchar(155),
    ShippingCity varchar(35),
    ShippingState varchar(25),
    ShippingZip varchar(12),
    EcommerceContact varchar(15),
    SourceStore varchar(35),
    DateBecameTheNewLeadStatus Date,
    DateBecameTheOpenLeadLeadStatus Date,
    DateBecameTheOutboundLeadStatus Date,
    DateBecameTheReservedLeadStatus Date,
    DateBecameTheSoldLeadStatus Date,
    DateBecameTheUnqualifiedLeadStatus Date,
    DateBecameTheDncLeadStatus Date,
    DateBecameTheLeadExhaustedLeadStatus Date,
    FirstConversion varchar(155),
    FirstConversionDate Date,
    Sold varchar(4),
    RecentConversionDate Date,
    RecentConversion varchar(155),
    LeadSourceDate Date,
    LinkedinClickId varchar(85),
    IPRegion varchar(15),
    KustomerID varchar(25),
    KustomerLastSync varchar(19),
    KustomerSyncError varchar(42),
    ai_followup_last_selected_at varchar(85),
    KustomerSyncNeeded varchar(5),
    KustomerSyncStatus varchar(5),
    TimeInCurrentStage varchar(11),
    LatestTimeInUnqualifiedLead varchar(85),
    LatestTimeInSubscriber varchar(11),
    LatestTimeInOpportunity varchar(11),
    LatestTimeInLead varchar(11),
    DateExitedUnqualifiedLead Date,
    DateEnteredCurrentStage Date,
    DateEnteredUnqualifiedLead Date,
    DateEnteredSubscriber Date,
    DateEnteredMarketingQualifiedLead Date,
    DateEnteredLead Date,
    CumulativeTimeInUnqualifiedLead varchar(85),
    CumulativeTimeInSubscriber varchar(11),
    CumulativeTimeInOpportunity varchar(11),
    CompanyName varchar(90),
    CompanyCreateDate Date,
    CompanyLastActivityDate Date,
    Country varchar(35),
    Name varchar(155),
    PhoneNumber varchar(25),
    LastChecked datetime,
    InsertedDT datetime
)
end
