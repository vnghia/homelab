import pulumi
from homelab_config import config
from pulumi import ComponentResource, ResourceOptions


class Network(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(self, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.networks = {
            name: model.build_resource(resource_name=name, opts=self.child_opts)
            for name, model in config.docker.networks.bridge.items()
        }
        for name, network in self.networks.items():
            pulumi.export("network-{}".format(name), network.name)

        self.register_outputs(
            {name: network.name for name, network in self.networks.items()}
        )
