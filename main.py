import logging
import os
import sys
import discord
import json
from pishock import PiShockAPI
from dotenv import load_dotenv
import asyncio


if os.path.exists("bot_log.log"):  # Clears the log file each startup
    os.remove("bot_log.log")

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("bot_log.log")],
)


# just redirects stdout and stderr to the logger aka terminal output
class LoggerStream:
    def write(self, message):

        if message.strip():
            logging.info(message.strip())

    def flush(self):
        pass


sys.stdout = LoggerStream()
sys.stderr = LoggerStream()


class Client(discord.Client):
    WORDLIST_FILE = "wordlist.json"
    WHITELIST_FILE = "whitelist.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shock_api = None
        # prob a better way to do this
        self.command_map = {
            ">ping": self.ping,
            ">setshocker": self.set_shocker,
            ">setusername": self.set_username,
            ">shocker": self.display_shocker,
            ">help": self.show_help,
            ">word": self.add_word,
            ">word_remove": self.remove_word,
            ">test": self.test_shocker,
            ">status": self.set_status,
            ">banner": self.banner,
            ">pfp": self.pfp,
        }
        load_dotenv()
        self.shocker_apikey = os.getenv("SHOCKER_APIKEY")
        self.shocker_username = os.getenv("SHOCKER_USERNAME")
        self.shocker_code = os.getenv("SHOCKER_CODE")

    async def init_shocker(self):

        if (
            not self.shocker_apikey
            or not self.shocker_username
            or not self.shocker_code
        ):
            return logging.error("Error: Shocker API data not set.")

        self.shock_api = PiShockAPI(self.shocker_username, self.shocker_apikey)
        return

    async def on_ready(self):

        logging.info(f"Logged on as {self.user}")
        await self.init_shocker()

        if self.shock_api:
            logging.info("Shocker API initialized.")

    def load_json(self, file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error loading JSON: {e}")
            return None
        except FileNotFoundError:
            logging.error(f"Error: File {file_path} not found.")
            return None

    def save_json(self, filename: str, data: dict | list) -> None:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    async def on_message(self, ctx):
        # can change to not dms if need in guilds i guess
        if ctx.channel.type != discord.ChannelType.private or ctx.content.strip() == "":
            return

        data = self.load_json(self.WHITELIST_FILE)
        whitelist = data.get("whitelist", []) if data else []
        if ctx.author == self.user:
            command = ctx.content.strip().split()[0].lower()
            if command in self.command_map:
                await self.handle_commands(ctx)

        if ctx.author.id not in whitelist or ctx.author == self.user:
            return

        await self.shock_message(ctx)

    async def shock_message(self, ctx):
        parts = ctx.content.split()
        wordlist = self.load_json(self.WORDLIST_FILE)

        if wordlist and parts[0] not in wordlist.get("words", []):
            return

        if len(parts) < 3:
            await ctx.channel.send(
                "```Error: Invalid message format! Expected format: (word) (shock value) (duration) ex. shock 10 5```"
            )
            return

        try:
            shock_value, duration = int(parts[1]), int(parts[2])
            if not (1 <= shock_value <= 100) or not (1 <= duration <= 15):
                raise ValueError

            await self.send_shock(ctx, duration, shock_value)

        except ValueError:
            await ctx.channel.send(
                "```Error: Invalid format. Ensure shock (1-100) and duration (1-15).```"
            )

    async def handle_commands(self, ctx):
        command = (
            ctx.content.strip().split()[0].lower() if ctx.content.strip() else None
        )

        command_map = self.command_map
        if command in command_map:
            await command_map[command](ctx)

    async def ping(self, ctx):
        await ctx.channel.send(f"Pong! {round(self.latency * 1000)}ms")

    async def set_shocker(self, ctx):
        try:
            _, apikey, code = ctx.content.split(" ")

            os.environ["SHOCKER_APIKEY"] = apikey
            os.environ["SHOCKER_CODE"] = code

            with open(".env", "a") as f:
                f.write(f"SHOCKER_APIKEY={apikey}\nSHOCKER_CODE={code}\n")

            await ctx.channel.send("```Shocker API key and code set successfully!```")
        except ValueError:
            await ctx.channel.send(
                "```Error: Invalid format! Usage: >setshocker <Apikey> <Code>```"
            )

    async def set_username(self, ctx):
        try:
            _, username = ctx.content.split(" ")

            os.environ["SHOCKER_USERNAME"] = username

            with open(".env", "a") as f:
                f.write(f"SHOCKER_USERNAME={username}\n")

            await ctx.channel.send(f"```Username `{username}` set successfully!```")
        except ValueError:
            await ctx.channel.send(
                "```Invalid format! Usage: >setusername <username>```"
            )

    async def display_shocker(self, ctx):
        apikey, code, username = (
            os.getenv("SHOCKER_APIKEY"),
            os.getenv("SHOCKER_CODE"),
            os.getenv("SHOCKER_USERNAME"),
        )

        if not all([apikey, code, username]):
            await ctx.channel.send(
                "```Error: API key, code, or username not set! Set them with `>setshocker <Apikey> <Code>` and or `>setusername <username>```"
            )
            return

        await ctx.channel.send(
            f"```API Key: {apikey}\nCode: {code}\nUsername: {username}```"
        )

    async def show_help(self, ctx):
        await ctx.channel.send(
            "```Commands:\n>ping\n>setshocker <Apikey> <Code>\n>setusername <username>\n>shocker\n>help\n>word <word>\n>word_remove\n>status <type> <status> (type: 1 - Game, 2 - Streaming, 3 - Listening, 4 - Watching)\n>banner <user/id>\n>pfp <user/id>```"
        )

    async def add_word(self, ctx):
        try:
            _, word = ctx.content.split(" ")
            wordlist = self.load_json(self.WORDLIST_FILE) or {"words": []}

            if word in wordlist["words"]:
                await ctx.channel.send(f"```Word `{word}` is already in the list.```")
                return
            wordlist["words"].append(word)
            self.save_json(self.WORDLIST_FILE, wordlist)

            await ctx.channel.send(f"```Word `{word}` has been added!```")

        except ValueError:
            await ctx.channel.send("```Error: Invalid format! Use: `>word <word>` ```")

    async def remove_word(self, ctx):
        try:
            _, word = ctx.content.split(" ")
            wordlist = self.load_json(self.WORDLIST_FILE) or []

            if word not in wordlist:
                await ctx.channel.send(
                    f"```Error: Word `{word}` is not in the list.```"
                )
                return

            wordlist.remove(word)
            self.save_json(self.WORDLIST_FILE, wordlist)

            await ctx.channel.send(f"```Word `{word}` has been removed!```")
        except ValueError:
            await ctx.channel.send(
                "```Error: Invalid format! Use: `>word_remove <word>` ```"
            )

    async def test_shocker(self, ctx):
        try:
            _, duration, intensity = ctx.content.split(" ")
            await self.send_shock(ctx, int(duration), int(intensity))
        except ValueError:
            await ctx.channel.send(
                "```Error: Invalid format! Use: `>test <duration> <intensity>` ```"
            )

    async def set_status(self, ctx):
        """Set your status."""

        parts = ctx.content.split()
        if len(parts) < 3:
            await ctx.channel.send(
                "```Error: Invalid format! Use: >status <type> <status>```"
            )
            return

        try:
            type = int(parts[1])
            status = " ".join(parts[2:])

            if not status:
                await ctx.channel.send(
                    "```Error: Status cannot be empty. Provide a valid status.```"
                )
                return

            if type == 1:
                await self.change_presence(activity=discord.Game(name=status))
                await ctx.chanel.send(
                    f"```Status set successfully! to {status} and type game```"
                )
            elif type == 2:
                await self.change_presence(
                    activity=discord.Streaming(
                        url="https://twitch.tv/meow", name=status
                    )
                )
                await ctx.chanel.send(
                    f"```Status set successfully! to {status} and type streaming```"
                )
            elif type == 3:
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.listening, name=status
                    )
                )
                await ctx.chanel.send(
                    f"```Status set successfully! to {status} and type listening```"
                )
            elif type == 4:
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching, name=status
                    )
                )
                await ctx.chanel.send(
                    f"```Status set successfully! to {status} and type watching```"
                )
            else:
                await ctx.channel.send(
                    "```Error: Invalid type! Use a valid type:\n1 - Game\n2 - Streaming\n3 - Listening\n4 - Watching```"
                )
        except ValueError:
            await ctx.channel.send(
                "```Error: Type must be a number (1, 2, 3, or 4).```"
            )

    async def banner(self, ctx):
        """Displays a user's banner."""
        parts = ctx.content.split()

        if len(parts) < 2:
            await ctx.channel.send(
                "```Error: Please provide a valid user ID or mention.```"
            )
            return

        user_id = parts[1]

        if user_id.startswith("<@") and user_id.endswith(">"):
            user_id = user_id[2:-1]

            user = await self.fetch_user(user_id)

            if user.banner:
                await ctx.channel.send(user.banner.url)
            else:
                await ctx.channel.send("```Error: User does not have a banner set.```")

    async def pfp(self, ctx):
        """Displays a user's pfp."""
        parts = ctx.content.split()

        if len(parts) < 2:
            await ctx.channel.send(
                "```Error: Please provide a valid user ID or mention.```"
            )
            return

        user_id = parts[1]

        if user_id.startswith("<@") and user_id.endswith(">"):
            user_id = user_id[2:-1]

            user = await self.fetch_user(user_id)

            if user.avatar:
                await ctx.channel.send(user.avatar.url)
            else:
                await ctx.channel.send("```Error: User does not have an avatar set.```")

    async def send_shock(self, ctx, duration: int, intensity: int):
        """Sends a shock to the specified target."""
        if not self.shock_api:
            await ctx.channel.send("```Error: Shocker API not initialized!```")
            return

        apikey = os.getenv("SHOCKER_APIKEY")
        code = os.getenv("SHOCKER_CODE")
        username = os.getenv("SHOCKER_USERNAME")

        if not all([apikey, code, username]):
            await ctx.channel.send(
                "```Error: Invalid shocker data. Ensure API, code, and username are set.```"
            )
            return

        if code:
            self.shock_api.shocker(code).shock(duration=duration, intensity=intensity)
        else:
            await ctx.channel.send("```Error: Shocker code is not set.```")

        await ctx.channel.send(
            f"```Shock sent with duration: {duration}s and intensity: {intensity}```"
        )


async def start_bot():
    """Start the bot and handle username caching."""
    load_dotenv()
    token = os.getenv("TOKEN")
    if not token:
        logging.error("Error: No token found in .env file.")
        return
    client = Client()
    await client.start(token)


if __name__ == "__main__":
    asyncio.run(start_bot())
