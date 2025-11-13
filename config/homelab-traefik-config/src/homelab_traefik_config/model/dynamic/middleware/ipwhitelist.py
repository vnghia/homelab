from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ..type import TraefikDynamicType


class TraefikDynamicMiddlewareIpWhitelistModel(HomelabBaseModel):
    DEFAULT_REJECT_STATUS_CODE: ClassVar[PositiveInt] = 404

    source_range: list[GlobalExtract]
    reject_status_code: PositiveInt = DEFAULT_REJECT_STATUS_CODE

    def to_data(
        self, type_: TraefikDynamicType, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        return {
            "ipAllowList": {
                "sourceRange": [
                    GlobalExtractor(source).extract_str(extractor_args)
                    for source in self.source_range
                ]
            }
            | (
                {"rejectStatusCode": self.reject_status_code}
                if type_ == TraefikDynamicType.HTTP
                else {}
            )
        }
