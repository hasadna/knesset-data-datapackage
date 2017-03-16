from .base_datapackage_test_case import BaseDatapackageTestCase
from .mocks import DummyCsvResource, MockMembersResource
import datetime
from knesset_data.dataservice.exceptions import KnessetDataServiceObjectException


class ExceptionsTestCase(BaseDatapackageTestCase):

    def assert_member_row(self, row, expected_id, expected_scraper_errors):
        self.assertEqual(row["id"], expected_id)
        if expected_scraper_errors is None:
            self.assertNotIn("scraper_errors", row)
        else:
            self.assertEqual(row["scraper_errors"], expected_scraper_errors)

    def test_dummy_exception(self):
        results_generator = DummyCsvResource("test", self.data_root, raise_exception=True).fetch()
        self.assertEqual(results_generator.next(), {'date': datetime.datetime(2015, 5, 2, 0, 0), 'integer': 5, 'string': 'hello world!'})
        with self.assertRaises(Exception) as cm:
            results_generator.next()
        self.assertEqual(cm.exception.message, "raised an exception!")

    def test_dummy_skipped_exception(self):
        results_generator = DummyCsvResource("test", self.data_root, raise_exception=True).fetch(skip_exceptions=True)
        self.assertEqual(list(results_generator), [{'date': datetime.datetime(2015, 5, 2, 0, 0), 'integer': 5, 'string': 'hello world!'},
                                                   "ERROR!"])

    def test_members_exception(self):
        results_generator = MockMembersResource("test-members-resource", self.data_root).fetch()
        self.assert_member_row(results_generator.next(), 200, "")
        self.assert_member_row(results_generator.next(), 201, "")
        self.assert_member_row(results_generator.next(), 202, "")
        with self.assertRaises(Exception) as cm:
            results_generator.next()
        self.assertEqual(cm.exception.message, "member with exception on init")

    def test_members_skipped_exception(self):
        results_generator = MockMembersResource("test-members-resource", self.data_root).fetch(skip_exceptions=True)
        # each value returned is a dict representing a csv row
        self.assert_member_row(results_generator.next(), 200, "")
        self.assert_member_row(results_generator.next(), 201, "")
        self.assert_member_row(results_generator.next(), 202, "")
        self.assert_member_row(results_generator.next(), "", "exception generating test-members-resource: member with exception on init")
        self.assert_member_row(results_generator.next(), "", "exception generating test-members-resource: member with exception on parse")
