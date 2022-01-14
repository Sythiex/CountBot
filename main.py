import os
import discord
from discord import AllowedMentions
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), case_insensitive=True)
bot.allowed_mentions = AllowedMentions.all()
bot.author_id = 194922571584634883
bot.admin_role_id = 194927736240865281


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='goons learn to count'))

extensions = [
    'cog_parties',
    'cog_misc',
    'cog_dev'
]

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)

bot.run(os.getenv('token'))
