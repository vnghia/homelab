import typing

from homelab_docker.resource.file import FileResource
from pulumi import ComponentResource, Input, ResourceOptions

if typing.TYPE_CHECKING:
    from .. import VectorService


class VectorEnrichmentTableResource(ComponentResource):
    RESOURCE_NAME = "enrichment"

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        content: Input[str],
        schema: dict[str, str],
        vector_service: VectorService,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, resource_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.path = vector_service.config_dir / "enrichment" / f"{resource_name}.csv"

        self.table = FileResource(
            f"{resource_name}-table",
            opts=self.child_opts,
            volume_path=self.path,
            content=content,
            permission=vector_service.user,
            extractor_args=vector_service.extractor_args,
        )

        from . import VectorConfigData, VectorConfigResource

        self.config = VectorConfigResource(
            f"{resource_name}-enrichment",
            opts=self.child_opts,
            config_data=VectorConfigData(
                keys={},
                sources={},
                transforms={},
                sinks={},
                enrichment_tables={
                    resource_name: {
                        "type": "file",
                        "file": {
                            "encoding": {"type": "csv"},
                            "path": self.path.to_path(vector_service.extractor_args),
                        },
                        "schema": schema,
                    }
                },
            ),
            vector_service=vector_service,
        )
