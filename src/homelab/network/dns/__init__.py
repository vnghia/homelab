from pulumi import ComponentResource, ResourceOptions


class Dns(ComponentResource):
    RESOURCE_NAME = "dns"

    def __init__(self) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)
