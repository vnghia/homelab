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
        return self.__replace__(
            groups=KanidmStateGroupConfig(
                self.groups.root
                | {
                    openid_group: KanidmStateGroupModel(
                        members=[
                            GlobalExtract.from_simple(member)
                            for member in self.persons.root
                        ]
                    )
                }
                | {
                    admin_group: KanidmStateGroupModel(
                        members=[
                            GlobalExtract.from_simple(member)
                            for member, model in self.persons.root.items()
                            if model.admin
                        ]
                    )
                }
                | {
                    user_group: KanidmStateGroupModel(
                        members=[
                            GlobalExtract.from_simple(member)
                            for member, model in self.persons.root.items()
                            if not model.admin
                        ]
                    )
                }
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
