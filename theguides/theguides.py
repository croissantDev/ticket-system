# plugins/test_plugin.py

from discord.ext import commands

class TestPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meow(self, ctx):
        await ctx.send("meow!")

def setup(bot):
    bot.add_cog(TestPlugin(bot))
