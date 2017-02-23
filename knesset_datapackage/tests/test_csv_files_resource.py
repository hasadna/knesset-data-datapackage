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
        self.assertListEqual([sorted(row.items()) for row in fetch_result], [[('doc file', 'hello_world.doc'),
                                                                              ('name', 'hello world'),
                                                                              ('text file', 'hello_world.txt')],
                                                                             [('doc file', 'goodbye_world.doc'),
                                                                              ('name', 'goodbye world'),
                                                                              ('text file', 'goodbye_world.txt')]])
        self.assert_dummy_csv_files_resource_path_contains_expected_content()

    def assert_dummy_csv_files_resource_path_contains_expected_content(self):
        for filename, content in [("hello_world.doc", "hello there! (IN DOC FORMAT!)"), ("hello_world.txt", "hello there!"),
                                  ("goodbye_world.doc", "goodbye DOC"), ("goodbye_world.txt", "goodbye TXT")]:
            with open(os.path.join(self.data_root, "test", filename), "r") as f:
                self.assertEqual(f.read(), content)

    def assert_dummy_csv_files_resource_path_contains_csv_file(self):
        with open(os.path.join(self.data_root, "test.csv"), "r") as f:
            self.assertEqual(f.read(), "name,text file,doc file\r\n"
                                       "hello world,hello_world.txt,hello_world.doc\r\n"
                                       "goodbye world,goodbye_world.txt,goodbye_world.doc\r\n")

    def assert_dummy_csv_files_resource_datapackage_descriptor(self, actual):
        expected = {'path': ['test.csv', 'hello_world.txt', 'hello_world.doc', 'goodbye_world.txt', 'goodbye_world.doc'],
                               'name': 'test',
                               'schema': {'fields': [{'type': 'string', 'name': 'name'},
                                                     {'type': 'string', 'name': 'text file'},
                                                     {'type': 'string', 'name': 'doc file'}]}}
        self.assertDictEqual(expected, actual)


    def test_fetch(self):
        # direct fetching from the source
        # datapackage.json is irelevant
        fetch_result = self.given_dummy_csv_files_resource_is_fetched()
        self.assert_dummy_csv_files_resource_result_contains_expected_content(fetch_result)

    def test_make(self):
        # make a datapackage and store in files
        # ensure directories contains the expected files
        # including the datapackage.json file
        resource = self.given_dummy_csv_files_resource_was_made()
        self.assert_dummy_csv_files_resource_path_contains_expected_content()
        self.assert_dummy_csv_files_resource_path_contains_csv_file()
        self.assert_dummy_csv_files_resource_datapackage_descriptor(resource.descriptor)

    def test_fetch_from_datapackage(self):
        # fetch from a previously made datapackage
        # we only care about the fetched data, we don't care about the datapackage.json file
        resource = self.given_dummy_csv_files_resource_was_made()
        self.assert_dummy_csv_files_resource_result_contains_expected_content(resource.fetch_from_datapackage())
