from knesset_datapackage.base import BaseDatapackage, DatapackageResourceLink
from knesset_datapackage.resources.committees import CommitteesResource, CommitteeMeetingsResource, CommitteeMeetingProtocolsResource
from knesset_datapackage.resources.members import MembersResource


class RootDatapackage(BaseDatapackage):

    NAME = "knesset-data"
    RESOURCES = {
        "members": (MembersResource, {}),

        "committees": (CommitteesResource, {"meetings_resource": DatapackageResourceLink("committee-meetings")}),
        "committee-meetings": (CommitteeMeetingsResource, {"protocols_resource": DatapackageResourceLink("committee-meetings-protocols")}),
        "committee-meetings-protocols": (CommitteeMeetingProtocolsResource, {"members_resource": DatapackageResourceLink("members")}),
    }
