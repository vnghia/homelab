from typing import Any

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pulumi import Input


class DaguDagStepHttpExecutorModel(HomelabBaseModel):
    headers: dict[str, GlobalExtract] = {}
    query: dict[str, GlobalExtract] = {}
    body: GlobalExtract | None = None
    silent: bool = True

    def to_executor(
        self,
        main_service: ServiceResourceBase,
        _dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        return {
            "type": "http",
            "config": (
                (
                    {
                        "headers": {
                            k: GlobalExtractor(v).extract_str(main_service, None)
                            for k, v in self.headers.items()
                        }
                    }
                    if self.headers
                    else {}
                )
                | (
                    {
                        "query": {
                            k: GlobalExtractor(v).extract_str(main_service, None)
                            for k, v in self.query.items()
                        }
                    }
                    if self.query
                    else {}
                )
                | (
                    {"body": GlobalExtractor(self.body).extract_str(main_service, None)}
                    if self.body
                    else {}
                )
                | ({"silent": True} if self.silent else {})
            ),
        }
