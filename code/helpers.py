from .constants import tryhard_voice, announcements_text, spam_text


async def get_starting_lineup(guild):
    all_members = guild.members
    return list(set(i.name for i in all_members if any(j.name.lower() in ["player", "trial"] for j in i.roles)))

def find(p, seq):
    """Return first item in seq where p(item) == True"""
    for x in seq:
        if p(x):
            return x

def get_spam_channel(guild):
    for chan in guild.text_channels:
        if chan.name == spam_text:
            return chan

def get_announcement_channel(guild):
    for chan in guild.text_channels:
        if chan.name == announcements_text:
            return chan

def get_voice_channel(guild):
    for chan in guild.voice_channels:
        if chan.name == tryhard_voice:
            return chan

