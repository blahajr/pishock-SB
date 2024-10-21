import logging
import os
import json
import sys
from dotenv import load_dotenv
import asyncio
from discord.ext.commands import Bot


logger = logging.getLogger("SB")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    file_handler = logging.FileHandler("bot_log.log")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


# Redirects stdout and stderr
class LoggerStream:
    def write(self, message):
        if message.strip():
            logger.info(message.strip())

    def flush(self):
        pass


sys.stdout = LoggerStream()
sys.stderr = LoggerStream()


class Shock(Bot):
    WORDLIST_FILE = "wordlist.json"
    WHITELIST_FILE = "whitelist.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def load_cogs_from_dir(self, directory):
        """Load all cogs."""
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        logger.info(f"{len(self.cogs)} Cogs have been loaded")

    async def on_ready(self):
        logger.info(f"Logged on as {self.user}")
        await self.load_cogs_from_dir("cogs")

    def load_json(self, file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error loading JSON: {e}")
            return None
        except FileNotFoundError:
            logger.error(f"Error: File {file_path} not found.")
            return None


async def start_bot():
    """Start the bot and handle username caching."""
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("Error: No token found in .env file.")
        return

    bot = Shock(
        command_prefix=">", self_bot=True
    )  # Technically can work as a normal bot too

    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(start_bot())
