from code.constants import token
from discord.ext import commands

bot = commands.Bot(command_prefix="!")
bot.load_extension("code.doodle.main")
bot.load_extension("code.prac.main")

@bot.event
async def on_ready():
    print("Everything's all ready to go!")

@bot.event
async def on_message(message):
    print("The message's content was", message.content)
    await bot.process_commands(message)

with open(token) as f:
    bot.run(f.read().strip())
