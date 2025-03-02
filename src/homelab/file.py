from pulumi import ComponentResource, ResourceOptions


class File(ComponentResource):
    RESOURCE_NAME = "file"

    def __init__(self) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.register_outputs({})
