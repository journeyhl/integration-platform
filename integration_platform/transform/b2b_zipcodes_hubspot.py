from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.b2b_zipcodes import B2BZipCodes
import logging
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo

class TransformHubspot:
    def __init__(self, pipeline: B2BZipCodes):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.TransformHubspot')
        self.last_checked = datetime.now(ZoneInfo('America/New_York'))
        pass

    def landing(self, data_extract):
        associations = self._associations_(data_extract=data_extract)
        territories = self._territories_(data_extract=data_extract)
        zipcodes = self._zipcodes_(data_extract=data_extract)
        hubspot_transformed = {
            'territories': {
                'qualified_name': 'hs.Territories',
                'data': territories
            },
            'associations': {
                'qualified_name': 'hs.Associations',
                'data': associations
            },
            'zipcodes': {
                'qualified_name': 'hs.Zipcodes',
                'data': zipcodes
            },
        }
        return hubspot_transformed


    def _associations_(self, data_extract: dict) -> list[dict]:
        associations = [
            {
                **a,
                'LastChecked': self.last_checked
            }
        for key, data in data_extract.items()
            for m in data['detailed_rows'] 
                for a in m['associations']
        ]
        return associations

    def _zipcodes_(self, data_extract: dict) -> list[dict]:
        zipcodes = []
        for zip in data_extract['zipcodes']['detailed_rows']:
            props = zip['properties']
            properties = {                
                'ZipCode': props['zip_code'],
                'CompanyAssociations': self.pipeline.default_transformer.string_to_int(props['company_associations']),
                'Territory': props['territory'],
                'Territory1': props['territory1'],
                'TerritoryOwner': self.pipeline.default_transformer.string_to_int(int_str=props['territory_owner']),
                'TerritoryType': props['territory_type'],
                'City': props['city'],
                'State': props['state'],
                'County': props['county'],
                'DataNotes': props['data_notes'],
                'DataSource': props['data_source'],
                'Households65plus100kEst': self.pipeline.default_transformer.string_to_int(int_str=props['households_65plus_100k_est']),
                'Households65plus100kMoe': self.pipeline.default_transformer.string_to_int(int_str=props['households_65plus_100k_moe']),
                'AllAccessibleTeamIDs': props['hs_all_accessible_team_ids'],
                'AllAssignedBusinessUnitIDs': props['hs_all_assigned_business_unit_ids'],
                'AllOwnerIDs': props['hs_all_owner_ids'],
                'AllTeamIDs': props['hs_all_team_ids'],
                'AvatarFilemanagerKey': props['hs_avatar_filemanager_key'],
                'CreatedByUserID': self.pipeline.default_transformer.string_to_int(int_str=props['hs_created_by_user_id']),
                'CreateDate': self.pipeline.default_transformer.parse_date_str(props['hs_createdate'], 0),
                'Lastmodifieddate': self.pipeline.default_transformer.parse_date_str(props['hs_lastmodifieddate'], 0),
                'MergedObjectIDs': props['hs_merged_object_ids'],
                'ObjectID': props['hs_object_id'],
                'ObjectSource': props['hs_object_source'],
                'ObjectSourceDetail1': props['hs_object_source_detail_1'],
                'ObjectSourceDetail2': props['hs_object_source_detail_2'],
                'ObjectSourceDetail3': props['hs_object_source_detail_3'],
                'ObjectSourceID': self.pipeline.default_transformer.string_to_int(int_str=props['hs_object_source_id']),
                'ObjectSourceLabel': props['hs_object_source_label'],
                'ObjectSourceUserID': props['hs_object_source_user_id'],
                'OwningTeams': props['hs_owning_teams'],
                'PinnedEngagementID': props['hs_pinned_engagement_id'],
                'ReadOnly': props['hs_read_only'],
                'SharedTeamIDs': props['hs_shared_team_ids'],
                'SharedUserIDs': props['hs_shared_user_ids'],
                'UniqueCreationKey': props['hs_unique_creation_key'],
                'UpdatedByUserID': self.pipeline.default_transformer.string_to_int(int_str=props['hs_updated_by_user_id']),
                'UserIDsOfAllNotificationFollowers': props['hs_user_ids_of_all_notification_followers'],
                'UserIDsOfAllNotificationRecipients': props['hs_user_ids_of_all_notification_recipients'],
                'UserIDsOfAllNotificationUnfollowers': props['hs_user_ids_of_all_notification_unfollowers'],
                'UserIDsOfAllOwners': props['hs_user_ids_of_all_owners'],
                'WasImported': False if not props['hs_was_imported'] or props['hs_was_imported'].lower() != 'true' else True,
                'HubspotOwnerAssigneddate': props['hubspot_owner_assigneddate'],
                'HubspotOwnerID': props['hubspot_owner_id'],
                'HubspotTeamID': props['hubspot_team_id'],
                'Income100kCountRank': self.pipeline.default_transformer.string_to_int(int_str=props['income_100k_count_rank']),
                'InsideTerritory': props['inside_territory'],
                'LastEnrichedAt': props['last_enriched_at'],
                'OutsideTerritory': props['outside_territory'],
                'Plus65Rank': self.pipeline.default_transformer.string_to_int(int_str=props['plus65_rank']),
                'Population65plusEst': self.pipeline.default_transformer.string_to_int(int_str=props['population_65plus_est']),
                'Population65plusMoe': self.pipeline.default_transformer.string_to_int(int_str=props['population_65plus_moe']),
                'PopulationTotal': self.pipeline.default_transformer.string_to_int(int_str=props['population_total']),
                'LastChecked': self.last_checked
            }
            zipcodes.append(properties)
        return zipcodes


    def _territories_(self, data_extract: dict) -> list[dict]:
        territories = []
        for territory in data_extract['territories']['detailed_rows']:
            props = territory['properties']
            properties = {
                'ObjectID': self.pipeline.default_transformer.string_to_int(int_str=props['hs_object_id']),
                'TerritoryName': props['territory_name'],
                'TerritoryType': props['territory_type'],   
                'OwnerID':self.pipeline.default_transformer.string_to_int(int_str=props['hubspot_owner_id']),
                'TeamID': self.pipeline.default_transformer.string_to_int(int_str=props['hubspot_team_id']),
                'AllAssignedBusinessUnitIDs': props['hs_all_assigned_business_unit_ids'],
                'AllOwnerIDs': props['hs_all_owner_ids'],
                'AllTeamIDs': props['hs_all_team_ids'],
                'AvatarFilemanagerKey': props['hs_avatar_filemanager_key'],
                'CreatedByUserID': self.pipeline.default_transformer.string_to_int(int_str=props['hs_created_by_user_id']),
                'CreateDate': self.pipeline.default_transformer.parse_date_str(props['hs_createdate'], 0),
                'Lastmodifieddate': self.pipeline.default_transformer.parse_date_str(props['hs_lastmodifieddate'], 0),
                'MergedObjectIDs': props['hs_merged_object_ids'],
                'ObjectSource': props['hs_object_source'],
                'ObjectSourceDetail1': props['hs_object_source_detail_1'],
                'ObjectSourceDetail2': props['hs_object_source_detail_2'],
                'ObjectSourceDetail3': props['hs_object_source_detail_3'],
                'ObjectSourceID': props['hs_object_source_id'],
                'ObjectSourceLabel': props['hs_object_source_label'],
                'ObjectSourceUserID': self.pipeline.default_transformer.string_to_int(int_str=props['hs_object_source_user_id']),
                'OwningTeams': props['hs_owning_teams'],
                'PinnedEngagementID': props['hs_pinned_engagement_id'],
                'ReadOnly': props['hs_read_only'],
                'SharedTeamIDs': props['hs_shared_team_ids'],
                'SharedUserIDs': props['hs_shared_user_ids'],
                'UniqueCreationKey': props['hs_unique_creation_key'],
                'UpdatedByUserID': self.pipeline.default_transformer.string_to_int(int_str=props['hs_updated_by_user_id']),
                'UserIDsOfAllNotificationFollowers': props['hs_user_ids_of_all_notification_followers'],
                'UserIDsOfAllNotificationRecipients': props['hs_user_ids_of_all_notification_recipients'],
                'UserIDsOfAllNotificationUnfollowers': props['hs_user_ids_of_all_notification_unfollowers'],
                'UserIDsOfAllOwners': props['hs_user_ids_of_all_owners'],
                'WasImported': False if not props['hs_was_imported'] or props['hs_was_imported'].lower() != 'true' else True,
                'OwnerAssigneddate': self.pipeline.default_transformer.parse_date_str(props['hubspot_owner_assigneddate'], 0),
                'LastChecked': self.last_checked
            }
            territories.append(properties)
        return territories