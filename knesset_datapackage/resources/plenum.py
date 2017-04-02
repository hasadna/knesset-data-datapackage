from knesset_datapackage.base import CsvFilesResource
from knesset_data.html_scrapers.plenum import PlenumMeetings
from knesset_data.html_scrapers.mocks import MockPlenumMeetings
from knesset_data.protocols.plenum import PlenumProtocolFile
import os, json
from shutil import copy
from collections import OrderedDict
from ..utils import merge_table_schemas


class PlenumMeetingsResource(CsvFilesResource):
    PROTOCOL_DATA_FIELDS = ["meeting_num_heb", "knesset_num_heb", "knesset_num", "booklet_num", "booklet_num_heb",
                            "booklet_meeting_num", "booklet_meeting_num_heb", "day_heb", "date_string_heb",
                            "time_string", "datetime"]

    def __init__(self, name, parent_datapackage_path):
        self._meeting_schema = PlenumMeetings.get_json_table_schema()
        self._protocol_schema = PlenumProtocolFile.get_json_table_schema()
        schema = merge_table_schemas(self._meeting_schema,
                                     self._protocol_schema,
                                     {"fields": [{"name": "protocol_original", "type": "string", "description": "original file (without processing), in case of error will be empty"},
                                                 {"name": "protocol_antiword_text", "type": "string", "description": "text after antiword processing, in case of error will be empty"},
                                                 {"name": "scraper_errors", "type": "string", "description": "comma separated list of errors encountered"}]})
        super(PlenumMeetingsResource, self).__init__(name, parent_datapackage_path, schema,
                                                     file_fields=["protocol_original", "protocol_antiword_text"])
        self.descriptor["plenum_errors"] = []

    def _get_plenum_meetings_instance(self, mock=None, **make_kwargs):
        if mock:
            return MockPlenumMeetings(full_protocol=True)
        else:
            return PlenumMeetings()

    def _data_generator(self, **make_kwargs):
        for plenum_meeting in self._get_plenum_meetings_instance(**make_kwargs).download(skip_exceptions=make_kwargs.get("skip_exceptions")):
            if make_kwargs.get("skip_exceptions") and isinstance(plenum_meeting, Exception):
                self.logger.error("encountered an unexpected exception fetching plenum protocol")
                self.logger.debug(plenum_meeting, exc_info=1)
                self.descriptor["plenum_errors"].append(plenum_meeting.message)
            else:
                row = self._get_empty_row()
                scraper_errors = []
                meeting_path = plenum_meeting.date.strftime("%Y/%m/%d")
                os.makedirs(self.get_path(meeting_path))
                protocol_original = os.path.join(meeting_path, plenum_meeting.url.split("/")[-1])
                protocol_antiword_text = os.path.join(meeting_path, "{}.txt".format(plenum_meeting.url.split("/")[-1]))
                try:
                    row.update({field["name"]: getattr(plenum_meeting, field["name"]) for field in self._meeting_schema["fields"]})
                    with plenum_meeting.protocol as protocol:
                        copy(protocol.file_name, self.get_path(protocol_original))
                        row["protocol_original"] = protocol_original
                        with open(self.get_path(protocol_antiword_text), "w") as f:
                            f.write(protocol.antiword_text)
                        row["protocol_antiword_text"] = protocol_antiword_text
                        for field in self._protocol_schema["fields"]:
                            try:
                                row[field["name"]] = getattr(protocol, field["name"])
                            except Exception, e:
                                if make_kwargs.get("skip_exceptions"):
                                    self.logger.debug("error getting plenum protocol {} attribute".format(field["name"]))
                                    self.logger.debug(e, exc_info=1)
                                    scraper_errors.append("error getting protocol attribute {}: {}".format(field["name"], e.message))
                                else:
                                    raise
                except Exception, e:
                    if make_kwargs.get("skip_exceptions"):
                        self.logger.warn("error getting plenum protocol ({}): {}".format(meeting_path, e.message))
                        self.logger.debug(e, exc_info=1)
                        scraper_errors.append(e.message)
                    else:
                        raise
                row["scraper_errors"] = ", ".join(scraper_errors)
                yield row
