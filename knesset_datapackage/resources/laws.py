from knesset_datapackage.resources.dataservice import BaseKnessetDataServiceCollectionResource
from knesset_data.dataservice.laws import PrivateLaw


class PrivateLawResource(BaseKnessetDataServiceCollectionResource):
    collection = PrivateLaw
    object_name = "private law"
    get_latest_by_page_estimate = ('id', 5)  # order by id desc, with estimate of 5 laws per day up to given days param value
