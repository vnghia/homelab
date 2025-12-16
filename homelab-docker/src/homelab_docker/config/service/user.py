from __future__ import annotations

import typing

from homelab_pydantic import HomelabRootModel

from ...model.user import UidGidModel

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class ServiceUserConfig(HomelabRootModel[str | None | UidGidModel]):
    root: str | UidGidModel | None = None

    def model(self, extractor_args: ExtractorArgs) -> UidGidModel:
        root = self.root
        if isinstance(root, UidGidModel):
            return root
        return extractor_args.host_model.users[root]
