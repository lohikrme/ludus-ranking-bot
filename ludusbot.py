# ludusbot.py
# Made by Chinese Parrot 24th july 2024

import random
import psycopg2
import discord
from discord.ext import commands

# create a default intents object
intents = discord.Intents.default()  
intents.message_content = True 
intents.members = True

# add both command prefix and intents to the bot
bot = commands.Bot(command_prefix='%', intents=intents)  # use percent as start of command

# when bot enters the channel
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

# --------- ALL COMMANDS ---------------

# factual command
@bot.command()
async def factual(ctx):
    commands = ["Chinese Parrot is a tier S duellist.", 
                "Brownie and Parrot rule the ludus", 
                "Shin is goat", 
                "Mount Blanc is the highest mountain of Europe not Elbrus",
                "Camponotus herculeanus is the largest ant species of Europe",
                "Petra and PSP are the ddossers",
                "Eagle owls kill all other predatory birds of their nesting territory, that's why they are so feared by other predatory birds",
                "You can calculate the 95% Confidence interval using formula: [average - 1.96 * SD; average + 1.96 * SD]",
                "Rabbits despite their smaller size usually dominate larger hares when competing territory",
                "The flying squirrel is a cute fluffy mammal that glides from tree to tree, eats leaves, and is protected by the EU directive",
                "Psychopaths don't feel anxiety or remorse, so if u feel neither, most likely u are not a psychopath"
                ]
    answer = random.choice(commands)
    await ctx.send(answer)

# register command
@bot.command()
async def register(ctx, nickname):

    username = ctx.author.name

    # fetch database password
    file = open('dbpassword.txt', 'r')
    salasana = file.readline()
    file.close()

    # open connection to database
    conn = psycopg2.connect(
        database = "ludus",
        user = "postgres",
        password = salasana,
        host = "localhost",
        port = "5432"
    )

    # if user has alrdy been registered
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        await ctx.send("You have already been registered! If you want to reset your rank, please contact Ludus admins.")

    # add a new user if database has space
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players", ())
        amount_of_lines = cursor.fetchone()[0]
        if (amount_of_lines < 10000):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, points, nickname) VALUES (%s, %s)", (username, 0, nickname))
            await ctx.send("Your discord username has successfully been registered into Ludus players!")
        else:
            await ctx.send("The database is full. This most likely means that the database has been attacked by a spammer. \n This will not endanger security, but limit makes sure database wont grow too large. Please contact Ludus admins.")

# queue command

# rename command


# token of bot to identify
file = open('token.txt', 'r')
token = file.readline()
file.close()

bot.run(token)
