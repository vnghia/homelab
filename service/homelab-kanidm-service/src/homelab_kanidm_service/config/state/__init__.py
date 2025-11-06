from __future__ import annotations

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from ...model.state.group import KanidmStateGroupModel
from .group import KanidmStateGroupConfig
from .person import KanidmStatePersonConfig
from .system import KanidmStateSystemConfig
from .system.oauth import KanidmStateSystemOauthConfig


class KanidmStateConfig(HomelabBaseModel):
    groups: KanidmStateGroupConfig = KanidmStateGroupConfig()
    persons: KanidmStatePersonConfig = KanidmStatePersonConfig()
    systems: KanidmStateSystemConfig = KanidmStateSystemConfig()

    def build(
        self, openid_group: str, admin_group: str, user_group: str
    ) -> KanidmStateConfig:
        openid_members = []
        admin_members = []
        user_members = []
        for member, model in self.persons.root.items():
            member_extract = GlobalExtract.from_simple(member)
            openid_members.append(member_extract)
            if model.admin:
                admin_members.append(member_extract)
            else:
                user_members.append(member_extract)

        return self.__replace__(
            groups=KanidmStateGroupConfig(
                self.groups.root
                | {openid_group: KanidmStateGroupModel(members=openid_members)}
                | {admin_group: KanidmStateGroupModel(members=admin_members)}
                | {user_group: KanidmStateGroupModel(members=user_members)}
            ),
            systems=KanidmStateSystemConfig(
                oauth2=KanidmStateSystemOauthConfig(
                    {
                        system: model.build(openid_group, self)
                        for system, model in self.systems.oauth2.root.items()
                    }
                )
            ),
        )
