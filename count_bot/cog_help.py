from discord.ext import commands


class CountbotHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)


class HelpCommands(commands.Cog, name='Help Commands'):
    """Shows info about commands"""

    def __init__(self, bot):
        self.bot = bot
        bot.help_command = CountbotHelpCommand()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(HelpCommands(bot))
