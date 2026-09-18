
if not exists(
    select *
    from sys.schemas s
    where s.name = 'klaviyo'
)
begin
    exec('create schema klaviyo');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'ProfileSubscriptions' and s.name = 'klaviyo'
)
begin
create table klaviyo.ProfileSubscriptions(
ID varchar(26) not null primary key,
Mkt_Email_CanReceiveEmail bit,
Mkt_Email_Consent varchar(35),
Mkt_Email_ConsentTimestamp datetime,
Mkt_Email_LastUpdated datetime,
Mkt_Email_Method varchar(25),
Mkt_Email_MethodDetail varchar(255),
Mkt_Email_CustomMethodDetail varchar(155),
Mkt_Email_DoubleOptin bit,
OpenTrk_Email_Consent varchar(35),
OpenTrk_Email_ConsentTimestamp datetime,
OpenTrk_Email_LastUpdated datetime,
OpenTrk_Email_CreatedTimestamp datetime,
OpenTrk_Email_Metadata varchar(55),
OpenTrk_Email_CanReceive bit,
OpenTrk_Email_ValidUntil datetime,
ClickTrk_Email_Consent varchar(16),
ClickTrk_Email_ConsentTimestamp datetime,
ClickTrk_Email_LastUpdated datetime,
ClickTrk_Email_CreatedTimestamp datetime,
ClickTrk_Email_Metadata varchar(55),
ClickTrk_Email_CanReceive bit,
ClickTrk_Email_ValidUntil datetime,
Mkt_SMS_CanReceiveSMS bit,
Mkt_SMS_Consent varchar(35),
Mkt_SMS_ConsentTimestamp datetime,
Mkt_SMS_Method varchar(25),
Mkt_SMS_MethodDetail varchar(355),
Mkt_SMS_LastUpdated datetime,
Txn_SMS_CanReceiveSMS bit,
Txn_SMS_Consent varchar(35),
Txn_SMS_ConsentTimestamp datetime,
Txn_SMS_Method varchar(25),
Txn_SMS_MethodDetail varchar(55),
Txn_SMS_LastUpdated datetime,
Mkt_Push_CanReceivePush bit,
Mkt_Push_Consent varchar(35),
Mkt_Push_ConsentTimestamp datetime,
InsertedDT datetime,
LastChecked datetime,
)
end
