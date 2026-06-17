from hatchet_sdk import Context
from hatchet_sdk.utils.typing import LogLevel
from hatchet_sdk.worker.runner.utils.capture_logs import LogRecord


def log_to_server(
    context: Context,
    message: str,
    level: LogLevel = LogLevel.INFO,
) -> None:
    context.log_sender.publish(
        record=LogRecord(
            message=message,
            step_run_id=context.step_run_id,
            level=level,
            task_retry_count=context.retry_count,
        )
    )
