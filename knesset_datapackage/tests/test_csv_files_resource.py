from base_datapackage_test_case import BaseDatapackageTestCase
from .mocks import DummyCsvFilesResource
import datetime, os


class CsvFilesResourceTestCase(BaseDatapackageTestCase):

    def given_dummy_csv_files_resource_is_fetched(self):
        return DummyCsvFilesResource("test", self.data_root).fetch()

    def given_dummy_csv_files_resource_was_made(self):
        resource = DummyCsvFilesResource("test", self.data_root)
        resource.make()
        return resource

    def assert_dummy_csv_files_resource_result_contains_expected_content(self, fetch_result):
        self.assertListEqual(list(fetch_result), ['file1.txt', 'file1.doc', 'file2.aaa'])
        self.assert_dummy_csv_files_resource_path_contains_expected_content()

    def assert_dummy_csv_files_resource_path_contains_expected_content(self):
        for filename, content in [("file1.txt", "hello there!"), ("file1.doc", "goodbye"), ("file2.aaa", "")]:
            with open(os.path.join(self.data_root, "test", filename), "r") as f:
                self.assertEqual(f.read(), content)

    def test_fetch(self):
        fetch_result = self.given_dummy_csv_files_resource_is_fetched()
        self.assert_dummy_csv_files_resource_result_contains_expected_content(fetch_result)

    def test_make(self):
        self.given_dummy_csv_files_resource_was_made()
        self.assert_dummy_csv_files_resource_path_contains_expected_content()

    def test_fetch_from_datapackage(self):
        resource = self.given_dummy_csv_files_resource_was_made()
        self.assert_dummy_csv_files_resource_result_contains_expected_content(resource.fetch_from_datapackage())
