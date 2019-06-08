from datetime import datetime

class Session:
    def __init__(self, time, players, msg_id=None):
        self.time = time
        self.players = players
        self.msg_id = msg_id

    def pretty(self, guild):
        """
        Pretty string to send to users when requested.
        """
        pretty_time = datetime.utcfromtimestamp(self.time).strftime('%a %H%M')
        pretty_players = [ guild.get_member(int(i[2:-1])).name for i in self.players ]
        return "{} {}".format(pretty_time, ", ".join(pretty_players))
