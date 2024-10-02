# bot_instance.py 
# updated 2nd october 2024

import discord
from discord.ext import commands

# GIVE BOT DEFAULT INTENTS + ACCESS TO MESSAGE CONTENT AND MEMBERS AND SET COMMAND PREFIX TO BE '/'
intents = discord.Intents.default()  
intents.message_content = True 
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)  # use slash as start of command