from datapackage.datapackage import DataPackage
from datapackage.resource import Resource, TabularResource
import os
import logging
import json
import unicodecsv
from collections import OrderedDict
import iso8601
import zipfile
from .utils import uncast_value


class BaseResource(Resource):

    def __init__(self, name=None, parent_datapackage_path=None, descriptor=None):
        if not descriptor:
            descriptor = OrderedDict()
        descriptor["name"] = name
        if name and parent_datapackage_path:
            default_base_path = os.path.join(parent_datapackage_path, name)
        else:
            default_base_path = None
        super(BaseResource, self).__init__(descriptor, default_base_path)

    def make(self, **kwargs):
        # make the resource and store it in base_path
        # should use fetch function to get each portion of data, then store it
        # be sure to check _skip_resource - which logs some info messages and checks if resource should be skipped
        raise NotImplementedError()

    def fetch(self, **kwargs):
        # fetch fresh data based on the given kwargs
        # should return a generator which yields each portion of data (e.g. each row)
        # be sure to check _skip_resource - which logs some info messages and checks if resource should be skipped
        raise NotImplementedError()

    def fetch_from_datapackage(self, **kwargs):
        # fetch data from a previously fetched datapackage
        # kwargs which affect fetching of the data will be ignored - as data was already fetched
        # should return a generator which yields each portion of data (e.g. each row)
        # be sure to check _skip_resource - which logs some info messages and checks if resource should be skipped
        raise NotImplementedError()

    def _skip_resource(self, include=None, exclude=None, dry_run=False, resources=None, **kwargs):
        if not hasattr(self, '_logged_skip_message'):
            self._logged_skip_message = True
            log = True
        else:
            log = False
        full_name = self.descriptor["name"]
        if dry_run:
            if log:
                self.logger.info("skipping resource '{}' due to dry_run flag".format(full_name))
            return True
        elif include and not [True for str in include if len(str) > 0 and full_name.startswith(str)]:
            if log:
                self.logger.debug("skipping resource '{}' due to include filter".format(full_name))
            self._descriptor.update({k: None for k in self._descriptor if k != "name"})
            self._descriptor["description"] = "resource skipped due to include filter"
            return True
        elif exclude and [True for str in exclude if len(str) > 0 and full_name.startswith(str)]:
            if log:
                self.logger.debug("skipping resource '{}' due to exclude filter".format(full_name))
            self._descriptor.update({k: None for k in self._descriptor if k != "name"})
            self._descriptor["description"] = "resource skipped due to exclude filter"
            return True
        elif resources and full_name not in resources:
            if log:
                self.logger.debug("skipping resource '{}' due to resources param".format(full_name))
            self._descriptor.update({k: None for k in self._descriptor if k != "name"})
            self._descriptor["description"] = "resource skipped due to resources param"
            return True
        else:
            if log:
                self.logger.info("processing datapackage resource '{}'".format(full_name))
            return False

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__module__.replace("knesset_data.", ""))
        return self._logger

    def get_file_path(self, ext):
        return "{}{}".format(self.get_path(), ext)

    def get_path(self, *relpaths):
        if len(relpaths) > 0:
            return os.path.join(self._base_path, *relpaths)
        else:
            return self._base_path


class BaseTabularResource(BaseResource, TabularResource):

    def __init__(self, name, parent_datapackage_path, descriptor=None):
        BaseResource.__init__(self, name, parent_datapackage_path, descriptor)


class CsvResource(BaseTabularResource):

    def __init__(self, name=None, parent_datapackage_path=None, json_table_schema=None):
        super(CsvResource, self).__init__(name, parent_datapackage_path)
        self.descriptor.update({"path": "{}.csv".format(name),
                                "schema": json_table_schema})

    def _get_field_csv_value(self, val, schema):
        field_type = schema.get("type", "string")
        try:
            if val is None:
                return None
            elif field_type == "datetime":
                return val.isoformat().encode('utf8')
            elif field_type == "integer":
                return val
            elif field_type == "string":
                if isinstance(val, (str, unicode)):
                    try:
                        return val.encode('utf8')
                    except UnicodeDecodeError:
                        # TODO: investigate further, why this should happen and if this logic is correct
                        return json.dumps(val)
                else:
                    # TODO: check why this happens, I assume it's because of some special field
                    return json.dumps(val)
            else:
                # try different methods to encode the value
                for f in (lambda val: val.encode('utf8'),
                          lambda val: unicode(val).encode('utf8')):
                    try:
                        return f(val)
                    except Exception:
                        pass
                self.logger.warn("failed to encode value for {}".format(schema["name"]))
                return ""
        except Exception, e:
            self.logger.error("failed to decode value '{}' for schema '{}'".format(val, schema))
            raise

    def _get_field_original_value(self, csv_val, schema):
        try:
            val = csv_val.decode('utf8')
        except UnicodeEncodeError:
            val = csv_val
        if schema["type"] == "datetime":
            return iso8601.parse_date(val, default_timezone=None) if val != '' else None
        elif schema["type"] == "integer":
            return int(val) if val != '' else None
        else:
            return val

    def _data_generator(self, **make_kwargs):
        # if you want to use stream generation - you should return a generator here
        # alternatively - leave this function as is and use _append to add rows to the csv file
        return []

    def _append(self, row, **make_kwargs):
        if not self._skip_resource(**make_kwargs):
            # append a row (with values in native python format) to the csv file (creates the file and header if does not exist)
            if not self.csv_path:
                raise Exception('cannot append without a path')
            fields = self.descriptor["schema"]["fields"]
            if not hasattr(self, "_csv_file_initialized"):
                self._csv_file_initialized = True
                self.logger.info('writing csv resource to: {}'.format(self.csv_path))
                with open(self.csv_path, 'wb') as csv_file:
                    unicodecsv.writer(csv_file, encoding="utf-8").writerow([field["name"] for field in fields])
            with open(self.csv_path, 'ab') as csv_file:
                unicodecsv.writer(csv_file, encoding="utf-8").writerow([uncast_value(row[field["name"]], field) for field in fields])

    def _get_empty_row(self):
        return {field["name"]: None for field in self.descriptor["schema"]["fields"]}

    def _get_field_schema(self, field_name):
        matching_fields = [field for field in self.descriptor["schema"]["fields"] if field["name"] == field_name]
        if len(matching_fields) == 1:
            return matching_fields[0]
        else:
            raise Exception("found {} fields named {}".format(len(matching_fields), field_name))

    def _update_field_schema(self, field_name, updates):
        self._get_field_schema(field_name).update(updates)

    @property
    def csv_path(self):
        if self._base_path:
            return "{}.csv".format(self._base_path)
        else:
            return None

    def make(self, **kwargs):
        if not self._skip_resource(**kwargs):
            for row in self.fetch(**kwargs):
                self._append(row)
            return True

    def fetch(self, **kwargs):
        if not self._skip_resource(**kwargs):
            for row in self._data_generator(**kwargs):
                yield row

    def fetch_from_datapackage(self, **kwargs):
        if not self._skip_resource(**kwargs):
            # IMPORTANT!
            # after this point - kwargs are ignored as we are fetching from previously prepared csv data
            if self.csv_path and os.path.exists(self.csv_path):
                with open(self.csv_path, 'rb') as csv_file:
                    csv_reader = unicodecsv.reader(csv_file)
                    header_row = None
                    for row in csv_reader:
                        if not header_row:
                            header_row = row
                        else:
                            csv_row = OrderedDict(zip(header_row, row))
                            parsed_row = []
                            for field in self.descriptor["schema"]["fields"]:
                                try:
                                    parsed_row.append((field["name"], self._get_field_original_value(csv_row[field["name"]], field)))
                                except Exception as e:
                                    import logging
                                    message = "error parsing field %s in file %s : %s" % (field["name"],self.csv_path, str(e))
                                    logging.exception(message)
                                    raise Exception(message)
                            yield OrderedDict(parsed_row)


class FilesResource(BaseResource):

    def __init__(self, name, parent_datapackage_path):
        super(FilesResource, self).__init__(name, parent_datapackage_path, {"path": []})

    def _data_generator(self, **make_kwargs):
        # if you want to use stream generation - you should return a generator here
        # generator should return relative file paths (relative to base_path) of files it created
        # alternatively - leave this function as is and use _append to add files
        return []

    def _append(self, file_path, **make_kwargs):
        if not self._skip_resource(**make_kwargs):
            # append a file (which was already created and saved)
            if not self._base_path:
                raise Exception("cannot append without base_path")
            self.descriptor["path"].append(file_path.replace(self._base_path+"/", ""))

    def make(self, **kwargs):
        if not self._skip_resource(**kwargs):
            for file_path in self.fetch(**kwargs):
                self._append(file_path)
            return True

    def fetch(self, **kwargs):
        if not self._skip_resource(**kwargs):
            for file_path in self._data_generator(**kwargs):
                yield file_path

    def fetch_from_datapackage(self, **kwargs):
        if not self._skip_resource(**kwargs):
            # IMPORTANT!
            # after this point - kwargs are ignored as we are fetching from previously prepared csv data
            return (file_path for file_path in self._descriptor["path"])


class CsvFilesResource(CsvResource, FilesResource):
    """
    resource is same as CsvResource but with support for files with file paths in a csv column
     __init__ gets a file_fields which contains a list of field names that contain file paths
     you are responsible to write the files to those paths and add the path (relative to the base_path) to the csv row
    """

    def __init__(self, name=None, parent_datapackage_path=None, json_table_schema=None, file_fields=None):
        CsvResource.__init__(self, name, parent_datapackage_path, json_table_schema)
        # the descriptor path for csv is a single path to the csv file
        # we change it here so that the csv file will be the first path in a list of paths
        self.descriptor["path"] = [self.descriptor["path"]]
        # name of the csv columns that contain paths to a file
        # used to populate the descriptor path with all the files
        self._file_fields = file_fields

    def _append(self, row, **make_kwargs):
        """
        same as the csv resource append
        the row you append should contain the file fields (as specified in __init__ file_fields parameter
        the paths from the file fields will be added to the descriptor paths
        :param row: OrderedDict of the csv row to append (must match the json_table_schema)
        :param make_kwargs: the global datapackage make_kwargs
        """
        [FilesResource._append(self, row[field]) for field in self._file_fields if row[field] and row[field] != ""]
        CsvResource._append(self, row, **make_kwargs)


class DatapackageResourceLink(object):

    def __init__(self, resource_name):
        self.resource_name = resource_name


class BaseDatapackage(DataPackage):

    NAME = None
    RESOURCES = {
        # "resource_name": (resource_class, resource_init_kwargs),
    }

    def __init__(self, base_path, with_dependencies=True):
        self._with_dependencies = with_dependencies
        super(BaseDatapackage, self).__init__(descriptor={"name": self.NAME}, default_base_path=base_path)

    def _order_resources(self, resources):
        resources_dict = {resource.descriptor["name"]: resource for resource in resources}
        resources = []
        for resource_name, resource_kwargs in self.RESOURCES.items():
            resources.append(resources_dict[resource_name])
        return resources

    def _get_resources(self, resources, base_path, num_iterations=0):
        need_to_rerun = False
        for resource_name, resource_load_args in self.RESOURCES.items():
            resource_class, resource_kwargs = resource_load_args
            if resource_name not in [resource.descriptor["name"] for resource in resources]:
                resource_has_unloaded_dependency = False
                for kwarg, val in resource_kwargs.items():
                    if isinstance(val, DatapackageResourceLink):
                        if self._with_dependencies:
                            loaded_resources = {resource.descriptor["name"]: resource for resource in resources}
                            if val.resource_name in loaded_resources:
                                resource_kwargs[kwarg] = loaded_resources[val.resource_name]
                            else:
                                resource_has_unloaded_dependency = True
                        else:
                            del resource_kwargs[kwarg]
                if resource_has_unloaded_dependency:
                    need_to_rerun = True
                else:
                    resource = resource_class(resource_name, base_path, **resource_kwargs)
                    resources.append(resource)
        if need_to_rerun:
            num_iterations += 1
            if num_iterations > len(self.RESOURCES)*2:
                raise Exception("problem loading resources due to resource dependencies")
            else:
                return self._get_resources(resources, base_path, num_iterations)
        else:
            return self._order_resources(resources)

    def _load_resources(self, descriptor, base_path):
        descriptor["resources"] = self._get_resources([], base_path)
        resources = []
        for i, resource in enumerate(descriptor["resources"]):
            if isinstance(resource, BaseResource):
                json_resource = resource.descriptor
            else:
                json_resource = resource
            descriptor["resources"][i] = json_resource
            resources.append(resource)
        return resources

    @property
    def resources(self):
        return self._resources

    def get_resource(self, name):
        matching_resources = [resource for resource in self.resources if resource.descriptor["name"] == name]
        if len(matching_resources) == 1:
            return matching_resources[0]
        elif len(matching_resources) == 0:
            raise LookupError("could not find resource with name {}".format(name))
        else:
            raise LookupError("found more then 1 resource with name {}".format(name))

    def _dict_recursively_remove_nulls(self, old_dict):
        new_dict = OrderedDict()
        for k in old_dict:
            if old_dict[k] is not None:
                if isinstance(old_dict[k], (dict, OrderedDict)):
                    new_dict[k] = self._dict_recursively_remove_nulls(old_dict[k])
                elif isinstance(old_dict[k], list):
                    new_dict[k] = []
                    for e in old_dict[k]:
                        if isinstance(e, (dict, OrderedDict)):
                            new_dict[k].append(self._dict_recursively_remove_nulls(e))
                        else:
                            new_dict[k].append(e)
                else:
                    new_dict[k] = old_dict[k]
        return new_dict

    def get_json_descriptor(self):
        old_descriptor = self.descriptor
        new_descriptor = OrderedDict()
        new_descriptor["name"] = old_descriptor.pop("name")
        new_descriptor["description"] = old_descriptor.pop("description", None)
        new_descriptor["resources"] = []
        for old_resource in self.descriptor.pop("resources"):
            new_resource = OrderedDict()
            new_resource["name"] = old_resource.pop("name")
            new_resource["description"] = old_resource.pop("description", None)
            new_resource["path"] = old_resource.pop("path", None)
            old_schema = old_resource.pop("schema", None)
            if old_schema:
                new_schema = OrderedDict()
                new_fields = []
                for old_field in old_schema.pop("fields"):
                    new_field = OrderedDict()
                    new_field["name"] = old_field.pop("name")
                    new_field["type"] = old_field.pop("type")
                    new_field["description"] = old_field.pop("description", None)
                    new_fields.append(new_field)
                new_schema["fields"] = new_fields
                new_schema.update(old_schema)
                new_resource["schema"] = new_schema
            new_resource.update(old_resource)
            new_descriptor["resources"].append(new_resource)
        new_descriptor.update(old_descriptor)
        return json.dumps(self._dict_recursively_remove_nulls(new_descriptor), indent=True)

    def make(self, **kwargs):
        self.logger.info('making datapackage: "{}", base path: "{}"'.format(self.descriptor["name"], self.base_path))
        if not os.path.exists(self.base_path):
           os.mkdir(self.base_path)
        self.logger.info('making resources')
        for resource in self.resources:
            if isinstance(resource, BaseResource):
                try:
                    resource.make(**kwargs)
                except Exception, e:
                    if kwargs.get("skip_exceptions"):
                        self.logger.error("got an exception in {} resource: {}".format(resource.descriptor["name"], e.message))
                        self.logger.exception(e)
                        resource.descriptor["error"] = e.message
                    else:
                        raise
        self.logger.info('writing datapackage.json')
        with open(os.path.join(self.base_path, "datapackage.json"), 'w') as f:
            f.write(self.get_json_descriptor()+"\n")
        self.logger.info('done')

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__module__.replace("knesset_data.", ""))
        return self._logger

    def save_to_zip(self, zip_file_name, data_root):
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    real_file = os.path.join(root, file)
                    rel_file = real_file.replace(data_root, "")
                    zipf.write(real_file, rel_file)

    @classmethod
    def load_from_zip(cls, zip_file_name, data_root):
        with zipfile.ZipFile(zip_file_name, 'r') as zipf:
            zipf.extractall(data_root)
        return os.path.join(data_root, "datapackage")
