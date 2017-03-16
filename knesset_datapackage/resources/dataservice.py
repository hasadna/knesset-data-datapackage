from knesset_datapackage.base import CsvResource
from knesset_data.dataservice.exceptions import KnessetDataServiceObjectException


class BaseKnessetDataServiceCollectionResource(CsvResource):

    # the related knesset_data.dataservice collection class
    collection = None

    # used for logging
    object_name = "object"

    # if True - keeps a list of all objects generated / appended
    # the objects are available using get_generated_objects method
    track_generated_objects = False

    # getter feature allows to get different types of data of options by fetch kwargs
    # by default all objects are fetched, you can add more types, see Committees resource for details
    collection_getter_kwargs = {
        # kwarg: getter type
        # OBJECT will be replaced with object_name
        "OBJECT_ids": "ids"
    }
    default_getter_type = "all"

    # True - enables running logic before appending the object
    # if enabled you should implement the _pre_append method
    # also, by default - it enables the scraper_errors feature, see below
    enable_pre_append = False

    # True - adds a "scraper_errors" column containing a list of errors caught for the object
    # False - exceptions are raised
    # None - if enable_pre_append is True, scraper_errors is True, otherwise it's False
    enable_scraper_errors = None

    def __init__(self, name, parent_datapackage_path):
        """
        initilizes the resource with the relevant json table schema for this collection
        """
        super(BaseKnessetDataServiceCollectionResource, self).__init__(name, parent_datapackage_path, self._get_json_table_schema())
        if self.track_generated_objects:
            self._generated_objects = []

    def _get_json_table_schema(self):
        """
        returns the json table schema for this collection (from thee knesset_data.dataservice collection class)
        """
        schema = self.collection.get_json_table_schema()
        if self.enable_pre_append:
            schema["fields"].append({"type": "string", "name": "scraper_errors"})
        return schema

    def _collection_get(self, object_id, proxies):
        """
        get a single object from the collection
        will raise an exception on any problem
        """
        return self.collection.get(object_id, proxies=proxies)

    def _collection_get_all(self, proxies, skip_exceptions):
        """
        get all the objects from the collection
        if skip_exception is enabled - will yield KnessetDataserviceObjectException object for each failed object
        otherwise - stops generating and raises an exception
        pay attention that some error might still raise exception even if skip_exceptions is True, for example - http request errors
        """
        return self.collection.get_all(proxies=proxies, skip_exceptions=skip_exceptions)

    def _get_objects_by_ids(self, getter_kwarg_value, proxies=None, skip_exceptions=False, **make_kwargs):
        """
        get specific object ids
        if skip_exception is enabled - will yield KnessetDataserviceObjectException object for each failed object
        otherwise - stops generating and raises an exception
        if skip_exceptions is enabled - no errors will be raised even if http errors (because we are fetching one object at a time)
        """
        # currently done inefficiently by getting one object each time
        # TODO: make it fetch objects in bulk
        ids = getter_kwarg_value
        self.logger.info('fetching {} ids: {}'.format(self.object_name, ids))
        self.descriptor["description"] = "specific {} ids".format(self.object_name)
        for object_id in ids:
            try:
                object = self._collection_get(object_id, proxies=proxies)
            except Exception, e:
                if not skip_exceptions:
                    raise e
                else:
                    object = KnessetDataServiceObjectException(self.collection, None, e)
            yield object


    def _get_objects_by_all(self, getter_kwarg_value, proxies=None, skip_exceptions=False, **make_kwargs):
        """
        get all objects from the collection, usually it means getting them ordered by id ascending
        see _collection_get_all method for details about exceptions and return values
        """
        self.logger.info('fetching all {}s'.format(self.object_name))
        self.descriptor["description"] = "all {}s".format(self.object_name)
        for object in self._collection_get_all(proxies=proxies, skip_exceptions=skip_exceptions):
            yield object

    def _get_objects(self, proxies=None, **make_kwargs):
        """
        calls the relevant getter function (_get_objects_by_?)
        see the _get_objects_by_? functions for details about exceptions and return values
        """
        for kwarg, gtype in self.collection_getter_kwargs.iteritems():
            kwarg = kwarg.replace('OBJECT', self.object_name)
            kwarg_value = make_kwargs.get(kwarg)
            if kwarg_value:
                return getattr(self, "_get_objects_by_{}".format(gtype))(kwarg_value, proxies=proxies, **make_kwargs)
        return getattr(self, "_get_objects_by_{}".format(self.default_getter_type))(None, proxies=proxies, **make_kwargs)

    def _pre_append(self, object, **make_kwargs):
        """
        used if enabled_pre_append is True
        allows for extending classes to perform additional work / update related resources
        """
        pass

    def _data_generator(self, **make_kwargs):
        """
        main method called by CsvResource to get the data
        yields a dict that corresponds to each csv row according to the json table schema
        """
        # _get_objects will try to consider skip_exceptions option and yield exception objects (usually KnessetDataserviceObjectException)
        # but - there are cases where exceptions will still be raised,
        # for example, if getting an error when fetching page of results we usually raise an exception and don't continue
        for object in self._get_objects(**make_kwargs):
            enable_scraper_errors = self.enable_scraper_errors or (self.enable_scraper_errors is None and self.enable_pre_append)
            scraper_errors = [] if enable_scraper_errors else None
            if make_kwargs.get("skip_exceptions") and isinstance(object, Exception):
                exception, object = object, None
            else:
                exception = None
            if exception:
                if enable_scraper_errors:
                    scraper_errors.append("exception generating {}: {}".format(self.descriptor["name"], exception.message))
                    row = self._get_empty_row()
                else:
                    # we raise an exception here even though the make_kwargs specify to skip_exceptions
                    # this is because scraper_errors tracking is disabled - so the exception will skip silently
                    # and we can't have that, can we?
                    raise exception
            else:
                if self.enable_pre_append:
                    try:
                        self._pre_append(object, **make_kwargs)
                    except Exception, e:
                        self.logger.exception(e)
                        if enable_scraper_errors:
                            self.logger.warning("exception generating {}, will continue to next object".format(self.descriptor["name"]))
                            scraper_errors.append("exception generating {}: {}".format(self.descriptor["name"], e))
                        else:
                            self.logger.error("exception generating {}, stopping execution and raising the exception".format(self.descriptor["name"]))
                            raise e
                self.logger.debug('appending {} id {}'.format(self.object_name, object.id))
                if self.track_generated_objects:
                    self._generated_objects.append(object)
                row = object.all_field_values()
            if enable_scraper_errors:
                row["scraper_errors"] = "\n".join(scraper_errors)
            yield row

    def get_generated_objects(self):
        if self.track_generated_objects:
            return self._generated_objects
        else:
            raise Exception()
