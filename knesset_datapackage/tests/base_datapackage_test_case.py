from unittest import TestCase
from tempfile import mkdtemp
from .mocks import DummyDatapackage
import shutil, os, json


class BaseDatapackageTestCase(TestCase):

    def setUp(self):
        self.data_roots = []
        self.data_root = self.given_temporary_data_root()
        self.datapackage_root = os.path.join(self.data_root, "datapackage")

    def tearDown(self):
        for data_root in self.data_roots:
            shutil.rmtree(data_root)

    def given_temporary_data_root(self):
        data_root = mkdtemp("knesset-datapackage-tests")
        self.data_roots.append(data_root)
        return data_root

    def given_dummy_datapackage_was_made(self):
        datapackage = DummyDatapackage(self.datapackage_root)
        datapackage.make()
        return datapackage

    def assert_dummy_resource_file_contains_expected_content(self, f):
        self.assertEqual(f.read(), "hello\nworld\n")

    def assert_dummy_resource_datapackage_json_contains_expected_content(self, f):
        self.assertEqual(json.loads(f.read()), {"name": "dummy-datapackage",
                                                "resources": [{"path": "dummy-resource.txt", "name": "dummy-resource"}]})

    def dummy_datapackage_path_should_contain_json_and_dummy_resource(self, datapackage_root):
        with open(os.path.join(datapackage_root, "datapackage.json")) as f: self.assert_dummy_resource_datapackage_json_contains_expected_content(f)
        with open(os.path.join(datapackage_root, "dummy-resource.txt")) as f: self.assert_dummy_resource_file_contains_expected_content(f)
