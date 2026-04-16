import pulumiverse_grafana as grafana
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from pulumi import ResourceOptions


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
