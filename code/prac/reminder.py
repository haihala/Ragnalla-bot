from .constants import CONF_DIR, database
from .prac_db import get_pracs

from time import time
from json import dump, load
from os.path import join as pjoin
from pathlib import Path

class Reminder:
    def __init__(self):
        # {user: {prac or confirm(str(type+time)): [alarms sent ("seconds before")]}}
        self.processed = {}

    def load(self, account):
        config =  Path(pjoin(CONF_DIR, account+".json"))
        if not config.is_file():
            config = Path(pjoin(CONF_DIR, "default.json"))
        with config.open() as f:
            return load(f)

    def save(self, account):
        with open(pjoin(CONF_DIR, account+".json"), "w") as f:
            dump(self.conf[account], f)

    def notifications(self, target):
        pings = {}
        for session in get_pracs():
            for user in session.players:
                conf = self.load(user)[target]
                ident = target+str(session.time)
                if user not in self.processed:
                    self.processed[user] = {}
                if ident not in self.processed[user]:
                    self.processed[user][ident] = set()

                new_pings = set()
                for checkable in conf:
                    cident = target+str(checkable)
                    if cident not in self.processed[user][ident]:
                        if (target == "voice" and time()-checkable < session.time) or (target == "ack" and session.msg_time + checkable > time()):
                            new_pings.add(session)
                            self.processed[user][ident].add(cident)
                if user in pings:
                    pings[user] = pings[user].union(new_pings)
                else:
                    pings[user] = new_pings
        return {i: pings[i] for i in pings if pings[i]}
