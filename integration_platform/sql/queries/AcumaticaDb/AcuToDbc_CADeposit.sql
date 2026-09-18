with TopLevel as(
select  c.TranType
      , c.RefNbr
      , c.ExtRefNbr
      , c.CashAccountID
      , cast(c.TranDate as date) TranDate
      , c.DrCr
      , c.TranDesc
      , c.TranPeriodID
      , c.FinPeriodID
      , c.Hold
      , c.Voided
      , c.Status
      , c.Released
      , c.TranAmt
      , c.TranID
      , c.Cleared
      , cast(c.ClearDate as date) ClearDate
      , c.LineCntr
      , c.LineCntrCharge
      , cast(c.ExtraCashTotal as decimal(18,2)) ExtraCashTotal
      , cast(c.ChargeTotal as decimal(18,2)) ChargeTotal
      , cast(c.DetailTotal as decimal(18,2)) DetailTotal
      , cast(c.ControlAmt as decimal(18,2)) ControlAmt
      , c.ChargesSeparate
      , c.ExtraCashAccountID
      , c.CashTranID
      , c.ChargeTranID
      , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_username
      , uc.FullName Created_Name
      , c.CreatedByScreenID Created_ScreenID
      , c.CreatedDateTime Created_Datetime
      , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_username
      , um.FullName LastMod_Name
      , c.LastModifiedByScreenID LastMod_ScreenID
      , c.LastModifiedDateTime LastMod_Datetime
      , c.NoteID
from CADeposit c
left join Users uc on c.CompanyID = uc.CompanyID and c.CreatedByID = uc.PKID
left join Users um on c.CompanyID = um.CompanyID and c.LastModifiedByID = um.PKID
where c.companyid = 2
)
select *
from TopLevel

