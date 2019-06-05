from constants import *

from discord.ext import commands

prefix = "!"
bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print("Everything's all ready to go~")

@bot.event
async def on_message(message):
    print("The message's content was", message.content)
    await bot.process_commands(message)


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

@bot.command()
async def dstart(ctx):
    """
    Posts a single doodle-esque message with reactions to communicate with.
    """
    msg = await ctx.send(DOODLE_MESSAGE)
    for emoji in WEEKDAY_EMOJIS:
        await msg.add_reaction(emoji)
    #await msg.pin()


@bot.command()
async def dstat(ctx):
    """
    Shows days that five or more users have approved. Assume that only the latest dstart is legit.
    """
    lastdmsg = await ctx.history().get(content=DOODLE_MESSAGE, author=bot.user)
    load = {}
    for r in lastdmsg.reactions:
        users = [i.name for i in await r.users().flatten() if not i.id == bot.user.id]
        load[r.emoji.name] = users

    text = "```"+"\n".join(["{}: {}, {}".format(day, len(load[day]), ", ".join(load[day])) for day in PLAIN_DAYS])+"```"
    await ctx.send(text)


bot.run("NTg1NTIwMDc1NjMzNTkwMjgz.XPargg.5kBbaTcIWXFeCQTPipsJdKRRqCk")
