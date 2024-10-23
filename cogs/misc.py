import time
from main import Shock

from discord.ext import commands
import discord


class Misc(commands.Cog):
    def __init__(self, bot: Shock):
        self.bot = bot

    @commands.command(name="status")
    async def set_status(self, ctx, type: int, *, status: str):
        """Set your status."""

        if not status:
            await ctx.channel.send(
                "```Error: Status cannot be empty. Provide a valid status.```"
            )
            return

        try:
            if type == 1:
                await self.bot.change_presence(activity=discord.Game(name=status))
                await ctx.channel.send(f"```Status set to '{status}' (type: game).```")
            elif type == 2:
                await self.bot.change_presence(
                    activity=discord.Streaming(
                        url="https://twitch.tv/meow", name=status
                    )
                )
                await ctx.channel.send(
                    f"```Status set to '{status}' (type: streaming).```"
                )
            elif type == 3:
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.listening, name=status
                    )
                )
                await ctx.channel.send(
                    f"```Status set to '{status}' (type: listening).```"
                )
            elif type == 4:
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching, name=status
                    )
                )
                await ctx.channel.send(
                    f"```Status set to '{status}' (type: watching).```"
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
    async def banner(self, ctx, user: discord.User):
        """Displays a user's banner."""
        if user.banner:
            await ctx.channel.send(user.banner.url)
        else:
            await ctx.channel.send("```Error: User does not have a banner set.```")

    @commands.command()
    async def pfp(self, ctx, user: discord.User):
        """Displays a user's profile picture."""
        if user.avatar:
            await ctx.channel.send(user.avatar.url)
        else:
            await ctx.channel.send("```Error: User does not have an avatar set.```")

    @commands.command()
    async def ping(self, ctx):
        """Measures bot latency."""
        await ctx.message.delete()
        before = time.monotonic()
        message = await ctx.send("Pinging...")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"`{int(ping)} ms`")

    @commands.command()
    async def shutdown(self, ctx):
        """Shuts down the bot."""
        await ctx.send("Shutting down...")
        await self.bot.close()


async def setup(bot: Shock):
    await bot.add_cog(Misc(bot))
