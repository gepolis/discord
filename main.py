import datetime
import os

import disnake
from disnake.ext import commands

import db
from db import Users

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all())
users = Users("db.db")
assistentlogs = db.AssistentLogs("db.db")
@bot.event
async def on_ready():
    assistentlogs.create_table()
    users.create_table()
    guild = bot.get_guild(1162706386136866857)
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    for member in guild.members:
        if not member.bot and not users.exists_user(member.id):
            users.add_user(member.id)


@bot.event
async def on_member_join(member: disnake.Member):
    if not member.bot:
        users.add_user(member.id)



@bot.event
async def on_member_remove(member):
    if not member.bot:
        users.remove_user(member.id)

for cog in os.listdir("./cogs"):
    if cog.endswith(".py"):
        bot.load_extension(f"cogs.{cog[:-3]}")

if __name__ == "__main__":
    bot.run("MTE2MjcxNzExODYyMjYxMzU5Ng.GdWbW-.2AnBCWYkiqrqVupCKpWL3B69A1PekN2TRsNgfs")

