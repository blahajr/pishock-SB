import time
from main import Shock

from discord.ext import commands
import discord


class Misc(commands.Cog):
    def __init__(self, bot: Shock):
        self.bot = bot

    @commands.command(name="status")
    async def set_status(self, ctx):
        """Set your status."""

        parts = ctx.content.split()
        if len(parts) < 3:
            await ctx.channel.send(
                "```Error: Invalid format! Use: >set_status <type> <status>```"
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
                await self.bot.change_presence(activity=discord.Game(name=status))
                await ctx.channel.send(
                    f"```Status set successfully! to {status} and type game```"
                )
            elif type == 2:
                await self.bot.change_presence(
                    activity=discord.Streaming(
                        url="https://twitch.tv/meow", name=status
                    )
                )
                await ctx.channel.send(
                    f"```Status set successfully! to {status} and type streaming```"
                )
            elif type == 3:
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.listening, name=status
                    )
                )
                await ctx.channel.send(
                    f"```Status set successfully! to {status} and type listening```"
                )
            elif type == 4:
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching, name=status
                    )
                )
                await ctx.channel.send(
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

    @commands.command()
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

            user = await self.bot.fetch_user(user_id)

            if user.banner:
                await ctx.channel.send(user.banner.url)
            else:
                await ctx.channel.send("```Error: User does not have a banner set.```")

    @commands.command()
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

            user = await self.bot.fetch_user(user_id)

            if user.avatar:
                await ctx.channel.send(user.avatar.url)
            else:
                await ctx.channel.send("```Error: User does not have an avatar set.```")

    @commands.command()
    async def ping(self, ctx):
        await ctx.message.delete()
        before = time.monotonic()
        message = await ctx.send("Pinging...")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"`{int(ping)} ms`")

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.close()


async def setup(bot: Shock):
    await bot.add_cog(Misc(bot))
