from knesset_datapackage.base import BaseDatapackage, BaseResource, CsvResource, FilesResource, CsvFilesResource
from datetime import datetime
import os


class DummyResource(BaseResource):

    def __init__(self, name=None, parent_datapackage_path=None, json_table_schema=None):
        super(DummyResource, self).__init__(name, parent_datapackage_path)
        self.descriptor.update({"path": "{}.txt".format(name)})

    def make(self, **kwargs):
        if not self._skip_resource(**kwargs):
            with open("{}.txt".format(self._base_path), 'w') as f:
                for msg in self.fetch(**kwargs):
                    f.write("{}\n".format(msg))

    def fetch(self, **kwargs):
        if not self._skip_resource(**kwargs):
            yield "hello"
            yield "world"


    def fetch_from_datapackage(self, **kwargs):
        if not self._skip_resource(**kwargs):
            with open("{}.txt".format(self._base_path), 'r') as f:
                for line in f:
                    yield line[:-1]


class DummyDatapackage(BaseDatapackage):

    def __init__(self, base_path):
        super(DummyDatapackage, self).__init__(descriptor={
            "name": "dummy-datapackage"
        }, default_base_path=base_path)

    def _load_resources(self, descriptor, base_path):
        descriptor["resources"] = [DummyResource("dummy-resource", base_path)]
        return super(DummyDatapackage, self)._load_resources(descriptor, base_path)


class DummyCsvResource(CsvResource):

    def __init__(self, name=None, parent_datapackage_path=None):
        super(DummyCsvResource, self).__init__(name, parent_datapackage_path, {"fields": [{"name": "date", "type": "datetime"},
                                                                                          {"name": "integer", "type": "integer"},
                                                                                          {"name": "string", "type": "string"}]})

    def _data_generator(self, **make_kwargs):
        yield {"date": datetime(2015, 5, 2), "integer": 5, "string": "hello world!"}
        yield {"date": datetime(2013, 6, 9), "integer": 3, "string": "goodbye"}


class DummyFilesResource(FilesResource):

    def _data_generator(self, **make_kwargs):
        if not os.path.exists(self._base_path):
            os.mkdir(self._base_path)
        for filename, content in [("file1.txt", "hello there!"), ("file1.doc", "goodbye"), ("file2.aaa", "")]:
            with open(os.path.join(self._base_path, filename), "w") as f:
                f.write(content)
            yield filename


class DummyCsvFilesResource(CsvFilesResource):
    pass

