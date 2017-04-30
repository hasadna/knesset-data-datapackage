from knesset_datapackage.resources.dataservice import BaseKnessetDataServiceCollectionResource
from knesset_data.dataservice.persons import Person, Position, PersonToPosition


class PersonsResource(BaseKnessetDataServiceCollectionResource):
	collection = Person
	object_name = "person"
	track_generated_objects = True
	enable_scraper_errors = True
    
class PositionsResource(BaseKnessetDataServiceCollectionResource):
	collection = Position
	object_name = "position"
	track_generated_objects = True
	enable_scraper_errors = True

class PersonsToPositionsResource(BaseKnessetDataServiceCollectionResource):
	collection = PersonToPosition
	object_name = "person_to_position"
	track_generated_objects = True
	enable_scraper_errors = True