from .base_datapackage_test_case import BaseDatapackageTestCase
from .mocks import DummyCsvResource, MockMembersResource
import datetime
import os
import json


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
        self.assert_member_row(results_generator.next(), None, "exception generating test-members-resource: member with exception on init")
        self.assert_member_row(results_generator.next(), None, "exception generating test-members-resource: member with exception on parse")

    def test_members_exception_make(self):
        resource = MockMembersResource("test-members-resource", self.data_root)
        resource.make(skip_exceptions=True)
        with open ("{}.csv".format(resource.get_path())) as f:
            lines = [line.strip().split(",") for line in f.readlines()]
            header = lines[0]
            self.assertEqual(header, ['id', 'army_rank_id', 'army_history_desc',
                                      'army_history_desc_eng', 'country_id', 'country_desc',
                                      'country_desc_eng', 'minority_type_id', 'education_id',
                                      'education_desc', 'education_desc_eng', 'marital_status_id',
                                      'city_id', 'mk_status_id', 'name', 'name_eng', 'first_name',
                                      'first_name_eng', 'gender', 'birth_date', 'immigration_date',
                                      'children_number', 'death_date', 'email', 'email_on', 'photo',
                                      'phone1', 'phone2', 'phone_fax', 'present', 'public_activity',
                                      'public_activity_eng', 'note', 'note_eng', 'scraper_errors'])
            self.assertEqual(lines[1:], [['200',] + ["" for void in range(len(header)-1)],
                                         ['201',] + ["" for void in range(len(header)-1)],
                                         ['202',] + ["" for void in range(len(header)-1)],
                                         ["" for void in range(len(header) - 1)] + ['exception generating test-members-resource: member with exception on init'],
                                         ["" for void in range(len(header) - 1)] + ['exception generating test-members-resource: member with exception on parse'],])

    def test_exception_in_resource_while_making_datapackage(self):
        # default behavior - stop processing and raise exception
        with self.assertRaises(Exception) as cm:
            self.given_dummy_datapackage_was_made()
        self.assertEqual(cm.exception.message, "dummy resource exception")
        # with skip_exceptions enabled
        datapackage = self.given_dummy_datapackage_was_made(skip_exceptions=True)
        with open (os.path.join(datapackage.base_path, "datapackage.json")) as f:
            descriptor = json.loads(f.read())
            self.assertEqual(descriptor, {u'name': u'dummy-datapackage',
                                          u'resources': [{u'path': u'dummy-resource-with-exception.txt',
                                                          u'name': u'dummy-resource-with-exception',
                                                          u'error': u'dummy resource exception'},
                                                         {u'path': u'dummy-resource.txt',
                                                          u'name': u'dummy-resource'}]})
