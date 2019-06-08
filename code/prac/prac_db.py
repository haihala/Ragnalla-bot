from ..constants import PLAIN_DAYS
from ..helpers import find

from .session import Session
from .constants import database

from datetime import datetime, timedelta
from time import time

def get_time(string):
    """
    Return epoch time of practice session specified by string
    """
    spl = string.lower().split(':')
    if spl[0] not in PLAIN_DAYS:
        return
    daynum = PLAIN_DAYS.index(spl[0])

    d = datetime.combine(datetime.today(), datetime.min.time())
    days_ahead = daynum - d.weekday()
    target_day = d + timedelta(days_ahead)
    daytime = int(target_day.timestamp())

    if len(spl) == 2:
        if len(spl[1]) != 4:
            return
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
    return [Session(int(i[0]), i[1:]) for i in tokens if int(i[0]) > time()]

def get_prac(timestamp):
    if not timestamp:
        # If no target time provided, go with first that hasn't yet gone.
        return min(get_pracs(), key=lambda x: x.time)
    else:
        return [i for i in pracs if i.time == target_time][0]

def add_prac(session, players=None):
    if players:
        session = Session(session, players)
    with open(database, 'a') as f:
        f.write("{} {}\n".format(session.time, " ".join(session.players)))

def del_prac(timestamp):
    pracs = [i for i in get_pracs() if i.time != timestamp]
    with open(database, 'w') as f:
        for session in pracs:
            f.write("{} {}\n".format(session.time, " ".join(session.players)))

def move_prac(origin, destination):
    prac = get_prac(origin)
    if prac:
        del_prac(prac.time)
        prac.time = destination
        add_prac(prac)

def sub_prac(player_diff, target_time=None):
    prac = get_prac(target_time)
    target_time = prac.time
    del_prac(target_time)

    new_players = set(prac.players)
    players_out = set(player_diff).intersection(new_players)
    players_in = set(player_diff) - players_out

    new_players -= set(players_out)
    new_players = new_players.union(set(players_in))

    add_prac(Session(target_time, new_players))

