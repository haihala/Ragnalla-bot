from .constants import CONF_DIR, database
from prac_db import get_pracs

from time import time
from json import dump, load
from os.path import join as pjoin

class Reminder:
    def __init__(self, guild):
        # {user: {prac or confirm(str(type+time)): [alarms sent ("seconds before")]}}
        self.processed = {}

    def load_config(self, user):
        # First load the global configuration, then put their personal on top of that.
        self.conf[user] = self.load("global")
        self.conf[user].update(self.load(user))

    def update_config(self, user, update)
        current = self.load(user)
        current.update(update)
        self.save(user)

        # Reload for that user
        self.load_config(user)

    def load(self, account):
        try:
            with open(pjoin(CONF_DIR, account+".json"), "r") as f:
                return load(f)
        except FileNotFoundError:
            return {}

    def save(self, account):
        with open(pjoin(CONF_DIR, account+".json"), "w") as f:
            dump(self.conf[account], f)


    def check(self, user, session, target):
        conf = self.load(user)
        if user not in self.processed:
            self.processed[user] = {}
        if target+session.time not in self.processed[user]:
            self.processed[user][target+session.time] = set()

        new = set()
        for checkable in conf:
            if target+checkable not in self.processed[user][target+session.time] and time()-checkable < session.time:
                new.add(session)
                self.processed[user][target+session.time].add(target+checkable)
        return new

    def ack_notifications(self):
        pings = {}
        for session in get_pracs():
            for user in session.players:
                new_pings = self.check(user, session, "ack")
                if user in pings:
                    pings[user] = pings[user].union(new_pings)
                else:
                    pings[user] = new_pings
        return pings


    def voice_notifications(self):
        pings = {}
        for session in get_pracs():
            for user in session.players:
                new_pings = self.check(user, session, "voice")
                if user in pings:
                    pings[user] = pings[user].union(new_pings)
                else:
                    pings[user] = new_pings
        return pings


