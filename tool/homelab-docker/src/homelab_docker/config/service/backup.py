from homelab_pydantic import HomelabBaseModel
from homelab_restic.model.frequency import BackupFrequency


class ServiceBackupConfig(HomelabBaseModel):
    frequency: BackupFrequency = BackupFrequency.DAILY
