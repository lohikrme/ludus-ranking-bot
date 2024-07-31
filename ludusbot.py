# ludusbot.py
# Made by Chinese Parrot 25th july 2024

import random
import psycopg2
import discord
import settings
from discord.ext import commands
import asyncio

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
                "KRAAAK!",
                "Kraak",
                "Kraa",
                "KRAAA!",
                "KRAAAAK KRAAK!",
                "KRAAAA KRA KRA KRRRAAAAAAAAAAAAK!",
                "Polly wants a cracker!"

                ]
    
    answer = random.choice(commands)
    await ctx.send(answer)


# USE THIS TO CHECK IF REGISTERED
async def is_registered(discord_id: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE discord_id = %s", (discord_id,))
    existing_user = cursor.fetchone()

    if existing_user is not None: # user is registered
        return True
    
    return False # user is not registered

# REGISTER COMMAND
@bot.command()
async def register(ctx, nickname):
    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)

    # NOTIFY USER THEY ARE ALREADY REGISTERED
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        await ctx.send("You have already been registered! If you want to reset your rank, please contact Ludus admins.")

    # ADD A NEW USER
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players", ())
        amount_of_lines = cursor.fetchone()[0]
        if (amount_of_lines < 10000):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, points, nickname, discord_id, old_points) VALUES (%s, %s, %s, %s, %s)", (username, 1000, nickname, str(ctx.author.id), 1000))
            await ctx.send("Your discord username has successfully been registered into Ludus players!")
        else:
            await ctx.send("The database is full. This most likely means that the database has been attacked by a spammer. \n This will not endanger security, but limit makes sure database wont grow too large. Please contact Ludus admins.")


# CHANGENICKNAME COMMAND
@bot.command()
async def changeNickName(ctx, nickname):

    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)

    # IF USERNAME EXISTS, CHANGE THEIR NICKNAME
    is_registered_result = await is_registered(str(ctx.author.id))

    if is_registered_result:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_nickname = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET nickname = %s WHERE discord_id = %s", (nickname, str(ctx.author.id)))
        await ctx.send(f"Your nickname has been updated! Your old nickname was {old_nickname}. Your new nickname is {nickname}")


# MYSCORE COMMAND
@bot.command()
async def myscore(ctx):
    is_registered_result = is_registered(str(ctx.author.id))
    if not is_registered_result:
        ctx.send(f"You have not yet registered. Please register by writing /register nickname. If problem persists contact admins.")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, points FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    score = str(cursor.fetchone())
    await ctx.send(f"Your score is {score}")

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


# UPDATE PLAYER POINTS IN DATABASE
async def update_player_points(channel, challenger, opponent, challenger_win: bool):

    # THESE CAN BE MODIFIED AS NEED
    standard_point_change = 30
    level_factor = 2

    # FETCH CURRENT POINTS FROM DATABASE
    cursor = conn.cursor()
    cursor.execute("SELECT points FROM players WHERE discord_id = %s", (str(challenger.id),))
    challenger_current_points = cursor.fetchone()[0]
    cursor.execute("SELECT points FROM players WHERE discord_id = %s", (str(opponent.id),))
    opponent_current_points = cursor.fetchone()[0]
    
    # CALCULATE TOTAL POINT CHANGE, AND THEN, HOW MANY 100p DIFFERENCES (POINT_lEVELS) THERE ARE
    point_difference = abs(challenger_current_points - opponent_current_points)

    point_levels = point_difference // 50


    # INITIATE NEW POINTS, AND THEN CALCULATE THE NEW POINTS BASED ON THE FORMULA
    challenger_new_points = challenger_current_points
    opponent_new_points = opponent_current_points

    # IF CHALLENGER WINS
    if challenger_win:
        if challenger_current_points > opponent_current_points:
            point_change = max(standard_point_change - point_levels, 1)
            challenger_new_points = challenger_current_points + point_change # challenger gains points
            opponent_new_points = opponent_current_points - point_change # opponent loses points

        elif challenger_current_points < opponent_current_points:
            point_change = standard_point_change + point_levels
            challenger_new_points = challenger_current_points + point_change # challenger gains points
            opponent_new_points = opponent_current_points - point_change # opponent loses points

        else:
            challenger_new_points = challenger_current_points + standard_point_change
            opponent_new_points = opponent_current_points - standard_point_change

    # IF OPPONENT WINS
    else:
        if challenger_current_points > opponent_current_points:
            point_change = standard_point_change + point_levels
            opponent_new_points = opponent_current_points + point_change # opponent gains points
            challenger_new_points = challenger_current_points - point_change # challenger loses points
            
        elif challenger_current_points < opponent_current_points:
            point_change = max(standard_point_change - point_levels, 1)
            opponent_new_points = opponent_current_points + point_change # opponent gains points
            challenger_new_points = challenger_current_points - point_change # challenger loses points

        else:
            challenger_new_points = challenger_current_points - standard_point_change
            opponent_new_points = opponent_current_points + standard_point_change

    # STORE THE NEW POINTS TO DATABASE AS POINTS, AND CURRENT POINTS AND OLD_POINTS

    # update challenger points
    cursor.execute("UPDATE players SET points = %s, old_points = %s WHERE discord_id = %s", (challenger_new_points, challenger_current_points, str(challenger.id),))

    # update opponent points
    cursor.execute("UPDATE players SET points = %s, old_points = %s WHERE discord_id = %s", (opponent_new_points, opponent_current_points, str(opponent.id),))


    # FEEDBACK USERS OF THEIR OLD AND NEW POINTS
    new_scores_tittle = "***** NEW SCORES *****"
    await channel.send(f"{new_scores_tittle.center(24)}")
    await channel.send(f"Challenger {challenger.mention} old_points are: {challenger_current_points}. \n Challenger {challenger.mention} new points are {challenger_new_points} \n")
    await channel.send(f"Opponent {opponent.mention} old_points are: {opponent_current_points}. \n Opponent {opponent.mention} new points are {opponent_new_points}")


    return



# CHALLENGE COMMAND
challenge_status = []


@bot.command()
async def challenge(ctx, opponent: discord.Member):
    global challenge_status

    # CHECK NOT CHALLENGE ONESELF
    if (opponent.id == ctx.author.id):
        await ctx.send("You may not challenge yourself!")
        return

    # CHECK CHALLENGER AND OPPONENT ARE REGISTERED, OTHERWISE NOTIFY AND RETURN
    opponent_is_registered = await is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.send(f"The opponent {opponent.mention} has not yet been registered. Ask him to register before duel.")
        return
    
    challenger_is_registered = await is_registered(str(ctx.author.id))
    if not challenger_is_registered:
        await ctx.send(f"The challenger {ctx.author.mention} has not yet been registered. Please register to be able to duel.")
        return
    
    if (ctx.author.id in challenge_status):
        await ctx.send(f"You {ctx.author.mention} have already challenged somebody. Please cancel that before challenging a new player.")
        return
    

    challenge_status.append(ctx.author.id)
    # Step 1: Initial Challenge Message
    challenge_embed = discord.Embed(title="Challenge Sent!",
                                    description=f"{ctx.author.mention} has challenged {opponent.mention} to a duel! {opponent.mention} should click swords emoticon if they want to accept the ft7!")
    challenge_msg = await ctx.send(embed=challenge_embed)

    # Add reactions for Accept, Decline, Cancel
    await challenge_msg.add_reaction("⚔️")  # Accept
    await challenge_msg.add_reaction("🚫")  # Cancel
    

    # Wait for a reaction
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: u == opponent and str(r.emoji) in ["⚔️", "🚫"])
    except asyncio.TimeoutError:
        challenge_status.remove(ctx.author.id)
        await ctx.send("Challenge expired.")
        return

    # Handle reactions
    if str(reaction.emoji) == "⚔️":
        await ctx.send("Challenge accepted!")
        
        opponent_results_embed = discord.Embed(title="Opponent reports results!",
        description=f"The opponent {opponent.mention} is supposed to answer this message! If challenger {ctx.author.mention} won press dagger emoticon! If opponent {opponent.mention} won press castle emoticon. If duel was cancelled press red emoticon.")
        opponent_msg = await ctx.send(embed=opponent_results_embed)
        await opponent_msg.add_reaction("🗡️") # challenger won
        await opponent_msg.add_reaction("🏰") # opponent won
        await opponent_msg.add_reaction("🚫") # cancel

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=lambda r, u: u == opponent and str(r.emoji) in ["🗡️", "🏰", "🚫"])
        except asyncio.TimeoutError:
            challenge_status.remove(ctx.author.id)
            await ctx.send("FT7 expired.")
            return
        
        if str(reaction.emoji) == "🗡️":
            challenge_status.remove(ctx.author.id)
            await ctx.send(f"Challenger {ctx.author.mention} has won the duel against the opponent {opponent.mention}!")
            await update_player_points(ctx, ctx.author, opponent, True)
        elif str(reaction.emoji) == "🏰":
            challenge_status.remove(ctx.author.id)
            await ctx.send(f"Opponent {opponent.mention} has won the duel against the challenger {ctx.author.mention}!")
            await update_player_points(ctx, ctx.author, opponent, False)
        elif str(reaction.emoji) == "🚫":
            challenge_status.remove(ctx.author.id)
            await ctx.send(f"The FT7 has been cancelled between the challenger {ctx.author.mention} and the opponent {opponent.mention}!")


        # Proceed to result selection
    elif str(reaction.emoji) == "🚫":
        await ctx.send("Challenge canceled.")
        challenge_status.remove(ctx.author.id)

    # Further steps (result selection, verification, database update) would follow here...



# TOKEN OF BOT TO IDENTIFY AND USE IN CHANNELS
token = settings.bot_token
bot.run(token)
