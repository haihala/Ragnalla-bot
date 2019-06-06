from constants import *

def get_dayems(guild):
    ems = {em.name: em for em in guild.emojis}
    return [ems[d] for d in PLAIN_DAYS]

async def latest_doodle_message(ctx, bot_user):
    return await ctx.history().get(content=DOODLE_MESSAGE, author=bot_user)

async def latest_doodle_reactions(ctx, bot_user):
    return (await latest_doodle_message(ctx, bot_user)).reactions

async def get_starting_lineup(guild):
    all_members = guild.members
    return list(set(i.name for i in all_members if any(j.name.lower() in ["player", "trial"] for j in i.roles)))

def verbose_doodle_output(names, days, ready):
    WORKS = 'x'
    NOTOK = '.'

    namelen = max(len(n) for n in names)
    header = ' ' * (namelen + 1) + ' '.join("{0:s}({1:d})".format(day, len(days[day])) for day in PLAIN_DAYS)
    lines = ("{name:{width}s} ".format(name=name, width=namelen)
                + ' '.join("  {}  ".format(WORKS if name in days[day] else NOTOK) for day in PLAIN_DAYS)
                for name in names)

    return "```\n{header}\n{status}\n```".format(header=header, status='\n'.join(lines))