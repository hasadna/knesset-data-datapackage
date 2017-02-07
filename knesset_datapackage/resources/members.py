from knesset_datapackage.resources.dataservice import BaseKnessetDataServiceCollectionResource
from knesset_data.dataservice.members import Member


class MembersResource(BaseKnessetDataServiceCollectionResource):
    collection = Member
    object_name = "member"
    track_generated_objects = True
