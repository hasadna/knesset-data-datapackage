from .base_datapackage_test_case import BaseDatapackageTestCase
from .mocks import DummyDatapackage
import os
import zipfile


class ZipTestCase(BaseDatapackageTestCase):

    def given_datapackage_is_saved_to_zip(self, datapackage):
        datapackage_zip_file = os.path.join(self.data_root, "datapackage.zip")
        datapackage.save_to_zip(datapackage_zip_file, self.data_root)
        return datapackage_zip_file

    def dummy_datapackage_zip_should_contain_json_and_dummy_resource(self, datapackage_zip_file):
        with zipfile.ZipFile(datapackage_zip_file, 'r') as zipf:
            self.assertEqual(len(zipf.namelist()), 2)
            with zipf.open("datapackage/datapackage.json") as f: self.assert_dummy_resource_datapackage_json_contains_expected_content(f)
            with zipf.open("datapackage/dummy-resource.txt") as f: self.assert_dummy_resource_file_contains_expected_content(f)

    def given_dummy_datapackage_is_loaded_from_zipfile(self, datapackage_zip_file, data_root):
        return DummyDatapackage.load_from_zip(datapackage_zip_file, data_root)

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
