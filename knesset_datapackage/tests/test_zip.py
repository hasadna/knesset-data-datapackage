from unittest import TestCase
from .mocks import DummyDatapackage
from tempfile import mkdtemp
import os
import shutil
import zipfile
import json


class TestDatapackageZip(TestCase):

    def setUp(self):
        self.data_roots = []
        self.data_root = self.given_temporary_data_root()
        self.datapackage_root = os.path.join(self.data_root, "datapackage")

    def test(self):
        # saving to zip
        datapackage = self.given_dummy_datapackage_was_made()
        datapackage_zip_file = self.given_datapackage_is_saved_to_zip(datapackage)
        self.dummy_datapackage_zip_should_contain_json_and_dummy_resource(datapackage_zip_file)
        # loading from the zip
        # get a new data_root - to prevent collisions (it will be deleted on tearDown)
        data_root = self.given_temporary_data_root()
        datapackage_root = self.given_dummy_datapackage_is_loaded_from_zipfile(datapackage_zip_file, data_root)
        self.dummy_datapackage_path_should_contain_json_and_dummy_resource(datapackage_root)

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

    def given_datapackage_is_saved_to_zip(self, datapackage):
        datapackage_zip_file = os.path.join(self.data_root, "datapackage.zip")
        datapackage.save_to_zip(datapackage_zip_file, self.data_root)
        return datapackage_zip_file

    def dummy_datapackage_zip_should_contain_json_and_dummy_resource(self, datapackage_zip_file):
        with zipfile.ZipFile(datapackage_zip_file, 'r') as zipf:
            self.assertEqual(zipf.namelist(), ['datapackage/datapackage.json', 'datapackage/dummy-resource.txt'])
            with zipf.open("datapackage/datapackage.json") as f:
                self.assertEqual(json.loads(f.read()), {"name": "dummy-datapackage",
                                                        "resources": [{"path": "dummy-resource.txt", "name": "dummy-resource"}]})
            with zipf.open("datapackage/dummy-resource.txt") as f:
                self.assertEqual(f.read(), "hello world")

    def given_dummy_datapackage_is_loaded_from_zipfile(self, datapackage_zip_file, data_root):
        return DummyDatapackage.load_from_zip(datapackage_zip_file, data_root)

    def dummy_datapackage_path_should_contain_json_and_dummy_resource(self, datapackage_root):
        with open(os.path.join(datapackage_root, "datapackage.json")) as f:
            self.assertEqual(json.loads(f.read()), {"name": "dummy-datapackage",
                                                    "resources": [{"path": "dummy-resource.txt", "name": "dummy-resource"}]})
        with open(os.path.join(datapackage_root, "dummy-resource.txt")) as f:
            self.assertEqual(f.read(), "hello world")
