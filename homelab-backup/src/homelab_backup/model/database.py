import dataclasses


@dataclasses.dataclass
class ServiceDatabaseBackupProfileModel:
    name: str
    backup_: str | None = None

    @property
    def backup(self) -> str:
        return self.backup_ or self.name
