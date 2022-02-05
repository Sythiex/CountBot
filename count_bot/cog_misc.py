import random

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
        print(f'{ctx.author} patted me {number} times')

    @commands.slash_command(guild_ids=guilds)
    async def roll(self, ctx: ApplicationContext,
                   dice: Option(str, "Format is 'XdY' where X is the number of dice to roll and Y is the size of the dice"),
                   modifier: Option(int, "Number added to the result of the roll", required=False, default=0)):
        """Roll some dice 🎲"""
        max_number_of_dice = 100
        max_die_size = 1000000000
        print(f'{ctx.author} rolled {dice} + {modifier}')
        # split the input and verify there are only 2 parts
        die_input_split = dice.lower().split('d')
        if len(die_input_split) != 2:
            await ctx.interaction.response.send_message(f"'{dice}' is not a valid input.", ephemeral=True)
            return
        # convert the parts into ints
        try:
            number_of_dice = int(die_input_split[0])
        except ValueError:
            if die_input_split[0] == '':  # if no number of dice is specified, assume 1
                number_of_dice = 1
            else:
                await ctx.interaction.response.send_message(f"'{die_input_split[0]}' is not an integer.", ephemeral=True)
                return
        try:
            die_size = int(die_input_split[1])
        except ValueError:
            await ctx.interaction.response.send_message(f"'{die_input_split[1]}' is not an integer.", ephemeral=True)
            return
        # keep numbers "sane"
        if number_of_dice > max_number_of_dice or number_of_dice < 1:
            await ctx.interaction.response.send_message(f"Number of dice must be between 1 and {max_number_of_dice}, got: {number_of_dice}", ephemeral=True)
            return
        if die_size > max_die_size or die_size < 1:
            await ctx.interaction.response.send_message(f"Size of dice must be between 1 and {max_die_size}, got: {die_size}", ephemeral=True)
            return
        # roll all the dice
        total = 0
        result_string = ''
        for i in range(number_of_dice):
            this_roll = random.randint(1, die_size)
            total = total + this_roll
            result_string += str(this_roll)
            if i != number_of_dice - 1:
                result_string += ' + '
        # add the modifier
        mod_str = ''
        if modifier != 0:
            total = total + modifier
            mod_str = f"{'-' if modifier < 0 else '+'} {abs(modifier)}"
            result_string += f" {'-' if modifier < 0 else '+'} *{abs(modifier)}*"  # uses italics to visually separate the mod from the rolls
        result_string += ' = '
        # hide result_string if there is no arithmetic to show (to avoid situations like '1 = 1')
        if number_of_dice == 1 and modifier == 0:
            result_string = ''
        await ctx.interaction.response.send_message(f"Rolled {number_of_dice}d{die_size} {mod_str}:\n{result_string}**{total}**")


def setup(bot):
    bot.add_cog(MiscCommands(bot))
