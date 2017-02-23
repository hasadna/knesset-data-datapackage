from .base_datapackage_test_case import BaseDatapackageTestCase
from .mocks import DummyResource
import os


class BaseResourceTestCase(BaseDatapackageTestCase):

    def given_dummy_resource_is_fetched(self):
        return DummyResource().fetch()

    def dummy_resource_fetch_result_should_contain_expected_data(self, fetch_result):
        self.assertEqual(fetch_result.next(), "hello")
        self.assertEqual(fetch_result.next(), "world")
        self.assertRaises(StopIteration, lambda: fetch_result.next())

    def given_dummy_resource_is_made_without_base_path(self):
        if os.path.exists("None.txt"):
            os.remove("None.txt")
        self.assertFalse(os.path.exists("None.txt"))
        DummyResource().make()

    def given_dummy_resource_is_made(self):
        resource = DummyResource("test", self.data_root)
        resource.make()
        return resource

    def test_fetch(self):
        fetch_result = self.given_dummy_resource_is_fetched()
        self.dummy_resource_fetch_result_should_contain_expected_data(fetch_result)

    def test_make_without_base_path(self):
        self.given_dummy_resource_is_made_without_base_path()
        with open("None.txt", "r") as f:
            self.assert_dummy_resource_file_contains_expected_content(f)
        os.remove("None.txt")

    def test_fetch_from_datapackage(self):
        resource = self.given_dummy_resource_is_made()
        self.dummy_resource_fetch_result_should_contain_expected_data(resource.fetch_from_datapackage())

