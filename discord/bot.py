import os
import json
import time
from dotenv import load_dotenv
import discord

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("Login success!")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if not isinstance(message.channel, discord.DMChannel):
        return
    if not message.content:
        return

    guild = client.get_guild(int(os.getenv("GUILD_ID", 0)))
    if message.author not in guild.members:
        return

    role = guild.get_role(int(os.getenv("ROLE_ID")))
    if message.author in role.members:
        await message.channel.send("認証済みです。")
        return

    codes = {}
    try:
        with open("./data/codes.json") as f:
            codes = json.load(f)
    except Exception:
        pass
    codes = {k: v for k, v in codes.items() if v > time.time() - 60}
    if message.content in codes.keys():
        codes = {k: v for k, v in codes.items() if k != message.content}
        with open("./data/codes.json", "w") as f:
            json.dump(codes, f)
        member = guild.get_member(message.author.id)
        await member.add_roles(role)
        await message.channel.send("認証しました。")
    else:
        with open("./data/codes.json", "w") as f:
            json.dump(codes, f)
        await message.channel.send("認証に失敗しました。")


client.run(TOKEN)
