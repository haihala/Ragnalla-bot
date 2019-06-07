from constants import *
from prac import Prac

import datetime
from time import time
from math import inf

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

def find(p, seq):
    """Return first item in seq where p(item) == True"""
    for x in seq:
        if p(x):
            return x

def get_time(string):
    """
    Return epoch time of practice session specified by string
    """
    spl = string.lower().split(':')
    daynum = PLAIN_DAYS.index(spl[0])

    d = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.min.time())
    days_ahead = daynum - d.weekday()
    target_day = d + datetime.timedelta(days_ahead)
    daytime = int(target_day.timestamp())

    if len(spl) == 2:
        tod = spl[1]
    else:
        tod = "1800"
    hour = int(tod[:2])
    minute = int(tod[2:])

    clocktime = 60 * (60 * hour + minute)
    result = daytime + clocktime
    if result-time()<0:
        result += 7*24*60*60
    return result

def get_pracs():
    with open(database) as f:
        tokens = [i.split() for i in f.readlines() if i]
    return [Prac(int(i[0]), i[1:]) for i in tokens]

def get_prac(timestamp):
    if not timestamp:
        # If no target time provided, go with first that hasn't yet gone.
        prac = min(get_pracs(), key=lambda x: x.time+inf*x.time<time())
        if prac.time < time():
            # No future practice sessions
            raise Exception("No active sessions")
        else:
            return prac
    else:
        pracs = [i for i in pracs if i.time == target_time]
        if pracs:
            return pracs[0]
        else:
            # Time was provided, yet it didn't match a practice session.
            raise Exception("Such a timestamp doesn't exist")

def add_prac(prac):
    with open(database, 'a') as f:
        f.write("{} {}\n".format(prac.time, " ".join(prac.players)))

def del_prac(timestamp):
    pracs = [i for i in get_pracs() if i.time != timestamp]
    with open(database, 'w') as f:
        for prac in pracs:
            f.write("{} {}\n".format(prac.time, " ".join(prac.players)))

def move_prac(origin, destination):
    prac = get_prac(origin)
    if prac:
        del_prac(prac.time)
        prac.time = destination
        add_prac(prac)

def sub_prac(players_in, players_out, target_time=None):
    pracs = get_pracs()
    prac = get_prac(target_time)
    target_time = prac.time
    del_prac(target_time)

    new_players = set(prac.players)
    new_players -= set(players_out)
    new_players = new_players.union(set(players_in))

    add_prac(Prac(target_time, new_players))

