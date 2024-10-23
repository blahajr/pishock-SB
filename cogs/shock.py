import json
import logging
import os

from main import Shock
from pishock import PiShockAPI
from discord.ext import commands
from dotenv import load_dotenv


class Shocker(commands.Cog):

    def __init__(self, bot: Shock):
        self.bot = bot
        load_dotenv()
        self.shocker_apikey = os.getenv("SHOCKER_APIKEY")
        self.shocker_username = os.getenv("SHOCKER_USERNAME")
        self.shocker_code = os.getenv("SHOCKER_CODE")
        self.shock_api = None

    async def init_shocker(self):
        if not (self.shocker_apikey and self.shocker_username and self.shocker_code):
            logging.error("Error: Shocker API data not set.")
            return
        self.shock_api = PiShockAPI(self.shocker_username, self.shocker_apikey)
        logging.info("Shocker API initialized.")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.init_shocker()

    WORDLIST_FILE = "wordlist.json"
    WHITELIST_FILE = "whitelist.json"

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

    @commands.Cog.listener()
    async def on_message(self, message):
        """handles the shocker custom messages"""

        data = self.load_json(self.WHITELIST_FILE)
        whitelist = data.get("whitelist", []) if data else []
        if message.author.id not in whitelist:
            return

        wordlist = self.load_json(self.WORDLIST_FILE)
        if not wordlist:
            return

        if any(word in message.content.lower() for word in wordlist.get("words", [])):
            await self.shock_message(self, message)

    async def shock_message(self, ctx, message: str):

        wordlist = self.load_json(self.WORDLIST_FILE)

        if wordlist and [0] not in wordlist.get("words", []):
            return

        if len(message) < 3:
            await ctx.channel.send(
                "```Error: Invalid message format! Expected format: (word) (shock value) (duration) ex. shock 10 5```"
            )
            return

        try:
            shock_value, duration = int(message[1]), int(message[2])
            if not (1 <= shock_value <= 100) or not (1 <= duration <= 15):
                raise ValueError

            await self.send_shock(ctx, duration, shock_value)

        except ValueError:
            await ctx.channel.send(
                "```Error: Invalid format. Ensure shock (1-100) and duration (1-15).```"
            )

    @commands.command(name="setshocker")
    async def set_shocker(self, ctx, apikey: str, code: str):
        """sets your shocker configuration"""
        os.environ["SHOCKER_APIKEY"] = apikey
        os.environ["SHOCKER_CODE"] = code

        with open(".env", "a") as f:
            f.write(f"SHOCKER_APIKEY={apikey}\nSHOCKER_CODE={code}\n")

        await ctx.channel.send("```Shocker API key and code set successfully!```")

    @commands.command(name="username")
    async def set_username(self, ctx, username: str):
        os.environ["SHOCKER_USERNAME"] = username
        with open(".env", "a") as f:
            f.write(f"SHOCKER_USERNAME={username}\n")

        await ctx.channel.send(f"```Username `{username}` set successfully!```")

    @commands.command()
    async def shocker(self, ctx):
        apikey = os.getenv("SHOCKER_APIKEY")
        code = os.getenv("SHOCKER_CODE")
        username = os.getenv("SHOCKER_USERNAME")

        if not all([apikey, code, username]):
            await ctx.channel.send(
                "```Error: API key, code, or username not set! Set them with `>set <Apikey> <Code>` and or `>setusername <username>```"
            )
            return

        await ctx.channel.send(
            f"```API Key: {apikey}\nCode: {code}\nUsername: {username}```"
        )

    @commands.command()
    async def help1(self, ctx):
        await ctx.channel.send(
            "```Commands:\n>ping\n>setshocker <Apikey> <Code>\n>setusername <username>\n>shocker\n>help\n>add <word>\n>remove_word <word>\n>status <type> <status> (type: 1 - Game, 2 - Streaming, 3 - Listening, 4 - Watching)\n>banner <user/id>\n>pfp <user/id>```"
        )

    @commands.command(name="add")
    async def add_word(self, ctx, word: str):
        wordlist = self.load_json(self.WORDLIST_FILE) or {"words": []}
        if word in wordlist["words"]:
            await ctx.channel.send(f"```Word `{word}` is already in the list.```")
            return

        wordlist["words"].append(word)
        self.save_json(self.WORDLIST_FILE, wordlist)

        await ctx.channel.send(f"```Word `{word}` has been added!```")

    @commands.command()
    async def remove_word(self, ctx, word: str):
        """removes word from the custom list"""

        wordlist = self.load_json(self.WORDLIST_FILE) or {"words": []}

        if word not in wordlist["words"]:
            await ctx.channel.send(f"```Error: Word `{word}` is not in the list.```")
            return

        wordlist["words"].remove(word)
        self.save_json(self.WORDLIST_FILE, wordlist)

        await ctx.channel.send(f"```Word `{word}` has been removed!```")

    @commands.command()
    async def test(self, ctx, duration: int, intensity: int):
        """test the shock"""

        await self.send_shock(ctx, duration, intensity)

    async def send_shock(self, ctx, duration: int, intensity: int) -> None:
        """Sends a shock."""
        if not self.shock_api:
            await ctx.channel.send("```Error: Shocker API not initialized!```")
            return

        if not (1 <= intensity <= 100):
            await ctx.channel.send("```Error: Intensity must be between 1 and 100.```")
            return

        try:
            if self.shocker_code:
                self.shock_api.shocker(self.shocker_code).shock(
                    duration=duration, intensity=intensity
                )
            else:
                await ctx.channel.send("```Error: Shocker code is not set!```")
            await ctx.channel.send(
                f"```Shock sent with duration: {duration}s and intensity: {intensity}```"
            )
        except Exception as e:
            await ctx.channel.send(f"```Error: {str(e)}```")


async def setup(bot: Shock):
    await bot.add_cog(Shocker(bot))
