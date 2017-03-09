from knesset_datapackage.base import CsvResource


class BaseKnessetDataServiceCollectionResource(CsvResource):
    collection = None
    object_name = "object"
    track_generated_objects = False
    collection_getter_kwargs = {
        # kwarg: getter type
        # OBJECT will be replaced with object_name
        "OBJECT_ids": "ids"
    }
    default_getter_type = "all"
    enable_pre_append = False
    get_latest_by_page_estimate = None  # to enable - set to tuple of (ORDERBY_FIELD, ESTIMATED_OBJECTS_PER_DAY)
                                        # allows to limit amount of returned data in all getter
                                        # by providing the ordering field and estimated objects per day

    def __init__(self, name, parent_datapackage_path):
        super(BaseKnessetDataServiceCollectionResource, self).__init__(name, parent_datapackage_path, self._get_json_table_schema())
        if self.track_generated_objects:
            self._generated_objects = []

    def _get_json_table_schema(self):
        schema = self.collection.get_json_table_schema()
        if self.enable_pre_append:
            schema["fields"].append({"type": "string", "name": "scraper_errors"})
        return schema

    def _collection_get(self, object_id, proxies):
        return self.collection.get(object_id, proxies=proxies)

    def _collection_get_page(self, order_by, proxies):
        return self.collection.get_page(order_by=order_by, proxies=proxies)

    def _collection_get_all(self, proxies):
        return self.collection.get_all(proxies=proxies)

    def _get_objects_by_ids(self, ids, proxies=None, **make_kwargs):
        self.logger.info('fetching {} ids: {}'.format(self.object_name, ids))
        self.descriptor["description"] = "specific {} ids".format(self.object_name)
        return (self._collection_get(object_id, proxies=proxies) for object_id in ids)

    def _get_objects_by_all(self, void, proxies=None, **make_kwargs):
        if self.get_latest_by_page_estimate:
            order_field, estimated_per_day = self.get_latest_by_page_estimate
            days = make_kwargs.get('days', 5)
            target_num_results = days * estimated_per_day
            self.logger.info('fetching up to {} {}s based on ordering of {}'.format(target_num_results, self.object_name, order_field))
            self.descriptor["description"] = "up to {} {}s based on ordering of {}".format(target_num_results, self.object_name, order_field)
            num_results = 0
            while num_results < target_num_results:
                for object in self._collection_get_page(order_by=(order_field, "desc"), proxies=proxies):
                    num_results += 1
                    yield object
        else:
            self.logger.info('fetching all {}s'.format(self.object_name))
            self.descriptor["description"] = "all {}s".format(self.object_name)
            for object in self._collection_get_all(proxies=proxies):
                yield object

    def _get_objects(self, proxies=None, **make_kwargs):
        for kwarg, gtype in self.collection_getter_kwargs.iteritems():
            kwarg = kwarg.replace('OBJECT', self.object_name)
            kwarg_value = make_kwargs.get(kwarg)
            if kwarg_value:
                return getattr(self, "_get_objects_by_{}".format(gtype))(kwarg_value, proxies=proxies, **make_kwargs)
        return getattr(self, "_get_objects_by_{}".format(self.default_getter_type))(None, proxies=proxies, **make_kwargs)

    def _pre_append(self, object, **make_kwargs):
        # allows for extending classes to perform additional work / update related resources
        # you will need to set enable_pre_append = True for it to work
        pass

    def _data_generator(self, **make_kwargs):
        for object in self._get_objects(**make_kwargs):
            if self.enable_pre_append:
                scraper_errors = []
                try:
                    self._pre_append(object, **make_kwargs)
                except Exception, e:
                    scraper_errors.append("exception generating {}: {}".format(self.descriptor["name"], e))
                    self.logger.warning("exception generating {}, will continue to next object".format(self.descriptor["name"]))
                    self.logger.exception(e)
            self.logger.debug('appending {} id {}'.format(self.object_name, object.id))
            if self.track_generated_objects:
                self._generated_objects.append(object)
            row = object.all_field_values()
            if self.enable_pre_append:
                row["scraper_errors"] = "\n".join(scraper_errors)
            yield row

    def get_generated_objects(self):
        if self.track_generated_objects:
            return self._generated_objects
        else:
            raise Exception()
