from constants import *
from helpers import *

from discord.ext import commands

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Everything's all ready to go~")
    print("Starting lineup is {}".format(await get_starting_lineup(bot.guilds[0])))

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
    if ldm and msg:
        if msg.id == ldm.id:
            reacters = [i.name for i in await [r for r in await latest_doodle_reactions(chan, bot.user) if r.emoji == CHECK_MARK][0].users().flatten()]
            starting_lineup = await get_starting_lineup(chan.guild)
            if all(user in reacters for user in starting_lineup ):
                await get.invoke(await bot.get_context(msg))

@bot.command()
async def prac(ctx, *, content):
    """
    Creates a prac session. Sets up reminders and makes the announcement.
    usage: <space separated list of times>;<space separated list of participants>: creates a 'prac' with those participants for each time specified. Makes announcements and activates reminder system. Times are specified as follows. One of MA|TI|KE|TO|PE|LA|SU (caps insensitive). Can optionally have a time of day, specified like so: MA:1700, clock format is 24h military.
    """
    pass

@bot.command()
async def sub(ctx, *, content):
    """
    Replaces one player in a prac session with another.
    usage: <day of prac> <list of corretly prefixed players>: prefix player name with '-' to remove and with '+' to add.
    """
    pass

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
    msg = await ctx.send(DOODLE_MESSAGE)

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

with open("app.token") as f:
    bot.run(f.read().strip())
