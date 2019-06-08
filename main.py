from prac import Prac
from constants import *
from helpers import *

from discord.ext import commands

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Everything's all ready to go!")

@bot.event
async def on_message(message):
    print("The message's content was", message.content)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    reacter = await bot.fetch_user(payload.user_id)
    emoji = payload.emoji
    chan = bot.get_channel(payload.channel_id)
    msg = await chan.fetch_message(payload.message_id)
    ldm = await latest_doodle_message(chan, bot.user)
    if ldm and msg and msg.id == ldm.id:
        reacts = await latest_doodle_reactions(chan, bot.user)
        if any(r.emoji == CHECK_MARK for r in reacts):
            ready_players = [i.name for i in await find(lambda r: r.emoji == CHECK_MARK, reacts).users().flatten()]
            starting_lineup = await get_starting_lineup(chan.guild)
            if all(user in ready_players for user in starting_lineup):
                await get.invoke(await bot.get_context(msg))


@bot.group()
async def prac(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.__dict__)
        await ctx.send(PRAC_INVALID_SUBCOMMAND)

@prac.command()
async def new(ctx, *, content):
    """
    Creates a prac session. Sets up reminders and makes the announcement.
    usage: !prac new <timespec> <list of players>: creates a 'prac' with those participants for each time specified. Timespec can be at any point in the command and is specified as followsA One of MA|TI|KE|TO|PE|LA|SU (caps insensitive). Can optionally have a time of day, specified like so: MA:1700, clock format is 24h military. All the following are legal 'ma' 'ma:1600' 'Ma:0300' 'mA'
    """
    # Sanitize
    bits = content.split()
    timespec = find(get_time, bits)
    if timespec:
        players = [i for i in bits if get_time(i) == None]
        add_prac(Prac(get_time(timespec), players))
        await ctx.send(PRAC_ADD_OK)
        await get_active.invoke(ctx)
    else:
        await ctx.send(PRAC_MISSING_TIME)

@prac.command()
async def sub(ctx, *, content):
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
        await get_active.invoke(ctx)
    except ValueError as e:
        await ctx.send(str(e))

@prac.command()
async def move(ctx, *, content):
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
        print(times)
        print(content)
        await ctx.send(PRAC_MISSING_TIME)
        return

    try:
        move_prac(origin, destination)
        await ctx.send(PRAC_MOVE_OK)
        await get_active.invoke(ctx)
    except ValueError as e:
        await ctx.send(str(e))

@prac.command()
async def get(ctx):
    active_sessions = get_pracs()
    text = "```{}```".format("\n".join(i.pretty(ctx.guild) for i in active_sessions))
    await ctx.send(text)

@bot.group()
async def doodle(ctx):
    """
    Doodle-esque scheduling system.
    """
    if ctx.invoked_subcommand is None:
        print(ctx.__dict__)
        await ctx.send(DOODLE_INVALID_SUBCOMMAND)

@doodle.command()
async def new(ctx):
    """
    Posts a single doodle-esque message with reactions to communicate with.
    """
    msg = await ctx.send(DOODLE_NEW_MESSAGE)

    for emoji in get_dayems(msg.guild):
        await msg.add_reaction(emoji)
    await msg.add_reaction(CHECK_MARK)

@doodle.command()
async def get(ctx):
    """
    Shows status of last doodle post. When every player and trialee has readied this will be automatically printed. Use `-v` or `--verbose` for more information
    """
    load = {}
    for r in await latest_doodle_reactions(ctx, bot.user):
        users = [i.name for i in await r.users().flatten() if not i.id == bot.user.id]
        if type(r.emoji) is str:
            load[r.emoji] = users
        else:
            load[r.emoji.name] = users

    args = ctx.message.content.split()[2:]
    if "-v" in args or "--verbose" in args:
        names = set(user for users in load.values() for user in users)
        days = {day: load[day] for day in PLAIN_DAYS}
        ready = load[CHECK_MARK]

        text = verbose_doodle_output(names, days, ready)
        # lines = ["{}, {}: {}".format(day, len(load[day]), ", ".join(load[day])) for day in PLAIN_DAYS]
        # lines.append("\nready, {}: {}".format(len(load[CHECK_MARK]), ", ".join(load[CHECK_MARK])))
        # text = "```"+"\n".join(lines)+"```"
    else:
        text = "```"
        load = {key: value for key, value in load.items() if key in PLAIN_DAYS}
        full_days = [i for i in load if len(load[i])>=5]

        if full_days:
            text += "\nFull days: {}".format(", ".join(full_days))

        i = 4
        while text == "```" and i:
            l = [j for j in load if len(load[j])==i]
            if l:
                text += "\n{}/5 days: {}".format(i, ", ".join(l))
            i -= 1

        text += "```"

    await ctx.send(text)

with open(token) as f:
    bot.run(f.read().strip())
