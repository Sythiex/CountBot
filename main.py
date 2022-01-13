import os
import discord
from cog_parties import PartyCommands
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), case_insensitive=True)
bot.author_id = 194922571584634883
bot.admin_role_id = 194927736240865281


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='goons learn to count'))


bot.add_cog(PartyCommands(bot))

bot.run(os.getenv('token'))
