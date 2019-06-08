from ..constants import PLAIN_DAYS, CHECK_MARK
from ..helpers import find, get_starting_lineup

from .constants import *

from discord.ext import commands

class Doodle(commands.Cog):
    """
    Cog for doodle group.
    """
    def __init__(self, bot):
        self.bot = bot

    def get_dayems(self):
        ems = {em.name: em for em in self.bot.guilds[0].emojis}
        return [ems[d] for d in PLAIN_DAYS]

    async def latest_message(self, ctx):
        return await ctx.history().get(content=DOODLE_NEW_MESSAGE, author=self.bot.user)

    async def latest_reactions(self, ctx):
        return (await self.latest_message(ctx)).reactions

    def verbose_output(self, names, days, ready):
        WORKS = 'x'
        NOTOK = '.'

        namelen = max(len(n) for n in names)
        header = ' ' * (namelen + 1) + ' '.join("{0:s}({1:d})".format(day, len(days[day])) for day in PLAIN_DAYS)
        lines = ("{name:{width}s} ".format(name=name, width=namelen)
                    + ' '.join("  {}  ".format(WORKS if name in days[day] else NOTOK) for day in PLAIN_DAYS)
                    for name in names)

        return "```\n{header}\n{status}\n```".format(header=header, status='\n'.join(lines))

    @commands.group()
    async def doodle(self, ctx):
        """
        Doodle-esque scheduling system.
        """
        if ctx.invoked_subcommand is None:
            print(ctx.__dict__)
            await ctx.send(DOODLE_INVALID_SUBCOMMAND)

    @doodle.command()
    async def new(self, ctx):
        """
        Posts a single doodle-esque message with reactions to communicate with.
        """
        msg = await ctx.send(DOODLE_NEW_MESSAGE)

        for emoji in self.get_dayems():
            await msg.add_reaction(emoji)
        await msg.add_reaction(CHECK_MARK)

    @doodle.command()
    async def get(self, ctx):
        """
        Shows status of last doodle post. When every player and trialee has readied this will be automatically printed. Use `-v` or `--verbose` for more information
        """
        load = {}
        for r in await self.latest_reactions(ctx):
            users = [i.name for i in await r.users().flatten() if not i.id == self.bot.user.id]
            if type(r.emoji) is str:
                load[r.emoji] = users
            else:
                load[r.emoji.name] = users

        args = ctx.message.content.split()[2:]
        if "-v" in args or "--verbose" in args:
            names = set(user for users in load.values() for user in users)
            days = {day: load[day] for day in PLAIN_DAYS}
            ready = load[CHECK_MARK]

            text = self.verbose_output(names, days, ready)
            # lines = ["{}, {}: {}".format(day, len(load[day]), ", ".join(load[day])) for day in PLAIN_DAYS]
            # lines.append("\nready, {}: {}".format(len(load[CHECK_MARK]), ", ".join(load[CHECK_MARK])))
            # text = "```"+"\n".join(lines)+"```"
        else:
            text = "```"
            load = {key: value for key, value in load.items() if key in PLAIN_DAYS}
            full_days = [i for i in load if len(load[i])>=5]

            if full_days:
                text += "\nFull days: {}".format(", ".join(full_days))

            i = 4
            while text == "```" and i:
                l = [j for j in load if len(load[j])==i]
                if l:
                    text += "\n{}/5 days: {}".format(i, ", ".join(l))
                i -= 1

            text += "```"

        await ctx.send(text)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        reacter = await self.bot.fetch_user(payload.user_id)
        emoji = payload.emoji
        chan = self.bot.get_channel(payload.channel_id)
        msg = await chan.fetch_message(payload.message_id)
        ldm = await self.latest_message(chan)
        if ldm and msg and msg.id == ldm.id:
            reacts = await self.latest_reactions(chan)
            checkmarks = find(lambda x: x.emoji==CHECK_MARK, reacts)
            if checkmarks:
                ready_players = [i.name for i in await checkmarks.users().flatten()]
                starting_lineup = await get_starting_lineup(chan.guild)
                if all(user in ready_players for user in starting_lineup):
                    await self.get.invoke(await self.bot.get_context(msg))

def setup(bot):
    bot.add_cog(Doodle(bot))
