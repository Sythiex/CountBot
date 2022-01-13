from typing import Union

import discord
import inflect
from discord import Embed, Colour, Member, Button, Interaction, Message
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View


class PartyCommands(commands.Cog, name='Party Commands'):
    """Create and start parties for games"""

    def __init__(self, bot):
        self.bot = bot
        self.views = []  # list of active PartyViews
        self.inflect_engine = inflect.engine()
        self.pat_count = 0
        self.last_pat_message = None
        self.last_pat_command_message = None

    # Add new games by creating additional commands. set party_size to 0 to create a party with no player limit
    @commands.command(aliases=['valrant', 'shootbang'])
    async def valorant(self, ctx: Context):
        """Start a party for Valorant"""
        activity_name = 'Valorant'
        party_size = 5
        role = '<@&883915179761487922>'
        color = 0xff4655
        await self.start_lfg(ctx, activity_name, party_size, role, color)

    @commands.command(aliases=['drg', 'rockandstone', 'rocknstone'])
    async def deeprockgalactic(self, ctx: Context):
        """Start a party for Deep Rock Galactic"""
        activity_name = 'Deep Rock Galactic'
        party_size = 4
        role = '<@&847218697647161404>'
        color = 0xffc400
        await self.start_lfg(ctx, activity_name, party_size, role, color)

    @commands.command()
    async def test(self, ctx: Context):
        print('test')
        activity_name = 'Test'
        party_size = 0
        role = ''
        await self.start_lfg(ctx, activity_name, party_size, role)

    @commands.command(aliases=['startparty'])
    async def start(self, ctx: Context):
        """Start your parties in this channel"""
        for view in list(self.views):
            if ctx.channel.id == view.original_message.channel.id:  # if view is in the same channel
                if ctx.author.id == view.party_owner.id or ctx.author.get_role(self.bot.admin_role_id) is not None:  # if command user is the party owner or admin
                    await view.start_party()

    @commands.command()
    async def cancel(self, ctx: Context):
        """Cancel your parties in this channel"""
        for view in list(self.views):
            if ctx.channel.id == view.original_message.channel.id:  # if view is in the same channel
                if ctx.author.id == view.party_owner.id or ctx.author.get_role(self.bot.admin_role_id) is not None:  # if command user is the party owner or admin
                    await view.cancel_lfg()

    @commands.command()
    async def cancelall(self, ctx: Context):
        """[ADMIN ONLY] Cancel all parties in this server"""
        if ctx.author.get_role(self.bot.admin_role_id) is not None:  # if command user is admin
            for view in list(self.views):
                if ctx.guild.id == view.original_message.guild.id:  # if view is in the same server
                    await view.cancel_lfg()

    @commands.command()
    async def pat(self, ctx: Context):
        """Pat CountBot"""
        if self.last_pat_message is not None:
            await self.last_pat_message.delete()
        if self.last_pat_command_message is not None:
            await self.last_pat_command_message.delete()
        self.pat_count += 1
        self.last_pat_command_message = ctx.message
        self.last_pat_message = await ctx.channel.send(
            content=f"{self.inflect_engine.number_to_words(self.pat_count).capitalize()} {'pat' if self.pat_count == 1 else 'pats'}, ha ha ha!")
        print(f'patter: {ctx.author}')

    def add_view(self, view):
        self.views.append(view)

    def remove_view(self, view):
        self.views.remove(view)

    async def start_lfg(self, ctx: Context, activity_name: str, party_size: int, role: str, embed_color: Union[Colour, int] = Embed.Empty):
        """
        |coro|

        Creates a new LFG post.

        :param ctx: the context from the command
        :param activity_name: the name of the activity
        :param party_size: the number of members to look for. set to 0 for a party with no max size
        :param role: the role to mention when posting a lfg message, passed as a string in the format '<@&role_id)>' (can be left empty)
        :param embed_color: the embed color, can be a hex color code or discord.Colour
        """
        party = []
        if party_size != 1:  # auto-add the command user to the party
            party.append(ctx.author)
        embed = Embed(title='Current Party:', color=embed_color)
        embed = refresh_embed(embed, party, party_size)
        view = PartyCommands.PartyView(self, activity_name, party, party_size, role, embed, ctx.author)
        original_message = await ctx.send(f'{role} Count to {party_size if party_size > 0 else "*yes*"} for {activity_name}', view=view, embed=embed)
        view.set_original_message(original_message)

    class PartyView(View):
        def __init__(self, cog, activity_name: str, party: list[Member], party_size: int, role: str, embed: Embed, party_owner: Member):
            super().__init__(timeout=7200)  # 2 hours
            self.activity_name = activity_name
            self.party = party
            self.party_size = party_size
            self.role = role
            self.embed = embed
            self.party_owner = party_owner
            self.original_message = None
            self.cog = cog
            cog.add_view(self)

        @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji='<:penta:561357366092759088>')
        async def join_button_callback(self, button: Button, interaction: Interaction):
            await interaction.response.defer()
            member = interaction.user
            if not in_party(member, self.party):  # if the member is not in the party, add them
                position = await self.add_member(member)
                if position >= self.party_size - 1 and self.party_size > 0:  # if the member fills the last slot in the party, start the party
                    await self.start_party()
                else:  # notify the member they have been added
                    await interaction.followup.send(content='You have been added to the party.', ephemeral=True)
            print(f'{member} clicked a button; current party: {self.party}')

        @discord.ui.button(label="Leave", style=discord.ButtonStyle.red, emoji='<:madnpc:863675310650163200>')
        async def leave_button_callback(self, button: Button, interaction: Interaction):
            await interaction.response.defer()
            member = interaction.user
            if in_party(member, self.party):  # if the member is in the party, remove them and notify them they have been removed
                await self.remove_member(member)
                await interaction.followup.send(content='You have been removed from the party.', ephemeral=True)
            print(f'{member} clicked a button; current party: {self.party}')

        async def add_member(self, member: Member):
            """
            |coro|

            Adds the given member to this party, then updates the party

            :param member: the member to add
            :return: the added member's position in the party
            """
            self.party.append(member)
            position = self.party.index(member)
            self.embed = refresh_embed(self.embed, self.party, self.party_size)
            await self.original_message.edit(view=self, embed=self.embed)
            return position

        async def remove_member(self, member: Member):
            """
            |coro|

            Removes the given member from this party, then updates the party

            :param member: the member to remove
            """
            self.party.remove(member)
            self.embed = refresh_embed(self.embed, self.party, self.party_size)
            await self.original_message.edit(view=self, embed=self.embed)

        async def start_party(self):
            """|coro|

            Notify the party and end the view"""
            await self.original_message.channel.send(f'Party for {self.activity_name} is ready! {get_mentions(self.party)}')
            await self.original_message.delete()
            self.stop()
            self.cog.remove_view(self)

        async def on_timeout(self):
            for buttons in self.children:
                buttons.disabled = True
            await self.original_message.edit(content=f'Party for {self.activity_name} timed out', view=self)
            await self.original_message.reply(content='Party timed out <:sadcat:823688094167203870>')
            self.cog.remove_view(self)

        async def cancel_lfg(self):
            """|coro|

            Cancels the LFG post and calls View.stop()"""
            for buttons in self.children:
                buttons.disabled = True
            await self.original_message.edit(content=f'Party for {self.activity_name} canceled.', view=self)
            self.stop()
            self.cog.remove_view(self)

        def set_original_message(self, message: Message):
            self.original_message = message


def refresh_embed(embed: Embed, party: list[Member], party_size: int):
    """
    Clears all fields in the embed, then adds fields based on the parameters.

    :param embed: the embed to refresh
    :param party: a list con field is added for each party member
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


def in_party(member: Member, party: list[Member]):
    """Returns true if the party contains the member"""
    if party.count(member) > 0:
        return True
    return False


def get_mentions(party: list[Member]):
    """Returns a string with a mention for each party member"""
    s = ''
    for members in party:
        s += members.mention + ' '
    return s