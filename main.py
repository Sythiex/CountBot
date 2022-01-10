import discord, inflect, os
from discord import Embed
from discord.ext import commands
from discord.ui import View

bot = commands.Bot(command_prefix="!", case_insensitive=True)
bot.author_id = 194922571584634883
views = []
inflect_engine = inflect.engine()
pat_count = 0
last_pat_message = None


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='goons learn to count'))


# Add new games by creating additional commands. set party_size to 0 to create a party with no player limit
@bot.command(aliases=['valrant', 'shootbang'])
async def valorant(ctx):
    activity_name = 'Valorant'
    party_size = 5
    role = '<@&883915179761487922>'
    color = 0xff4655
    await start_lfg(ctx, activity_name, party_size, role, color)


@bot.command(aliases=['drg', 'rockandstone', 'rocknstone'])
async def deeprockgalactic(ctx):
    activity_name = 'Deep Rock Galactic'
    party_size = 4
    role = '<@&847218697647161404>'
    color = 0xffc400
    await start_lfg(ctx, activity_name, party_size, role, color)


@bot.command()
async def test(ctx):
    activity_name = 'Test'
    party_size = 0
    role = ''
    await start_lfg(ctx, activity_name, party_size, role)


@bot.command()
async def pat(ctx):
    global pat_count, last_pat_message
    if last_pat_message is not None:
        await last_pat_message.delete()
    await ctx.message.delete()
    pat_count += 1
    pat_string = 'pat' if pat_count == 1 else 'pats'
    last_pat_message = await ctx.channel.send(content=f"{inflect_engine.number_to_words(pat_count).capitalize()} {pat_string}, ha ha ha!")
    print(f'patter: {ctx.author}')


@bot.command(aliases=['start', 'startparty'])
async def forcestart(ctx):
    for view in list(views):
        if ctx.channel.id == view.original_message.channel.id:
            await view.start_party()


@bot.command()
async def cancel(ctx):  # cancel parties in the channel this command is used
    for view in list(views):
        if ctx.channel.id == view.original_message.channel.id:
            await view.cancel_lfg()


@bot.command()
async def cancelall(ctx):
    for view in list(views):
        if ctx.guild.id == view.original_message.guild.id:
            await view.cancel_lfg()


async def start_lfg(ctx, activity_name, party_size, role, embed_color=Embed.Empty):
    """
    |coro|

    Creates a new LFG post.

    :param ctx: the context from the command
    :param activity_name: the name of the activity
    :param party_size: the number of users to look for. set to 0 for a party with no max size
    :param role: the role pinged when posting a lfg message (can be left blank)
    :param embed_color: the embed color
    """
    party = []
    embed = Embed(title='Current Party:', color=embed_color)
    embed = refresh_embed(embed, party, party_size)
    view = PartyView(activity_name, party, party_size, role, embed)

    original_message = await ctx.send(f'{role} Count to {party_size if party_size > 0 else "*yes*"} for {activity_name}', view=view, embed=embed)
    view.set_original_message(original_message)
    if party_size != 1:
        await view.add_user(ctx.author)


def in_party(user, party):
    """Returns true if the party contains the user"""
    if party.count(user) > 0:
        return True
    return False


def get_mentions(party):
    """Returns a string with a mention for each party member"""
    s = ''
    for users in party:
        s += users.mention + ' '
    return s


def refresh_embed(embed, party, party_size):
    """
    Clears all fields in the embed, then adds fields based on the parameters.

    :param embed: the embed to refresh
    :param party: a field is added for each party member
    :param party_size: a blank field is added for each empty party slot. if 0, one blank field is always added
    :return: the embed
    """
    embed.clear_fields()
    party_length = len(party)
    if party_size > 0:
        for x in range(party_size):
            if x < party_length:
                embed.add_field(name=f'{x + 1}.', value=party[x].name, inline=False)
            else:
                embed.add_field(name=f'{x + 1}.', value='------', inline=False)
    else:
        index = 0
        for x in range(party_length):
            embed.add_field(name=f'{x + 1}.', value=party[x].name, inline=False)
            index += 1
        embed.add_field(name=f'{index + 1}.', value='------', inline=False)
    return embed


def add_view(view):
    views.append(view)


def remove_view(view):
    views.remove(view)


class PartyView(View):
    def __init__(self, activity_name, party, party_size, role, embed):
        super().__init__(timeout=7200)  # 2 hours
        self.activity_name = activity_name
        self.party = party
        self.party_size = party_size
        self.role = role
        self.embed = embed
        self.original_message = None
        add_view(self)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji='<:penta:561357366092759088>')
    async def join_button_callback(self, button, interaction):
        await interaction.response.defer()
        user = interaction.user
        if not in_party(user, self.party):  # if the user is not in the party, add them
            position = await self.add_user(user)
            if position >= self.party_size - 1 and self.party_size > 0:  # if the user fills the last slot in the party, start the party
                await self.start_party()
            else:  # notify the user they have been added
                await interaction.followup.send(content='You have been added to the party.', ephemeral=True)
        print(f'current party: {self.party}')

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red, emoji='<:madnpc:863675310650163200>')
    async def leave_button_callback(self, button, interaction):
        await interaction.response.defer()
        user = interaction.user
        if in_party(user, self.party):  # if the user is in the party, remove them, update the party, and notify the user they have been removed
            self.party.remove(user)
            self.embed = refresh_embed(self.embed, self.party, self.party_size)
            await interaction.edit_original_message(view=self, embed=self.embed)
            await interaction.followup.send(content='You have been removed from the party.', ephemeral=True)
        print(f'current party: {self.party}')

    async def add_user(self, user):
        """
        |coro|

        Adds the given user to this party, then updates the party

        :param user: the user to add
        :return: the added user's position in the party
        """
        self.party.append(user)
        position = self.party.index(user)
        self.embed = refresh_embed(self.embed, self.party, self.party_size)
        # self.embed.set_field_at(position, name=f'{position + 1}.', value=user.name, inline=False)
        await self.original_message.edit(view=self, embed=self.embed)
        return position

    async def start_party(self):
        """|coro|

        Notify the party and end the view"""
        await self.original_message.channel.send(f'Party for {self.activity_name} is ready! {get_mentions(self.party)}')
        await self.original_message.delete()
        self.stop()
        remove_view(self)

    async def on_timeout(self):
        for buttons in self.children:
            buttons.disabled = True
        await self.original_message.edit(content=f'Party for {self.activity_name} timed out', view=self)
        await self.original_message.reply(content='Party timed out <:sadcat:823688094167203870>')
        remove_view(self)

    async def cancel_lfg(self):
        """|coro|

        Cancels the LFG post and calls View.stop()"""
        for buttons in self.children:
            buttons.disabled = True
        await self.original_message.edit(content=f'Party for {self.activity_name} canceled.', view=self)
        self.stop()
        remove_view(self)

    def set_original_message(self, message):
        self.original_message = message


bot.run(os.getenv("token"))
