from knesset_datapackage.base import BaseDatapackage, BaseResource
import os


class DummyResource(BaseResource):

    def __init__(self, name=None, parent_datapackage_path=None, json_table_schema=None):
        super(DummyResource, self).__init__(name, parent_datapackage_path)
        self.descriptor.update({"path": "{}.txt".format(name)})

    def make(self, **kwargs):
        with open("{}.txt".format(self._base_path), 'w') as f:
            f.write("hello world")


class DummyDatapackage(BaseDatapackage):

    def __init__(self, base_path):
        super(DummyDatapackage, self).__init__(descriptor={
            "name": "dummy-datapackage"
        }, default_base_path=base_path)

    def _load_resources(self, descriptor, base_path):
        descriptor["resources"] = [DummyResource("dummy-resource", base_path)]
        return super(DummyDatapackage, self)._load_resources(descriptor, base_path)
