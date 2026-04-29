import datetime
import logging
import os
from typing import Self

import docker
import pyotp
from docker.models.containers import Container
from pyrate_limiter import Duration, Limiter, Rate
from pythonjsonlogger.json import JsonFormatter
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
)

TOTP_KEY = "WINTELE_TOTP"
CONTAINER_KEY = "WINTELE_CONTAINER"

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
handler = logging.StreamHandler()
handler.setFormatter(
    JsonFormatter(
        "{levelname}{name}{asctime}{message}",
        style="{",
        rename_fields={"levelname": "level"},
    )
)
logger.addHandler(handler)


class BotData:
    CONTAINER_START_TIMEOUT = 120.0

    def __init__(self) -> None:
        self.limiter = Limiter(Rate(5, Duration.MINUTE))
        self.totp = pyotp.TOTP(os.environ[TOTP_KEY])
        self.container = docker.from_env().containers.get(os.environ[CONTAINER_KEY])


class BotContext(CallbackContext[ExtBot[None], None, None, BotData]):
    def __init__(
        self,
        application: Application[ExtBot[None], Self, None, None, BotData, None],
        chat_id: int | None = None,
        user_id: int | None = None,
    ) -> None:
        super().__init__(application, chat_id, user_id)

    @property
    def totp(self) -> pyotp.TOTP:
        return self.bot_data.totp

    @property
    def container(self) -> Container:
        return self.bot_data.container


async def post_init(
    application: Application[ExtBot[None], BotContext, None, None, BotData, None],
) -> None:
    await application.bot.set_my_commands(
        [
            ("on", "Turn the machine on. Usage: /on <totp>"),
            ("off", "Turn the machine off. Usage: /off <totp>"),
        ]
    )


async def on(update: Update, context: BotContext) -> None:
    if update.effective_message is None:
        logger.error("No effective message found. This is a bug in python-telegram-bot")
        return

    if not context.bot_data.limiter.try_acquire(str(update.effective_message.chat_id)):
        logger.info(f"User {update.effective_message.from_user} has been rate-limited")
        await update.effective_message.reply_text(
            "You have been rate-limited. Please try again later"
        )
        return

    if context.args is None:
        await update.effective_message.reply_text("Usage: /on <totp>")
        return

    totp = context.args[0]
    success = context.totp.verify(totp)
    if success:
        logger.info(
            f"On request from user {update.effective_message.from_user} is accepted"
        )

        container = context.bot_data.container
        container.reload()
        if container.status == "running":
            await update.effective_message.reply_text("The machine has been turned on")
        else:
            await update.effective_message.reply_text("Turning on the machine ...")
            container.start()

            now = datetime.datetime.now()
            for log in container.logs(stream=True, follow=True, since=now):
                if b"Windows started succesfully" in log:
                    await update.effective_message.reply_text(
                        "The machine has been turned on"
                    )
                    break
                if (
                    datetime.datetime.now() - now
                ).total_seconds() >= BotData.CONTAINER_START_TIMEOUT:
                    await update.effective_message.reply_text(
                        "Could not turn on the machine"
                    )
                    break

        container.start()
    else:
        await update.effective_message.reply_text("Request denied")


async def off(update: Update, context: BotContext) -> None:
    if update.effective_message is None:
        logger.error("No effective message found. This is a bug in python-telegram-bot")
        return

    if not context.bot_data.limiter.try_acquire(str(update.effective_message.chat_id)):
        logger.info(f"User {update.effective_message.from_user} has been rate-limited")
        await update.effective_message.reply_text(
            "You have been rate-limited. Please try again later"
        )
        return

    if context.args is None:
        await update.effective_message.reply_text("Usage: /off <totp>")
        return

    totp = context.args[0]
    success = context.totp.verify(totp)
    if success:
        logger.info(
            f"Off request from user {update.effective_message.from_user} is accepted"
        )

        await update.effective_message.reply_text("Turning off the machine ...")
        container = context.bot_data.container
        container.reload()
        container.stop()
        await update.effective_message.reply_text("The machine has been turned off")
    else:
        await update.effective_message.reply_text("Request denied")


def main() -> None:
    context_types = ContextTypes(context=BotContext, bot_data=BotData)
    application = (
        ApplicationBuilder()
        .token(os.environ["WINTELE_TOKEN"])
        .context_types(context_types)
        .post_init(post_init)
        .build()
    )
    application.add_handler(CommandHandler("on", on, block=True))
    application.add_handler(CommandHandler("off", off, block=True))
    application.run_polling()


if __name__ == "__main__":
    main()
