import inflect
from discord import ApplicationContext, Option
from discord.ext import commands

guilds = [
    194927673372442624,  # RELEASE THE KEKEN
    928771354914873345  # Test
]


class MiscCommands(commands.Cog, name='Misc Commands'):
    """Memes and yokes"""

    def __init__(self, bot):
        self.bot = bot
        self.inflect_engine = inflect.engine()
        self.pat_count = 0
        self.last_pat_message = None

    @commands.slash_command(guild_ids=guilds)
    async def pat(self, ctx: ApplicationContext, number: Option(int, 'The number of times to pat', required=False, default=1)):
        """Pat CountBot"""
        if self.last_pat_message is not None:
            await self.last_pat_message.delete()
        self.pat_count += number
        await ctx.interaction.response.send_message(f"{self.inflect_engine.number_to_words(self.pat_count).capitalize()} {'pat' if self.pat_count == 1 else 'pats'}, ha ha ha!")
        message_id = (await ctx.interaction.original_message()).id
        self.last_pat_message = await ctx.fetch_message(message_id)

        print(f'patter: {ctx.author}')


def setup(bot):
    bot.add_cog(MiscCommands(bot))
