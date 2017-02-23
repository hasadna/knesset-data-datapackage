from base_datapackage_test_case import BaseDatapackageTestCase
from .mocks import DummyCsvResource
import datetime, os


class CsvResourceTestCase(BaseDatapackageTestCase):

    def given_dummy_csv_resource_is_fetched(self):
        return DummyCsvResource("test", self.data_root).fetch()

    def given_dummy_csv_resource_was_made(self):
        resource = DummyCsvResource("test", self.data_root)
        resource.make()
        return resource

    def assert_dummy_csv_resource_result_contains_expected_content(self, fetch_result):
        self.assertDictEqual(fetch_result.next(), {'date': datetime.datetime(2015, 5, 2, 0, 0), 'integer': 5, 'string': 'hello world!'})
        self.assertDictEqual(fetch_result.next(), {"date": datetime.datetime(2013, 6, 9, 0, 0), "integer": 3, "string": "goodbye"})
        self.assertRaises(StopIteration, lambda: fetch_result.next())

    def assert_dummy_csv_resource_path_contains_expected_content(self):
        with open(os.path.join(self.data_root, 'test.csv'), 'r') as f:
            self.assertListEqual(f.readlines(), ['date,integer,string\r\n', '2015-05-02T00:00:00,5,hello world!\r\n', '2013-06-09T00:00:00,3,goodbye\r\n'])

    def test_fetch(self):
        fetch_result = self.given_dummy_csv_resource_is_fetched()
        self.assert_dummy_csv_resource_result_contains_expected_content(fetch_result)

    def test_make(self):
        self.given_dummy_csv_resource_was_made()
        self.assert_dummy_csv_resource_path_contains_expected_content()

    def test_fetch_from_datapackage(self):
        resource = self.given_dummy_csv_resource_was_made()
        self.assert_dummy_csv_resource_result_contains_expected_content(resource.fetch_from_datapackage())
