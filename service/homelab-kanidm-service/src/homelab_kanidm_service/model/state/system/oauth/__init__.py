from __future__ import annotations

import typing

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from .claim import KanidmStateSystemOauthClaimModel

if typing.TYPE_CHECKING:
    from .....config.state import KanidmStateConfig


class KanidmStateSystemOauthModel(HomelabBaseModel):
    present: bool = True
    public: bool = False
    display_name: GlobalExtract
    origin_url: list[GlobalExtract]
    origin_landing: GlobalExtract
    prefer_short_username: bool = False
    allow_insecure_client_disable_pkce: bool = False
    remove_orphaned_claim_maps: bool = True
    scope_maps: dict[str, list[str]] = {}
    claim_maps: dict[str, KanidmStateSystemOauthClaimModel] = {}

    def build(
        self, openid_group: str, kanidm_state: KanidmStateConfig
    ) -> KanidmStateSystemOauthModel:
        return self.__replace__(
            scope_maps=self.scope_maps | {openid_group: ["openid", "email", "profile"]},
            claim_maps={
                key: model.build(kanidm_state) for key, model in self.claim_maps.items()
            },
        )
