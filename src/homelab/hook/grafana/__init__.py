import dataclasses
import os
from pathlib import Path
from typing import ClassVar

import orjson
import pulumiverse_grafana as grafana
import yaml_rs
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from pulumi import ResourceOptions


@dataclasses.dataclass
class Folder:
    DASHBOARD_FOLDER: ClassVar[str] = "dashboard"

    path: Path | None
    resource: grafana.oss.Folder | None

    @classmethod
    def path_to_uid(cls, path: Path) -> str:
        return path.with_suffix("").as_posix().replace("/", "-")

    def provision(self, grafana_folder: Path, grafana_opts: ResourceOptions) -> None:
        opts = ResourceOptions.merge(
            grafana_opts, ResourceOptions(parent=self.resource or None)
        )

        path = grafana_folder / self.path if self.path else grafana_folder
        for file in os.listdir(path):
            full_path = path / file
            if not full_path.is_dir():
                continue

            relative_sub_path = self.path / file if self.path else Path(file)

            if file == self.DASHBOARD_FOLDER:
                for config_path in full_path.glob("*.yaml"):
                    dashboard_uid = self.path_to_uid(
                        relative_sub_path.parent / config_path.name
                    )
                    with open(config_path, "r+b") as config_file:
                        config = yaml_rs.load(config_file)
                        if not isinstance(config, dict):
                            raise ValueError(
                                "Grafana config should contain only one object"
                            )

                        config["metadata"] = {"name": dashboard_uid}
                        for link in config["spec"].get("links", []):
                            link_path = link.pop("path", None)
                            if link_path:
                                link["url"] = "/d/{}".format(
                                    self.path_to_uid(
                                        relative_sub_path.parent / link_path
                                    )
                                )

                        grafana.oss.Dashboard(
                            dashboard_uid,
                            opts=opts,
                            config_json=orjson.dumps(config).decode(),
                            folder=self.resource.uid if self.resource else None,
                        )
            else:
                relative_sub_path_uid = self.path_to_uid(relative_sub_path)
                resource = grafana.oss.Folder(
                    file,
                    opts=opts,
                    parent_folder_uid=self.resource.uid if self.resource else None,
                    title=file.capitalize(),
                    uid=relative_sub_path_uid,
                )
                Folder(path=relative_sub_path, resource=resource).provision(
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
    Folder(path=None, resource=None).provision(grafana_folder, grafana_opts)
