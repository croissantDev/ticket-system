from discord.ext import commands

class TheGuides(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@commands.command()
async def ping(self, ctx):
    await ctx.send("pong!")

async def setup(bot):  # <-- must be async
    await bot.add_cog(TheGuides(bot))
