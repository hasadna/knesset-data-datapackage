from knesset_datapackage.base import BaseDatapackage, BaseResource, CsvResource, FilesResource, CsvFilesResource
from datetime import datetime
import os
from ..resources.members import MembersResource
from knesset_data.dataservice.mocks import MockMember
from collections import OrderedDict


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


class DummyResourceWithException(DummyResource):

    def fetch(self, **kwargs):
        for item in super(DummyResourceWithException, self).fetch(**kwargs):
            yield item
        raise Exception("dummy resource exception")


class DummyDatapackage(BaseDatapackage):

    NAME = "dummy-datapackage"
    RESOURCES = OrderedDict([("dummy-resource-with-exception", (DummyResourceWithException, {})),
                             ("dummy-resource", (DummyResource, {})),])

    def __init__(self, base_path, with_dependencies=True, without_exceptions=False):
        if without_exceptions:
            del self.RESOURCES["dummy-resource-with-exception"]
        super(DummyDatapackage, self).__init__(base_path, with_dependencies=with_dependencies)


class DummyCsvResource(CsvResource):

    def __init__(self, name=None, parent_datapackage_path=None, raise_exception=False):
        super(DummyCsvResource, self).__init__(name, parent_datapackage_path, {"fields": [{"name": "date", "type": "datetime"},
                                                                                          {"name": "integer", "type": "integer"},
                                                                                          {"name": "string", "type": "string"}]})
        self.raise_exception = raise_exception

    def _data_generator(self, **make_kwargs):
        yield {"date": datetime(2015, 5, 2), "integer": 5, "string": "hello world!"}
        if self.raise_exception:
            if make_kwargs.get("skip_exceptions"):
                yield "ERROR!"
            else:
                raise Exception("raised an exception!")
        else:
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

    def __init__(self, name=None, parent_datapackage_path=None):
        super(DummyCsvFilesResource, self).__init__(name, parent_datapackage_path,
                                                    {"fields": [{"name": "name", "type": "string"},
                                                                {"name": "text file", "type": "string"},
                                                                {"name": "doc file", "type": "string"}]},
                                                    file_fields=("text file", "doc file"))

    def _data_generator(self, **make_kwargs):
        if not os.path.exists(self._base_path):
            os.mkdir(self._base_path)
        for filename, content in [("hello_world.doc", "hello there! (IN DOC FORMAT!)"), ("hello_world.txt", "hello there!"),
                                  ("goodbye_world.doc", "goodbye DOC"), ("goodbye_world.txt", "goodbye TXT")]:
            with open(os.path.join(self._base_path, filename), "w") as f:
                f.write(content)
        yield {"name": "hello world", "text file": "hello_world.txt", "doc file": "hello_world.doc"}
        yield {"name": "goodbye world", "text file": "goodbye_world.txt", "doc file": "goodbye_world.doc"}


class MockMembersResource(MembersResource):
    collection = MockMember
