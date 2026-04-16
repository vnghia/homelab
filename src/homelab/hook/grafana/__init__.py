import dataclasses
import os
from pathlib import Path

import pulumiverse_grafana as grafana
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from pulumi import ResourceOptions


@dataclasses.dataclass
class Folder:
    path: Path | None
    resource: grafana.oss.Folder | None

    def provision_subfolder(
        self, grafana_folder: Path, grafana_opts: ResourceOptions
    ) -> None:
        opts = ResourceOptions.merge(
            grafana_opts, ResourceOptions(parent=self.resource or None)
        )

        path = grafana_folder / self.path if self.path else grafana_folder
        for folder in os.listdir(path):
            subpath = self.path / folder if self.path else Path(folder)
            resource = grafana.oss.Folder(
                folder,
                opts=opts,
                parent_folder_uid=self.resource.uid if self.resource else None,
                title=folder.capitalize(),
                uid=subpath.as_posix().replace("/", "-"),
            )
            Folder(path=subpath, resource=resource).provision_subfolder(
                grafana_folder, grafana_opts
            )


def pre_build(service: ExtraService[ExtraConfig]) -> None:
    pass


def post_build(service: ExtraService[ExtraConfig]) -> None:
    grafana_opts = ResourceOptions.merge(
        service.child_opts,
        ResourceOptions(
            providers={
                "grafana": grafana.Provider(
                    service.name(),
                    opts=service.child_opts,
                    auth=service.extract_variable_str("AUTH"),
                    url=service.extract_variable_str("URL"),
                ),
            }
        ),
    )

    grafana_folder = (
        Path(__file__).parent.parent.parent.parent.parent / "config" / "grafana"
    ).resolve(True)
    Folder(path=None, resource=None).provision_subfolder(grafana_folder, grafana_opts)
