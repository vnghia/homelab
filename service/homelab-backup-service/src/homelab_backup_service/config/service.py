from homelab_pydantic import HomelabRootModel

from homelab_backup_service.model.service import BackupServiceModel


class BackupServiceConfig(HomelabRootModel[dict[str, BackupServiceModel]]):
    pass
