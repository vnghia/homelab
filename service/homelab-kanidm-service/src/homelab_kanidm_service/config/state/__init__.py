from __future__ import annotations

from homelab_docker.extract import GlobalExtract
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

    def build(self, openid_group: str) -> KanidmStateConfig:
        return self.__replace__(
            groups=KanidmStateGroupConfig(
                self.groups.root
                | {
                    openid_group: KanidmStateGroupModel(
                        members=[
                            GlobalExtract.from_simple(member)
                            for member in list(self.persons.root.keys())
                        ]
                    )
                }
                | {
                    KanidmStatePersonConfig.to_group_name(
                        member
                    ): KanidmStateGroupModel(
                        members=[GlobalExtract.from_simple(member)]
                    )
                    for member in list(self.persons.root.keys())
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
