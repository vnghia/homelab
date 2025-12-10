from homelab_extract.plain import PlainArgs
from homelab_secret.resource import SecretResource
from pulumi import ComponentResource, Output, ResourceOptions

from .. import ResticConfig
from ..model import ResticRepositoryModel
from .repository import ResticRepositoryResource


class ResticRepository(ComponentResource):
    def __init__(
        self,
        name: str,
        repository: ResticRepositoryModel,
        *,
        opts: ResourceOptions | None,
        secret_resource: SecretResource,
        plain_args: PlainArgs,
    ) -> None:
        super().__init__(name, name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.keep = repository.keep
        self.repository = repository.build_repository(plain_args)
        self.password = repository.password.build_resource(
            "password", self.child_opts, secret_resource, plain_args
        )
        self.envs = repository.build_envs(plain_args)

        self.resource = ResticRepositoryResource(
            name,
            opts=self.child_opts,
            envs={
                "RESTIC_REPOSITORY": Output.from_input(self.repository),
                "RESTIC_PASSWORD": self.password.result,
            }
            | {k: Output.from_input(v) for k, v in self.envs.items()},
        )

        self.register_outputs({})


class ResticResource(ComponentResource):
    RESOURCE_NAME = "restic"

    def __init__(
        self,
        config: ResticConfig,
        *,
        opts: ResourceOptions | None,
        secret_resource: SecretResource,
        plain_args: PlainArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.restic = {
            name: ResticRepository(
                name,
                model,
                opts=self.child_opts,
                secret_resource=secret_resource,
                plain_args=plain_args,
            )
            for name, model in config.repositories.items()
        }

        self.register_outputs({})

    def __getitem__(self, key: str) -> ResticRepository:
        return self.restic[key]
