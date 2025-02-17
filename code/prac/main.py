from .prac_db import *
from .constants import *

from discord.ext import commands

class Prac(commands.Cog):
    """
    Cog for prac group.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def prac(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(PRAC_INVALID_SUBCOMMAND)

    @prac.command()
    async def new(self, ctx, *, content):
        """
        Creates a prac session. Sets up reminders and makes the announcement.
        usage: !prac new <timespec> <list of players>: creates a 'prac' with those participants for each time specified. Timespec can be at any point in the command and is specified as followsA One of MA|TI|KE|TO|PE|LA|SU (caps insensitive). Can optionally have a time of day, specified like so: MA:1700, clock format is 24h military. All the following are legal 'ma' 'ma:1600' 'Ma:0300' 'mA'
        """
        # Sanitize
        bits = content.split()
        timespec = find(get_time, bits)
        if timespec:
            players = [i for i in bits if get_time(i) == None]
            add_prac(get_time(timespec), players)
            await ctx.send(PRAC_ADD_OK)
            await self.get.invoke(ctx)
        else:
            await ctx.send(PRAC_MISSING_TIME)

    @prac.command()
    async def sub(self, ctx, *, content):
        """
        Replaces players in a prac session.
        usage: !prac sub [timespec] <list of players>: Mentioned players are removed if they are currently in, added if they are out. Time is optional and is specified using the weekday:clock method used in !prac new. Time specification can also appear anywhere in the command, not just as firsts argument. If multiple times are provided, the first is used.
        """
        bits = content.split()
        timespec = find(get_time, bits)
        players = [i for i in bits if get_time(i) == None]

        try:
            sub_prac(players, timespec)
            await ctx.send(PRAC_SUB_OK)
            await self.get.invoke(ctx)
        except ValueError as e:
            await ctx.send(str(e))

    @prac.command()
    async def move(self, ctx, *, content):
        """
        Moves a prac session to another time.
        usage: !prac move [current timespec] <destination timespec> If current timespec isn't provided, the first upcoming prac is assumed. If current timespec is provided, it has to be the first one. Timespec format is the same as in !prac new
        """

        times = [get_time(i) for i in content.split() if get_time(i) != None]
        if len(times) == 1:
            origin = None
            destination = times[-1]
        elif len(times) == 2:
            origin = times[0]
            destination = times[-1]
        else:
            await ctx.send(PRAC_MISSING_TIME)
            return

        try:
            move_prac(origin, destination)
            await ctx.send(PRAC_MOVE_OK)
            await self.get.invoke(ctx)
        except ValueError as e:
            await ctx.send(str(e))

    @prac.command()
    async def get(self, ctx):
        active_sessions = get_pracs()
        text = "```{}```".format("\n".join(i.pretty(ctx.guild) for i in active_sessions))
        await ctx.send(text)

def setup(bot):
    bot.add_cog(Prac(bot))
