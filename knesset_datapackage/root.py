from knesset_datapackage.base import BaseDatapackage, DatapackageResourceLink
from knesset_datapackage.resources.committees import CommitteesResource, CommitteeMeetingsResource, CommitteeMeetingProtocolsResource
from knesset_datapackage.resources.members import MembersResource
from knesset_datapackage.resources.plenum import PlenumMeetingsResource
from knesset_datapackage.resources.persons import PersonsResource, PositionsResource, PersonsToPositionsResource
from collections import OrderedDict


class RootDatapackage(BaseDatapackage):

    NAME = "knesset-data"
    RESOURCES = OrderedDict([
        ("committees", (CommitteesResource, {"meetings_resource": DatapackageResourceLink("committee-meetings")})),
        ("committee-meetings", (CommitteeMeetingsResource, {"protocols_resource": DatapackageResourceLink("committee-meetings-protocols")})),
        ("committee-meetings-protocols", (CommitteeMeetingProtocolsResource, {})),

        ("members", (MembersResource, {})),

        ("plenum-meetings", (PlenumMeetingsResource, {})),
        
        ("persons-person", (PersonsResource, {})),
        ("persons-position", (PositionsResource, {})),
        ("persons-persons-to-positions", (PersonsToPositionsResource, {})),
    ])
