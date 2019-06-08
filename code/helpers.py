async def get_starting_lineup(guild):
    all_members = guild.members
    return list(set(i.name for i in all_members if any(j.name.lower() in ["player", "trial"] for j in i.roles)))

def find(p, seq):
    """Return first item in seq where p(item) == True"""
    for x in seq:
        if p(x):
            return x

