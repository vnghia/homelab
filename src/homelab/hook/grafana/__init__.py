import dataclasses
import os
from pathlib import Path

import orjson
import pulumiverse_grafana as grafana
import yaml_rs
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from pulumi import ResourceOptions


@dataclasses.dataclass
class Folder:
    path: Path | None
    resource: grafana.oss.Folder | None

    def provision(self, grafana_folder: Path, grafana_opts: ResourceOptions) -> None:
        opts = ResourceOptions.merge(
            grafana_opts, ResourceOptions(parent=self.resource or None)
        )

        path = grafana_folder / self.path if self.path else grafana_folder
        for file in os.listdir(path):
            full_path = path / file
            sub_path = self.path / file if self.path else Path(file)
            sub_path_posix = sub_path.with_suffix("").as_posix().replace("/", "-")

            if full_path.is_dir():
                resource = grafana.oss.Folder(
                    file,
                    opts=opts,
                    parent_folder_uid=self.resource.uid if self.resource else None,
                    title=file.capitalize(),
                    uid=sub_path.as_posix().replace("/", "-"),
                )
                Folder(path=sub_path, resource=resource).provision(
                    grafana_folder, grafana_opts
                )
            elif full_path.suffix == ".yaml":
                with open(full_path, "r+b") as config_file:
                    config = yaml_rs.load(config_file)
                    if not isinstance(config, dict):
                        raise ValueError(
                            "Grafana config should contain only one object"
                        )

                    kind = config["kind"]
                    match kind:
                        case "Dashboard":
                            dashboard_name = full_path.stem
                            config["metadata"] = {"name": sub_path_posix}
                            grafana.oss.Dashboard(
                                dashboard_name,
                                opts=opts,
                                config_json=orjson.dumps(config).decode(),
                                folder=self.resource.uid if self.resource else None,
                            )
                        case _:
                            raise ValueError(
                                "Unsupported grafana config kind: {}".format(kind)
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
