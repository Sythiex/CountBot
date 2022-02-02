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
                   dice_to_roll: Option(str, "Format is 'XdY' where X is the number of dice to roll and Y is the size of the dice"),
                   modifier: Option(int, "Number added to the result of the roll", required=False, default=0)):
        """Roll some dice 🎲"""
        print(f'{ctx.author} rolled {dice_to_roll} + {modifier}')
        # make sure the input contains 'd'
        dice_to_roll = dice_to_roll.lower()
        if 'd' not in dice_to_roll:
            await ctx.interaction.response.send_message(f"'{dice_to_roll}' is not a valid input.", ephemeral=True)
            return
        # split the input and verify there are only 2 parts
        die_input_split = dice_to_roll.split('d')
        if len(die_input_split) != 2:
            await ctx.interaction.response.send_message(f"'{dice_to_roll}' is not a valid input.", ephemeral=True)
            return
        # convert the parts into ints
        try:
            number_of_dice = int(die_input_split[0])
        except ValueError:
            await ctx.interaction.response.send_message(f"'{die_input_split[0]}' is not an integer.", ephemeral=True)
            return
        try:
            die_size = int(die_input_split[1])
        except ValueError:
            await ctx.interaction.response.send_message(f"'{die_input_split[1]}' is not an integer.", ephemeral=True)
            return
        # keep numbers "sane"
        if number_of_dice > 100 or number_of_dice < 1:
            await ctx.interaction.response.send_message(f"Number of dice must be between 1 and 100, got: {number_of_dice}", ephemeral=True)
            return
        if die_size > 1000000000 or die_size < 1:
            await ctx.interaction.response.send_message(f"Size of dice must be between 1 and 1000000000, got: {die_size}", ephemeral=True)
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
        # add the mod
        mod_str = ''
        if modifier != 0:
            total = total + modifier
            mod_str = f" {'-' if modifier < 0 else '+'} {abs(modifier)}"
            result_string += f" {'-' if modifier < 0 else '+'} *{abs(modifier)}*"  # uses italics to visually separate the mod from the rolls

        await ctx.interaction.response.send_message(f"Rolled {dice_to_roll}{mod_str}:\n{result_string} = **{total}**")


def setup(bot):
    bot.add_cog(MiscCommands(bot))
