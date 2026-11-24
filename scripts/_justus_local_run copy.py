import logging, os, tempfile
from integration_platform.connectors.hubspot_api import HubSpotAPI
from integration_platform.connectors.sql import SQLConnector, CentralStoreQueries
from integration_platform.transform.default_transformer import DefaultTransformer
from datetime import datetime, timedelta
from pathlib import Path
import polars as pl
hub = HubSpotAPI('debug')
dbc = SQLConnector(pipeline='debug', database_name='db_CentralStore')
acu_db = SQLConnector(pipeline='debug', database_name='AcumaticaDb')
def_transformer = DefaultTransformer('debug')

#MARK: _condense_hubspot_response_
#I made this for klaviyo writeback, but would be useful here i think. Im just putting here for example, you can place wherever
def _condense_hubspot_response_(hubspot_profile: dict):
    ''':class:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform`.:meth:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform._condense_hubspot_response_`
    ---
    
    Trims hubspot's api response to only what we'll need for this process
    
    Parameters
    ---
    :param (*_type_*) `hubspot_profile`: response from hubspot api. {} if no profile is found

    Returns
    ---
    :return `hubspot_profile` (dict): condensed dictionary containing all relevant data points for hubspot contacts
    
    <hr>
    
    ## Upstream Calls (Methods/Functions Called by)
    
        ### :class:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform`.:meth:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform._get_hubspot_profile_`
    
        - Called after getting response from hubspot api
    '''        
    if hubspot_profile == {}:
        return {}
    hubspot_profile = {
        'id': hubspot_profile['id'],
        'createdAt': hubspot_profile['createdAt'],
        'updatedAt': hubspot_profile['updatedAt'],
        'url': hubspot_profile['url'],
        **hubspot_profile['properties'],   
    }
    return hubspot_profile

#also just adding here for time sake, you can put wherever
def _set_epoch(time_period: datetime):
    # Sets the time filter for queries, depending on the day
    epoch_ms = int(time_period.timestamp() * 1000)
    return epoch_ms

def main():
    PROPERTIES_TO_PULL = ['firstname','lastname','email','phone','customer_id']
    hubspot_contacts = hub.search_contacts(filter_groups=[{"filters": [{"propertyName": "lastmodifieddate", "operator": "GTE", "value": _set_epoch(datetime.now() - timedelta(hours=36))}]}], properties=PROPERTIES_TO_PULL)
    hubspot_contacts = [_condense_hubspot_response_(contact) for contact in hubspot_contacts]
    bp = 'here'
    dbc_customers = dbc.query_db(query="""
    select *
    from acu.Customers 
    """) #can join on phone or email here


    acu_customers = acu_db.query_db(query="""
    select rtrim(b.AcctCD) AcctCD
         , b.AcctName
         , cu.CustomerClassID
         , coalesce(c.Phone1, c.Phone2) Phone
         , c.EMail
         , replace(cs.Value, 'https://app.hubspot.com/contacts/5053729/contact/', '') RecordID
         , cs.Value URL
    from BAccount b
    left join CSAnswers cs on b.CompanyID = cs.CompanyID and b.NoteID = cs.RefNoteID and AttributeID = 'HUBSPOTID'
    inner join Contact c on b.CompanyID = c.CompanyID and b.DefContactID = c.ContactID
    inner join Customer cu on b.CompanyID = cu.CompanyID and b.BAccountID = cu.BAccountID
    where c.CompanyID = 2
    and b.DeletedDatabaseRecord = 0 
    and b.Type = 'CU'
    """) #can join on phone, email or RecordID here. 


    #note: use default_transformer.parse_phone to do format the hubspot_customers phone number to match what's in db
    bp = 'here'
    hubspot_contacts = [
        {
            **contact,
            'phone': def_transformer.parse_phone(phone_str=contact.get('phone')),
            'email': def_transformer.clean_string(string=contact.get('email'))
        } for contact in hubspot_contacts
    ]

    #you can turn the hubspot list into a polars dataframe and do the join that way, or as your file had it with the maps.
    df_hubspot = pl.DataFrame(data=hubspot_contacts, infer_schema_length=None)
    bp = 'here'

    #then you can join however
    #use inner if you only want matches. Left returns everything from the left dataframe (df_hubspot)
    acu_id_joined = df_hubspot.join(acu_customers, left_on='id', right_on='RecordID', how='left') 
    dbc_phone_joined = df_hubspot.join(dbc_customers, left_on='phone', right_on='Phone', how='left')
    dbc_email_joined = df_hubspot.join(dbc_customers, left_on='email', right_on='Email', how='left')
    bp = 'here'

    #or iterate with the map
    hubspot_map = {
        contact['id']:{
            'phone': contact['phone'],
            'email': contact['email']
        }
        for contact in hubspot_contacts
    }
    #im lazy and didnt write out the maps for the acu and dbc datasets, but same premise as you had it in your file where email/phone is the key and CustomerID is the value
    bp = 'here'

main()