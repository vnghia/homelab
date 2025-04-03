from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import Self

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel

if typing.TYPE_CHECKING:
    from .....config.state import KanidmStateConfig


class KanidmStateSystemOauthClaimUserType(StrEnum):
    USERNAME = auto()


class KanidmStateSystemOauthClaimUserModel(HomelabBaseModel):
    user: KanidmStateSystemOauthClaimUserType


class KanidmStateSystemOauthClaimFullJoinType(StrEnum):
    SSV = auto()
    CSV = auto()
    ARRAY = auto()


class KanidmStateSystemOauthClaimFullModel(HomelabBaseModel):
    join_type: KanidmStateSystemOauthClaimFullJoinType = (
        KanidmStateSystemOauthClaimFullJoinType.ARRAY
    )
    values_by_group: dict[str, list[GlobalExtract]]


class KanidmStateSystemOauthClaimModel(
    HomelabRootModel[
        KanidmStateSystemOauthClaimUserModel | KanidmStateSystemOauthClaimFullModel
    ]
):
    def to_full_model(
        self, kanidm_state: KanidmStateConfig
    ) -> KanidmStateSystemOauthClaimFullModel:
        from .....config.state.person import KanidmStatePersonConfig

        root = self.root

        if isinstance(root, KanidmStateSystemOauthClaimUserModel):
            match root.user:
                case KanidmStateSystemOauthClaimUserType.USERNAME:
                    return KanidmStateSystemOauthClaimFullModel(
                        values_by_group={
                            KanidmStatePersonConfig.to_group_name(person): [
                                GlobalExtract.from_simple(person)
                            ]
                            for person in kanidm_state.persons.root.keys()
                        }
                    )
        else:
            return root

    def build(self, kanidm_state: KanidmStateConfig) -> Self:
        return self.__class__(self.to_full_model(kanidm_state))
