import discord
from discord.ext import commands


class DevCommands(commands.Cog, name='Dev Commands'):
    """Developer Commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.id == self.bot.author_id

    @commands.command(aliases=['lc'])
    async def listcogs(self, ctx):
        """Returns a list of all enabled cogs."""
        base_string = "```css\n"
        base_string += "\n".join([str(cog) for cog in self.bot.extensions])
        base_string += "\n```"
        await ctx.send(base_string)

    @commands.command(aliases=['rl'])
    async def reload(self, ctx, cog):
        """Reloads a cog."""
        extensions = self.bot.extensions
        if cog == 'all':
            for extension in extensions:
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            await ctx.send('Done')
        if cog in extensions:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
            await ctx.send('Done')
        else:
            await ctx.send('Unknown Cog')

    @commands.command()
    async def load(self, ctx, cog):
        """Loads a cog."""
        try:
            self.bot.load_extension(cog)
            await ctx.send(f"`{cog}` has successfully been loaded.")
        except discord.ExtensionNotFound:
            await ctx.send(f"`{cog}` does not exist!")

    @commands.command(aliases=['ul'])
    async def unload(self, ctx, cog):
        """Unload a cog."""
        extensions = self.bot.extensions
        if cog not in extensions:
            await ctx.send("Cog is not loaded!")
            return
        self.bot.unload_extension(cog)
        await ctx.send(f"`{cog}` has successfully been unloaded.")


def setup(bot):
    bot.add_cog(DevCommands(bot))
