# encoding: utf-8
from .committees import CommitteesResource, CommitteeMeetingsResource, CommitteeMeetingProtocolsResource
from knesset_data.dataservice.committees import Committee, CommitteeMeeting
from .plenum import PlenumMeetingsResource
from ..tests.base_datapackage_test_case import BaseDatapackageTestCase
import datetime
import os
import contextlib
import unicodecsv
from ..utils import cast_value

# you can use this to get a template of the dataservice data
# for example -
# {f._knesset_field_name: f.get_json_table_schema_field() for f in Committee.get_fields().values()}


COMMITTEE_SOURCE_DATA = {"committee_id": "-1",
                         'committee_type_id': 4,
                         'committee_parent_id': None,
                         'committee_name': u"hebrew name",
                         'committee_name_eng': u"string",
                         'committee_name_arb': u'string',
                         'committee_begin_date': datetime.datetime(1950, 1, 1, 0, 0),
                         'committee_end_date': None,
                         'committee_desc': u"hebrew description",
                         'committee_desc_eng': u"string",
                         'committee_desc_arb': u"string",
                         'committee_note': u"string",
                         'committee_note_eng': u"string",
                         'committee_portal_link': u"can be used to link to the dedicated page in knesset website", }

COMMITTEE_EXPECTED_DATA = {'id': '-1',
                           'type_id': 4,
                           'parent_id': None,
                           'name': u'hebrew name',
                           'name_eng': u'string',
                           'name_arb': u'string',
                           'begin_date': datetime.datetime(1950, 1, 1, 0, 0),
                           'end_date': None,
                           'description': u'hebrew description',
                           'description_eng': u'string',
                           'description_arb': u'string',
                           'note': u'string',
                           'note_eng': u'string',
                           'portal_link': u'can be used to link to the dedicated page in knesset website',
                           'scraper_errors': u'', }

COMMITTEE_MEETING_SOURCE_DATA = {'committeebackgroundpagelink': u"",
                                 'committee_agenda_canceled': u"",
                                 'committee_agenda_committee_id': -1,
                                 'committee_agenda_id': -1,
                                 'committee_agenda_place': u"",
                                 'committee_agenda_associated': u"",
                                 'committee_agenda_associated_id': u"",
                                 'committee_agenda_invited': u"",
                                 'committee_agenda_invited1': u"",
                                 'committee_agenda_note': u"",
                                 'committee_agenda_special': u"",
                                 'committee_agenda_sub': u"",
                                 'date_creation': u"",
                                 'oldurl': u"",
                                 'startdatetime': u"",
                                 'topic_id': u"",
                                 'committee_agenda_date': datetime.datetime(1951, 1, 1, 0, 0),
                                 'committee_agenda_session_content': u"",
                                 'committee_date': u"",
                                 'committee_date_order': u"",
                                 'committee_day': u"",
                                 'committee_location': u"",
                                 'committee_material_hour': u"",
                                 'committee_month': u"",
                                 'material_comittee_id': u"",
                                 'material_expiration_date': u"",
                                 'material_id': u"",
                                 'meeting_is_paused': u"",
                                 'meeting_start': u"",
                                 'meeting_stop': u"",
                                 'sd2committee_agenda_invite': u"",
                                 'streaming_url': u"",
                                 'title': u"",
                                 'url': u"",}

COMMITTEE_MEETING_EXPECTED_DATA = {'protocol': u'',
                                   'session_content': u'',
                                   'agenda_special ': u'',
                                   'datetime': datetime.datetime(1951, 1, 1, 0, 0),
                                   'material_expiration_date ': u'',
                                   'id': -1,
                                   'meeting_stop ': u'',
                                   'agenda_associated_id ': u'', 'committee_id': -1, 'agenda_invite ': u'',
                                   'title': u'', 'creation_date ': u'', 'agenda_invited1 ': u'', 'streaming_url ': u'',
                                   'date ': u'', 'place ': u'', 'scraper_errors': u'', 'old_url ': u'', 'month ': u'',
                                   'note ': u'', 'day ': u'', 'material_id ': u'', 'start_datetime ': u'',
                                   'material_hour ': u'', 'is_paused ': u'', 'agenda_associated ': u'',
                                   'date_order ': u'', 'meeting_start ': u'', 'location ': u'', 'topid_id ': u'',
                                   'agenda_sub ': u'', 'url': u'', 'agenda_invited ': u'', 'agenda_canceled ': u'',
                                   'material_committee_id ': u'', 'background_page_link ': u''
                                   }


class MockCommitteesResource(CommitteesResource):

    def _get_objects_by_main(self, void, proxies=None, **kwargs):
        return [
            Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=1)}),
            Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=2)})
        ]

    def _get_objects_by_active(self, void, proxies=None, **kwargs):
        return [
            Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=3)})
        ]

    def _collection_get(self, object_id, proxies):
        if object_id == 4:
            return Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=4)})

    def _collection_get_page(self, order_by, proxies):
        pass

    def _collection_get_all(self, proxies, skip_exceptions):
        return [
            Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=1)}),
            Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=2)}),
            Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=3)}),
            Committee({"data": dict(COMMITTEE_SOURCE_DATA, committee_id=4)})
        ]


class MockCommitteeMeetingsResource(CommitteeMeetingsResource):

    def _committee_meeting_get(self, committee_id, fromdate, proxies):
        return [
            CommitteeMeeting({"data": dict(COMMITTEE_MEETING_SOURCE_DATA, committee_agenda_id=5)}),
            CommitteeMeeting({"data": dict(COMMITTEE_MEETING_SOURCE_DATA, committee_agenda_id=6)})
        ]


class ResourcesTestCase(BaseDatapackageTestCase):

    maxDiff = None

    def _make_and_fetch_resource(self, get_resource, **make_kwargs):
        get_resource().make(**make_kwargs)
        return get_resource().fetch(**make_kwargs)

    def test_committees(self):
        # fetching directly
        self.assertEqual(list(MockCommitteesResource().fetch()), [dict(COMMITTEE_EXPECTED_DATA, id=3)])
        self.assertEqual(list(MockCommitteesResource().fetch(committee_ids=[4])), [dict(COMMITTEE_EXPECTED_DATA, id=4)])
        self.assertEqual(list(MockCommitteesResource().fetch(all_committees=True)), [dict(COMMITTEE_EXPECTED_DATA, id=1),
                                                                                     dict(COMMITTEE_EXPECTED_DATA, id=2),
                                                                                     dict(COMMITTEE_EXPECTED_DATA, id=3),
                                                                                     dict(COMMITTEE_EXPECTED_DATA, id=4)])
        self.assertEqual(list(MockCommitteesResource().fetch(main_committees=True)),
                         [dict(COMMITTEE_EXPECTED_DATA, id=1),
                          dict(COMMITTEE_EXPECTED_DATA, id=2),])
        # making the resource
        data_root = self.given_temporary_data_root()
        MockCommitteesResource("committees", data_root).make()
        with open(os.path.join(data_root, "committees.csv")) as f:
            lines = unicodecsv.reader(f.readlines())
            self.assertEqual(list(lines), [
                ['id', 'type_id', 'parent_id', 'name', 'name_eng', 'name_arb', 'begin_date',
                 'end_date', 'description', 'description_eng', 'description_arb', 'note',
                 'note_eng', 'portal_link', 'scraper_errors'],
                ['3', '4', '', 'hebrew name', 'string', 'string', '1950-01-01T00:00:00',
                 '', 'hebrew description', 'string', 'string', 'string',
                 'string', 'can be used to link to the dedicated page in knesset website', '']
            ])
        # fetching from the made resource
        fetched_items = MockCommitteesResource("committees", data_root).fetch_from_datapackage()
        fetched_items = [dict(oredered_dict.items()) for oredered_dict in fetched_items]
        self.assertEqual(fetched_items, [dict(COMMITTEE_EXPECTED_DATA, id=3)])

    def test_committee_meetings(self):
        # committee meetings support only appending to csv
        data_root = self.given_temporary_data_root()
        resource = MockCommitteeMeetingsResource("committee-meetings", data_root)
        # append meetings for the given committee
        resource.append_for_committee(6)
        # fetch them from the csv
        fetched_items = MockCommitteeMeetingsResource("committee-meetings", data_root).fetch_from_datapackage()
        fetched_items = [dict(oredered_dict.items()) for oredered_dict in fetched_items]
        self.assertEqual(fetched_items, [dict(COMMITTEE_MEETING_EXPECTED_DATA, id=5),
                                         dict(COMMITTEE_MEETING_EXPECTED_DATA, id=6)])

    def test_committee_meeting_protocols(self):
        # protocols only support appending
        resource = CommitteeMeetingProtocolsResource("committee-meeting-protocols", self.given_temporary_data_root())
        committee_id, meeting_id, meeting_datetime = 6, 7, datetime.datetime(1953,5,4)
        # a contextmanager for mock protocol
        @contextlib.contextmanager
        def meeting_protocol():
            yield type("MockProtocol", (object,), {"text": "Hello World!",
                                                   "parts": [type("MockProtocolPart", (object,), {"header": "mock header", "body": "mock body"}),
                                                             type("MockProtocolPart", (object,), {"header": "mock header 2", "body": "mock body 2"})],
                                                   "file_name": ""})
        # appending using the fake protocol
        resource.append_for_meeting(committee_id, meeting_id, meeting_datetime, meeting_protocol(), skip_exceptions=True)
        # checking the created files
        with open(resource.get_file_path(".csv")) as f:
            self.assertEqual(list(unicodecsv.reader(f.readlines())),
                             [['committee_id', 'meeting_id', 'text',
                               'parts',
                               'original',
                               'scraper_errors'],
                              ['6',            '7',          'committee_6/7_1953-05-04_00-00-00/protocol.txt',
                               'committee_6/7_1953-05-04_00-00-00/protocol.csv', '',
                               "error getting original file: [Errno 2] No such file or directory: ''"]])
        with open(resource.get_path("committee_6", "7_1953-05-04_00-00-00", "protocol.txt")) as f:
            self.assertEqual(f.readlines(), ["Hello World!"])
        with open(resource.get_path("committee_6", "7_1953-05-04_00-00-00", "protocol.csv")) as f:
            self.assertEqual(f.readlines(), ['header,body\r\n', 'mock header,mock body\r\n', 'mock header 2,mock body 2\r\n'])

    def test_plenum_meetings(self):
        # it's important to run the make of a resource, even if not checking the output - to test the casting of values
        PlenumMeetingsResource("plenum", self.given_temporary_data_root()).make(mock=True, skip_exceptions=True)
        resource = PlenumMeetingsResource("plenum", self.given_temporary_data_root())
        results = list(resource.fetch(mock=True, skip_exceptions=True))
        # results = list(PlenumMeetingsResource("plenum", data_root).fetch(mock=True, skip_exceptions=True))
        self.assertEqual(len(results), 41)
        self.assertEqual(results[0],
                         # meeting fields
                         {'date': datetime.date(2015, 5, 20),
                          'url': u"http://www.knesset.gov.il/plenum/data/20_ptm_307658.doc",
                          # protocol fields
                          'booklet_num_heb': None,
                          'booklet_meeting_num': 219,
                          'knesset_num_heb': "עשרים",
                          'datetime': datetime.datetime(2017, 3, 21, 16),
                          'time_string': ("16", "00"),
                          'knesset_num': 20,
                          'header_text': """NL2017-03-21OMNITECHNLNLNLNLדברי הכנסתNLNLחוב' כ"אNLNLישיבה רי"טNLNLהישיבה המאתיים-ותשע-עשרה של הכנסת העשריםNLNLיום שלישי, כ"ג באדר התשע"ז (21 במרס 2017)NLNLירושלים, הכנסת, שעה 16:00NLNLתוכן ענייניםNLNLמסמכים שהונחו על שולחן הכנסת 5NLNLסגן מזכירת הכנסת נאזם בדר: 5NLNLנאומים בני דקה 6NLNLטלב אבו עראר (הרשימה המשותפת): 6NLNLיואב בן צור (ש"ס): 6NLNLאיתן ברושי (המחנה הציוני): 8NLNLענת ברקו (הליכוד): 8NLNLחיים ילין (יש עתיד): 10NLNLיהודה גליק (הליכוד): 10NLNLיוסי יונה (המחנה הציוני): 11NLNLמירב בן ארי (כולנו): 12NLNLמירב בן ארי (כולנו): 12NLNLקסניה סבטלובה (המחנה הציוני): 14NLNLדב חנין (הרשימה המשותפת): 15NLNLעאידה תומא סלימאן (הרשימה המשותפת): 16NLNLמנחם אליעז""",
                          'meeting_num_heb': "מאתיים-ותשע-עשרה",
                          'booklet_meeting_num_heb': "רי\"ט",
                          'booklet_num': None,
                          'date_string_heb': ('21', "מרס", '2017'),
                          'day_heb': "שלישי",
                          # protocol files
                          'protocol_original': u"2015/05/20/20_ptm_307658.doc",
                          'protocol_antiword_text': "2015/05/20/20_ptm_307658.doc.txt",
                          'scraper_errors': "error getting protocol attribute booklet_num: 'NoneType' object has no attribute 'decode'",})
        self.assertEqual(os.path.getsize(resource.get_path(results[0]["protocol_original"])), 868864)
        self.assertEqual(os.path.getsize(resource.get_path(results[0]["protocol_antiword_text"])), 348448)
