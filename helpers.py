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
