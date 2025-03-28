from __future__ import annotations

from homelab_docker.extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class KanidmStateSystemOauthModel(HomelabBaseModel):
    present: bool = True
    public: bool = False
    display_name: GlobalExtract
    origin_url: list[GlobalExtract]
    origin_landing: GlobalExtract
    prefer_short_username: bool = False
    scope_maps: dict[str, list[str]] = {}

    def add_openid_scope(self, openid_group: str) -> KanidmStateSystemOauthModel:
        return self.__replace__(
            scope_maps=self.scope_maps | {openid_group: ["openid", "email", "profile"]}
        )
