from homelab_backup.model.frequency import BackupFrequency
from homelab_pydantic import HomelabBaseModel


class ServiceBackupConfig(HomelabBaseModel):
    frequency: BackupFrequency = BackupFrequency.DAILY
