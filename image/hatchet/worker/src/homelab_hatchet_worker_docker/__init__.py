from hatchet_sdk import Context, Hatchet
from homelab_hatchet_restic import ResticTask
from homelab_hatchet_restic.config import ResticConfig

hatchet = Hatchet()


@hatchet.task(input_validator=ResticConfig)
async def restic_debug(input: ResticConfig, ctx: Context) -> dict[str, str]:
    await ResticTask(input).debug()
    return {"task": "restic"}


def main() -> None:
    worker = hatchet.worker("worker", workflows=[restic_debug])
    worker.start()
