# ludusbot.py
# Made by Chinese Parrot 25th july 2024

import random
import psycopg2
import discord
import settings
import facts
from discord.ext import commands
from discord import app_commands
import asyncio

# OPEN THE CONNECTION TO THE DATABASE
conn = psycopg2.connect(
        database = settings.db_name,
        user = settings.db_user,
        password = settings.db_password,
        host = settings.db_host,
        port = settings.db_port
)
conn.autocommit = True

# GIVE BOT DEFAULT INTENTS + ACCESS TO MESSAGE CONTENT AND MEMBERS AND SET COMMAND PREFIX TO BE '/'
intents = discord.Intents.default()  
intents.message_content = True 
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)  # use slash as start of command

# BOT ENTERS THE CHANNEL
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    bot.tree.clear_commands(guild=None) 
    await bot.tree.sync()
    print("Slash commands have been cleared and updated.")


# ------- PRIVATE VARIABLES -----------
challenge_status = []


# -------- PRIVATE FUNCTIONS -----------

# USE THIS TO CHECK IF REGISTERED
async def is_registered(discord_id: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE discord_id = %s", (discord_id,))
    existing_user = cursor.fetchone()

    if existing_user is not None: # user is registered
        return True
    
    return False # user is not registered
# is registered ends


# UPDATE PLAYER POINTS IN DATABASE
async def update_player_points(channel, challenger, opponent, challenger_win: bool):

    # THESE CAN BE MODIFIED AS NEED
    standard_point_change = 30

    # FETCH CURRENT POINTS FROM DATABASE
    cursor = conn.cursor()

    cursor.execute("SELECT battles, wins, average_enemy_rank, points FROM players WHERE discord_id = %s", (str(challenger.id),))
    result = cursor.fetchone()
    challenger_stats = {
        'battles': result[0],
        'wins': result[1],
        'average_enemy_rank': result[2],
        'current_points': result[3]
    }
    cursor.execute("SELECT battles, wins, average_enemy_rank, points FROM players WHERE discord_id = %s", (str(opponent.id),))
    result = cursor.fetchone()
    opponent_stats = {
        'battles': result[0],
        'wins': result[1],
        'average_enemy_rank': result[2],
        'current_points': result[3]
    }
    
    # CALCULATE TOTAL POINT CHANGE, AND THEN, HOW MANY 100p DIFFERENCES (POINT_lEVELS) THERE ARE
    point_difference = abs(challenger_stats['current_points'] - opponent_stats['current_points'])

    point_levels = point_difference // 50


    # INITIATE NEW POINTS, AND THEN CALCULATE THE NEW POINTS BASED ON THE FORMULA
    challenger_new_points = challenger_stats['current_points']
    opponent_new_points = opponent_stats['current_points']

    # IF CHALLENGER WINS
    if challenger_win:
        # update both players battles, wins, average_enemy_rank
        challenger_stats["average_enemy_rank"] = (challenger_stats["battles"] * challenger_stats["average_enemy_rank"] + opponent_stats["current_points"]) / (challenger_stats["battles"] + 1)
        challenger_stats["battles"] = challenger_stats["battles"] + 1
        challenger_stats["wins"] = challenger_stats["wins"] + 1

        opponent_stats["average_enemy_rank"] = (opponent_stats["battles"] * opponent_stats["average_enemy_rank"] + challenger_stats["current_points"]) / (opponent_stats["battles"] + 1)
        opponent_stats["battles"] = opponent_stats["battles"] + 1

        # solve point change amount for both players
        if challenger_stats['current_points'] > opponent_stats['current_points']:
            point_change = max(standard_point_change - point_levels, 1)
            challenger_new_points = challenger_stats['current_points'] + point_change # challenger gains points
            opponent_new_points = opponent_stats['current_points'] - point_change # opponent loses points

        elif challenger_stats['current_points'] < opponent_stats['current_points']:
            point_change = standard_point_change + point_levels
            challenger_new_points = challenger_stats['current_points'] + point_change # challenger gains points
            opponent_new_points = opponent_stats['current_points'] - point_change # opponent loses points

        else:
            challenger_new_points = challenger_stats['current_points'] + standard_point_change
            opponent_new_points = opponent_stats['current_points'] - standard_point_change

    # IF OPPONENT WINS
    else:
        # update both players battles, wins, average_enemy_rank
        opponent_stats["average_enemy_rank"] = (opponent_stats["battles"] * opponent_stats["average_enemy_rank"] + challenger_stats["current_points"]) / (opponent_stats["battles"] + 1)
        opponent_stats["battles"] = opponent_stats["battles"] + 1
        opponent_stats["wins"] = opponent_stats["wins"] + 1

        challenger_stats["average_enemy_rank"] = (challenger_stats["battles"] * challenger_stats["average_enemy_rank"] + opponent_stats["current_points"]) / (challenger_stats["battles"] + 1)
        challenger_stats["battles"] = challenger_stats["battles"] + 1

        # solve point change amount for both players
        if challenger_stats['current_points'] > opponent_stats['current_points']:
            point_change = standard_point_change + point_levels
            opponent_new_points = opponent_stats['current_points'] + point_change # opponent gains points
            challenger_new_points = challenger_stats['current_points'] - point_change # challenger loses points
            
        elif challenger_stats['current_points'] < opponent_stats['current_points']:
            point_change = max(standard_point_change - point_levels, 1)
            opponent_new_points = opponent_stats['current_points'] + point_change # opponent gains points
            challenger_new_points = challenger_stats['current_points'] - point_change # challenger loses points

        else:
            challenger_new_points = challenger_stats['current_points'] - standard_point_change
            opponent_new_points = opponent_stats['current_points'] + standard_point_change

    # STORE THE NEW POINTS TO DATABASE AS POINTS, AND CURRENT POINTS AND OLD_POINTS

    # update challenger points
    cursor.execute("UPDATE players SET battles = %s, wins = %s, average_enemy_rank = %s, points = %s, old_points = %s WHERE discord_id = %s", (challenger_stats['battles'], challenger_stats['wins'], challenger_stats['average_enemy_rank'], challenger_new_points, challenger_stats['current_points'], str(challenger.id),))

    # update opponent points
    cursor.execute("UPDATE players SET battles = %s, wins = %s, average_enemy_rank = %s, points = %s, old_points = %s WHERE discord_id = %s", (opponent_stats['battles'], opponent_stats['wins'], opponent_stats['average_enemy_rank'], opponent_new_points, opponent_stats['current_points'], str(opponent.id),))

    # FEEDBACK USERS OF THEIR OLD AND NEW POINTS
    new_scores_tittle = "***** NEW SCORES *****"
    await channel.send(f"{new_scores_tittle.center(24)}")
    await channel.send(f"Challenger {challenger.mention} old_points are: {challenger_stats['current_points']}. \n Challenger {challenger.mention} new points are {challenger_new_points} \n")
    await channel.send(f"Opponent {opponent.mention} old_points are: {opponent_stats['current_points']}. \n Opponent {opponent.mention} new points are {opponent_new_points}")

    return 
# update player points ends


async def print_facts(ctx, language):
    answer = ""
    if (language.lower() == 'eng'):
        answer = random.choice(facts.facts_eng)
    elif (language.lower() == 'rus'):
        answer = random.choice(facts.facts_rus)
    else:
        await ctx.send(f"Given language {language} did not match language options. Try for example '/factual eng' or '/factual rus'.")
        return
    return await ctx.send(answer)  


# ------- BOT COMMANDS (PUBLIC FUNCTIONS) ---------------

# FACTUAL ENG COMMAND
@bot.command()
async def factual(ctx):
    answer = random.choice(facts.facts_eng)
    await ctx.send(answer)  
# factual eng ends

# FACTUAL ENG COMMAND
@bot.command()
async def фактически(ctx):
    answer = random.choice(facts.facts_rus)
    await ctx.send(answer)  
# factual rus ends


# REGISTER COMMAND
@bot.command()
async def register(ctx, nickname):
    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)
    # NOTIFY USER THEY ARE ALREADY REGISTERED
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        await ctx.send("You have already been registered! If you want to reset your rank, please contact admins.")
    # ADD A NEW USER
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players", ())
        amount_of_lines = cursor.fetchone()[0]
        if (amount_of_lines < 10000):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, points, nickname, discord_id, old_points, battles, wins, average_enemy_rank) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (username, 1000, nickname, str(ctx.author.id), 1000, 0, 0, 0))
            await ctx.send("Your discord account has successfully been registered to participate ranked battles!")
        else:
            await ctx.send("The database is full. Please contact admins.")
# register ends


# CHANGENICK COMMAND
@bot.command()
async def changenick(ctx, nickname):
    # IF USERNAME EXISTS IN DATABASE, CHANGE THEIR NICKNAME
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_nickname = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET nickname = %s WHERE discord_id = %s", (nickname, str(ctx.author.id)))
        await ctx.send(f"Your nickname has been updated! Your old nickname was {old_nickname}. Your new nickname is {nickname}")
# change nickname ends


# CHANGECLAN COMMAND
@bot.command()
async def changeclan(ctx, clanname):
    # IF USER ID EXISTS IN DATABASE, CHANGE THEIR CLANNAME
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        cursor = conn.cursor()
        cursor.execute("SELECT clanname FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_clanname = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET clanname = %s WHERE discord_id = %s", (clanname, str(ctx.author.id)))
        await ctx.send(f"Your nickname has been updated! Your old clanname was {old_clanname}. Your new nickname is {clanname}")
# change clanname ends


# MYSCORE COMMAND
@bot.command()
async def myscore(ctx):
    is_registered_result = is_registered(str(ctx.author.id))
    if not is_registered_result:
        ctx.send(f"You have not yet registered. Please register by writing /register nickname. If problem persists contact admins.")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, points, battles, wins, average_enemy_rank, clanname FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    score = cursor.fetchone()
    stats = {
        'nickname': score[0],
        'points': score[1],
        'battles': score[2],
        'wins': score[3],
        'average_enemy_rank': score[4],
        "clanname": score[5]
    }
    if stats["battles"] > 0:
        await ctx.send(f"Your {ctx.author.mention} current stats are: \n points: {stats['points']}, \n winrate: {(stats['wins'] / stats['battles'])*100}%, \n battles: {stats['battles']}, \n avrg enemy rank: {round(stats['average_enemy_rank'], 0)}, \n clanname: {stats['clanname']}")
    else:
        await ctx.send(f"Your {ctx.author.mention} current stats are: \n points: {stats['points']}, \n winrate: 0%, \n battles: {stats['battles']}, \n avrg_enemy_rank: {round(stats['average_enemy_rank'], 0)}, \n clanname: {stats['clanname']}")
# myscore ends


# TOP X COMMAND
# for example, user gives '/top 10' and bot gives scores of top10 players
@bot.command()
async def top(ctx, number):
    # if number not numeric, info user
    if not number.isdigit():
        await ctx.send("You must give after 'top' command a number, for example '/top 10' or '/top 15'")
        return

    number = int(number)
    scoreboard_text = f"SCOREBOARD TOP{number} PLAYERS"
    await ctx.send("```**" + scoreboard_text.center(24) + "**```")

    cursor = conn.cursor()
    cursor.execute("SELECT nickname, points, battles, wins, average_enemy_rank, clanname FROM players ORDER BY points DESC",())

    scores_per_player = []
    top_players = cursor.fetchmany(number)
    
    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        wins = item[3]
        if (item[2] > 0):
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {(item[3] / item[2]) * 100}%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        else:
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    await ctx.send("\n".join(scores_per_player))
    await ctx.send(f"```** Top{number} players have been printed! **```")
# top X ends


# CLANTOP X COMMAND
@bot.command()
async def clantop(ctx, number, clanname):
    # if number is not numeric, info user
    if not number.isdigit():
        await ctx.send("You must give after 'top' command a number, for example '/clantop 10 Marchia' or '/clantop 15 Marchia'")
        return

    number = int(number)
    scoreboard_text = f"SCOREBOARD TOP{number} PLAYERS"
    await ctx.send("```**" + scoreboard_text.center(24) + "**```")

    cursor = conn.cursor()
    cursor.execute("SELECT nickname, points, battles, wins, average_enemy_rank, clanname FROM players WHERE clanname = %s ORDER BY points DESC", (clanname,))

    scores_per_player = []
    top_players = cursor.fetchmany(number)

    if (len(top_players) < 1):
        await ctx.send(f"No players were found with clanname: '{clanname}'. Maybe there is a typo. For example, small and large letters are considered separate.")
        return

    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        wins = item[3]
        if (item[2] > 0):
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {(item[3] / item[2]) * 100}%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        else:
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    await ctx.send("\n".join(scores_per_player))
    await ctx.send(f"```** Top{number} players have been printed! **```")
# top X ends


# CHALLENGE COMMAND
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
# challenge ends



# TOKEN OF BOT TO IDENTIFY AND USE IN CHANNELS
token = settings.bot_token
bot.run(token)
