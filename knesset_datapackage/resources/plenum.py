from knesset_datapackage.base import CsvFilesResource
from knesset_data.html_scrapers.plenum import PlenumMeetings
from knesset_data.html_scrapers.mocks import MockPlenumMeetings
import os, json
from shutil import copy
from collections import OrderedDict


class PlenumMeetingsResource(CsvFilesResource):
    PROTOCOL_DATA_FIELDS = ["meeting_num_heb", "knesset_num_heb", "knesset_num", "booklet_num", "booklet_num_heb",
                            "booklet_meeting_num", "booklet_meeting_num_heb", "day_heb", "date_string_heb",
                            "time_string", "datetime"]

    def __init__(self, name, parent_datapackage_path):
        fields = [{"name": "day", "type": "integer", "description": "meeting day (1 = 1st day of month is)"},
                  {"name": "month", "type": "integer", "description": "meeting month (1 = January, 12 = December)"},
                  {"name": "year", "type": "integer", "description": "meeting year"},
                  {"name": "protocol_url", "type": "string", "description": "url to download the protocol file"},
                  {"name": "protocol_original", "type": "string", "description": "original file (without processing), in case of error will be empty"},
                  {"name": "protocol_antiword_text", "type": "string", "description": "text after antiword processing, in case of error will be empty"}]
        for field in self.PROTOCOL_DATA_FIELDS:
            field_name = field
            field_type = "string"
            field_description = None
            fields.append({"name": "protocol_{}".format(field_name),
                           "type": field_type,
                           "description": field_description})
        fields.append({"name": "scraper_errors", "type": "string", "description": "comma separated list of errors encountered"})
        json_table_schema = {"fields": fields}
        super(PlenumMeetingsResource, self).__init__(name, parent_datapackage_path, json_table_schema,
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
                meeting_path = os.path.join(str(plenum_meeting.year), str(plenum_meeting.month), str(plenum_meeting.day))
                os.makedirs(self.get_path(meeting_path))
                row["protocol_original"] = os.path.join(meeting_path, plenum_meeting.url.split("/")[-1])
                row["protocol_antiword_text"] = os.path.join(meeting_path, "{}.txt".format(plenum_meeting.url.split("/")[-1]))
                try:
                    with plenum_meeting.protocol as protocol:
                        copy(protocol.file_name, self.get_path(row["protocol_original"]))
                        with open(self.get_path(row["protocol_antiword_text"]), "w") as f:
                            f.write(protocol.antiword_text)
                        for field in self.PROTOCOL_DATA_FIELDS:
                            field_name = field
                            try:
                                val = getattr(protocol, field_name)
                            except Exception, e:
                                if make_kwargs.get("skip_exceptions"):
                                    val = ""
                                    self.logger.debug("error getting plenum protocol {} attribute".format(field_name))
                                    self.logger.debug(e, exc_info=1)
                                    scraper_errors.append("error getting protocol_{}: {}".format(field_name, e.message))
                                else:
                                    raise
                            row["protocol_{}".format(field_name)] = val
                except Exception, e:
                    if make_kwargs.get("skip_exceptions"):
                        row["protocol_original"] = ""
                        row["protocol_antiword_text"] = ""
                        self.logger.warn("error getting plenum protocol ({}): {}".format(meeting_path, e.message))
                        self.logger.debug(e, exc_info=1)
                        scraper_errors.append(e.message)
                    else:
                        raise
                row.update({"day": plenum_meeting.day,
                            "month": plenum_meeting.month,
                            "year": plenum_meeting.year,
                            "protocol_url": plenum_meeting.url,
                            "scraper_errors": ", ".join(scraper_errors)})
                yield row

        # for filename, content in [("hello_world.doc", "hello there! (IN DOC FORMAT!)"), ("hello_world.txt", "hello there!"),
        #                           ("goodbye_world.doc", "goodbye DOC"), ("goodbye_world.txt", "goodbye TXT")]:
        #     with open(os.path.join(self._base_path, filename), "w") as f:
        #         f.write(content)
        # yield {"name": "hello world", "text file": "hello_world.txt", "doc file": "hello_world.doc"}
        # yield {"name": "goodbye world", "text file": "goodbye_world.txt", "doc file": "goodbye_world.doc"}
