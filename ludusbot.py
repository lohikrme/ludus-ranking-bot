# ludusbot.py
# Made by Chinese Parrot 25th july 2024

import random
import psycopg2
import discord
from discord import ButtonStyle
import settings
from discord.ext import commands
from mybutton import MyButton

# GIVE BOT DEFAULT INTENTS + ACCESS TO MESSAGE CONTENT AND MEMBERS AND SET COMMAND PREFIX TO BE '%'
intents = discord.Intents.default()  
intents.message_content = True 
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)  # use slash as start of command

# OPEN THE CONNECTION TO THE DATABASE

conn = psycopg2.connect(
        database = settings.db_name,
        user = settings.db_user,
        password = settings.db_password,
        host = settings.db_host,
        port = settings.db_port
    )
conn.autocommit = True

# BOT ENTERS THE CHANNEL
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

# --------- ALL COMMANDS ---------------

# FACTUAL COMMAND
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
                "Psychopaths don't feel anxiety or remorse. If you are anxious, you are not a real psychopath.",
                "Xoxoxoxo",
                "Top 5 players of ludus are: Maximou, Totenflag, Parrot, Shin, Nerji",
                "Perch (Perca fluviatilis) is the most common fish in Europe",
                "Crucian carp (Carassius carassius) is the most badass fish out there. They can survive months without breathing during the harsh winters when small lakes freeze all the way to bottom.",
                "The origin of house cat is in the African wild cats (Felis sylvestris lybica)",
                "Most kinds of evolution are actually devolution - loss of genetic material. This is how dogs or MRSA developed.",
                "The heaviest sumo ever was Orora weighting up to 292kg with a height of 190cm",
                "Some parrots such as cockatoos, macaws and conures can produce up to 135 decibel sound and induce immediate hearing damage to humans.",
                "Airplane gasolin still contains lead in 2024 because the gasolin freezes so much in the air that ethanol cannot be used. Living nearby airfields can therefore be dangerous.",
                "Nergi is smartest ludus player",
                "Busbyy (BSB) is the secret name of PSP",
                "KRAAAK!"

                ]
    
    answer = random.choice(commands)
    await ctx.send(answer)

# REGISTER COMMAND
@bot.command()
async def register(ctx, nickname):
    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)

    # NOTIFY USER THEY ARE ALREADY REGISTERED
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        await ctx.send("You have already been registered! If you want to reset your rank, please contact Ludus admins.")

    # ADD A NEW USER
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players", ())
        amount_of_lines = cursor.fetchone()[0]
        if (amount_of_lines < 10000):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, points, nickname) VALUES (%s, %s, %s)", (username, 0, nickname))
            await ctx.send("Your discord username has successfully been registered into Ludus players!")
        else:
            await ctx.send("The database is full. This most likely means that the database has been attacked by a spammer. \n This will not endanger security, but limit makes sure database wont grow too large. Please contact Ludus admins.")


# CHANGENICKNAME COMMAND
@bot.command()
async def changeNickName(ctx, nickname):

    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)

    # IF USERNAME EXISTS, CHANGE THEIR NICKNAME
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM players WHERE username = %s", (username,))
        old_nickname = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET nickname = %s WHERE username = %s", (nickname, username))
        await ctx.send(f"Your nickname has been updated! Your old nickname was {old_nickname}. Your new nickname is {nickname}")


# lEADERBOARD COMMAND
@bot.command()
async def leaderboard(ctx):
    await ctx.send("Printing points of all players starting...")

    scoreboard_text = "SCOREBOARD"
    await ctx.send("```**" + scoreboard_text.center(24) + "**```")

    cursor = conn.cursor()
    cursor.execute("SELECT nickname, points FROM players ORDER BY points DESC",())

    messages = []
    data = cursor.fetchmany(1000)
    for item in data:
        printable_text = str(item)
        messages.append("```**" + printable_text.center(24) + "**```")
    await ctx.send("\n".join(messages))
    await ctx.send("All players have been printed!")


# TOP10 COMMAND
@bot.command()
async def top10(ctx):
    await ctx.send("Printing points of top10 players starting...")
    
    scoreboard_text = "TOP10 PLAYERS:"
    await ctx.send(f"```**{scoreboard_text.center(24)}**```")
    
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, points FROM players ORDER BY points DESC LIMIT 10")
    
    messages = []
    data = cursor.fetchmany(10)
    for row in data:
        printable_text = str(row)
        messages.append(f"```**{printable_text.center(24)}**```")
    
    await ctx.send("\n".join(messages))
    await ctx.send("Top10 players have been printed!")
    
    cursor.close()

# FUNCTIONS NEEDED FOR CHALLENGING PPL
    
async def accept_duel(interaction):
    print("Duel has been accepted!")

async def refuse_duel(interaction, view, challenger, opponent_nick):
    print("Duel has been refused!")
    # Iterate through the ActionRows of the message
    for action_row in interaction.message.components:
        # Iterate through the children of each ActionRow
        for component in action_row.children:
            # Check if the component's custom_id matches the ones we're looking for
            if component.custom_id in ["1", "2"]:
                # Remove the component from the view
                view.remove_item(component)
    
    await interaction.response.send_message(f"You have refused the challenge by {challenger.name}!", ephemeral=True)
    await challenger.send(f"Your challenge to {opponent_nick} has been refused.")




# CHALLENGE COMMAND
@bot.command()
async def challenge(ctx, opponent_nick):
    await ctx.send(f"You are trying to challenge {opponent_nick} to ft7!")

    # STORE CHALLENGER AND OPPONENT AS VARIABLES
    opponent = discord.utils.get(ctx.guild.members, nick=opponent_nick)
    if opponent is None:
        opponent = discord.utils.get(ctx.guild.members, name=opponent_nick)
    challenger = ctx.author

    # VIEWS AND BUTTONS
    accept_view = discord.ui.View()

    accept_button = MyButton(custom_id="1", label="Accept!", style=ButtonStyle.success, callback_function=accept_duel)
    refuse_button = MyButton(custom_id="2", label="Refuse!", style=ButtonStyle.danger, callback_function=lambda interaction: refuse_duel(interaction, accept_view, challenger, opponent_nick))

    # CHALLENGE MESSAGES
    challenger_name = ctx.author.nick
    if ctx.author.nick is None:
        challenger_name = ctx.author.name

    challenger_message = f"```You have challenged {opponent_nick} to ft7!```"
    opponent_message = f"```You have been challenged to ft7 by {challenger_name}! If you accept, both of you get to select win, stalemate or loss for yourselves.```"
    

    # MAKE SURE ONE DOESN'T CHALLENGE THEMSELF
    #if opponent == ctx.author:
    #    await ctx.send("It seems you tried to challenge yourself! If there is a bug, please contact Ludus admins.")

    # IF OPPONENT EXISTS: (CHANGE TO ELIF IF CHALLENGING THEMSELF IS BANNED)
    if opponent:
        await ctx.send(f"Opponent has been found. If he will accept the challenge, you both get to select win, stalemate or loss for yourselves.")
        
        accept_view.add_item(accept_button)
        accept_view.add_item(refuse_button)
        await ctx.author.send(challenger_message)
        await opponent.send(opponent_message, view=accept_view)

    # IF OPPONENT DOES NOT EXIST
    else:
        await ctx.send("The opponent you selected does not exist! Try their real discord name if nick not work.")


# TOKEN OF BOT TO IDENTIFY AND USE IN CHANNELS
token = settings.bot_token
bot.run(token)
