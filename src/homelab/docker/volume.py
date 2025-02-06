# import homelab_docker as docker
# import pulumi
# from homelab_config import config
# from pulumi import ComponentResource, ResourceOptions


# class Volume(ComponentResource):
#     RESOURCE_NAME = "volume"

#     def __init__(self, opts: ResourceOptions | None) -> None:
#         super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
#         self.child_opts = ResourceOptions(parent=self)

#         self.volumes = {
#             name: model.build_resource(name, opts=self.child_opts)
#             for name, model in config.docker.volumes.local.items()
#         }

#         for service_name, service in config.docker.services.items():
#             for name, model in service.databases.postgres.items():
#                 for version in model.versions:
#                     full_name = model.get_full_name_version(service_name, name, version)
#                     self.volumes[full_name] = docker.volume.Local(
#                         labels=config.PROJECT_LABELS
#                     ).build_resource(full_name, opts=self.child_opts)

#         for name, volume in self.volumes.items():
#             pulumi.export("volume-{}".format(name), volume.name)

#         self.register_outputs(
#             {name: volume.name for name, volume in self.volumes.items()}
#         )
