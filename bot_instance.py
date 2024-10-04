# bot_instance.py
# updated 4th october 2024

import discord
from discord.ext import commands

# GIVE BOT DEFAULT INTENTS + ACCESS TO MESSAGE CONTENT
# AND MEMBERS AND SET COMMAND PREFIX TO BE '/'
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# most commands are slash, ! is for possible hidden commands
bot = commands.Bot(command_prefix="!", intents=intents)
