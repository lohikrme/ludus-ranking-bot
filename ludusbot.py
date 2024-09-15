# ludusbot.py
# Made by Chinese Parrot 25th july 2024

import random
import psycopg2
import discord
import settings
import facts
import guides
from discord.ext import commands
import asyncio
import datetime

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

guilds = [
    1060303582487908423, # middle-earth
    1194360639544635482 # legion
]

# BOT ENTERS THE CHANNEL
@bot.event
async def on_connect():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.sync_commands(guild_ids=guilds)
    print("Slash commands have been cleared and updated... Wait a bit more before bot is ready...")
    print("Bot is finally ready to function!")


# -------- PRIVATE FUNCTIONS -----------

# USE THIS TO UPDATE DUELS DATATABLE HISTORY
async def update_duels_history(challenger_discord_id: str, opponent_discord_id: str, challenger_won: bool):
    date = datetime.datetime.now()
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO duels (date, challenger_discord_id, opponent_discord_id, challenger_won) VALUES (%s, %s, %s, %s)", (date, challenger_discord_id, opponent_discord_id, challenger_won))
# update duels history ends  
  

# USE THIS TO CHECK IF USER REGISTERED
async def is_registered(discord_id: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE discord_id = %s", (discord_id,))
    existing_user = cursor.fetchone()

    if existing_user is not None: # user is registered
        return True
    
    return False # user is not registered
# is registered ends


# USE TO INFO USER OF EXISTING CLANNAMES
async def fetchExistingClannames():
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM clans", ())
    clannames = cursor.fetchall()
    current_clans = []
    for item in clannames:
        current_clans.append(item[0])
    return current_clans
# fetch existing clannames ends


# UPDATE CLAN POINTS IN DATABASE
async def update_clan_points(challenger_clan_id: int, defender_clan_id: int, challenger_win: bool):
    # these can be updated as need
    standard_point_change = 20
    point_level_divident = 60
    minimum_point_change = 2

    # fetch current points from database
    cursor = conn.cursor()
    cursor.execute("SELECT battles, wins, average_enemy_rank, points FROM clans WHERE id = %s", (challenger_clan_id,))
    result = cursor.fetchone()
    challenger_stats = {
        'battles': result[0],
        'wins': result[1],
        'average_enemy_rank': result[2],
        'current_points': result[3]
    }
    cursor.execute("SELECT battles, wins, average_enemy_rank, points FROM clans WHERE id = %s", (defender_clan_id,))
    result = cursor.fetchone()
    defender_stats = {
        'battles': result[0],
        'wins': result[1],
        'average_enemy_rank': result[2],
        'current_points': result[3]
    }
    
    # CALCULATE TOTAL POINT CHANGE, AND THEN, HOW MANY 100p DIFFERENCES (POINT_lEVELS) THERE ARE
    point_difference = abs(challenger_stats['current_points'] - defender_stats['current_points'])

    point_levels = point_difference // point_level_divident

    # INITIATE NEW POINTS, AND THEN CALCULATE THE NEW POINTS BASED ON THE FORMULA
    challenger_new_points = challenger_stats['current_points']
    opponent_new_points = defender_stats['current_points']

    # IF CHALLENGER WINS
    if challenger_win:
        # update both clans battles, wins, average_enemy_rank
        challenger_stats["average_enemy_rank"] = (challenger_stats["battles"] * challenger_stats["average_enemy_rank"] + defender_stats["current_points"]) / (challenger_stats["battles"] + 1)
        challenger_stats["battles"] = challenger_stats["battles"] + 1
        challenger_stats["wins"] = challenger_stats["wins"] + 1

        defender_stats["average_enemy_rank"] = (defender_stats["battles"] * defender_stats["average_enemy_rank"] + challenger_stats["current_points"]) / (defender_stats["battles"] + 1)
        defender_stats["battles"] = defender_stats["battles"] + 1

        # solve point change amount for both players
        if challenger_stats['current_points'] > defender_stats['current_points']:
            point_change = max(standard_point_change - point_levels, minimum_point_change)
            challenger_new_points = challenger_stats['current_points'] + point_change # challenger gains points
            opponent_new_points = defender_stats['current_points'] - point_change # opponent loses points

        elif challenger_stats['current_points'] < defender_stats['current_points']:
            point_change = standard_point_change + point_levels
            challenger_new_points = challenger_stats['current_points'] + point_change # challenger gains points
            opponent_new_points = defender_stats['current_points'] - point_change # opponent loses points

        else:
            challenger_new_points = challenger_stats['current_points'] + standard_point_change
            opponent_new_points = defender_stats['current_points'] - standard_point_change

    # IF DEFENDER WINS
    else:
        # update both players battles, wins, average_enemy_rank
        defender_stats["average_enemy_rank"] = (defender_stats["battles"] * defender_stats["average_enemy_rank"] + challenger_stats["current_points"]) / (defender_stats["battles"] + 1)
        defender_stats["battles"] = defender_stats["battles"] + 1
        defender_stats["wins"] = defender_stats["wins"] + 1

        challenger_stats["average_enemy_rank"] = (challenger_stats["battles"] * challenger_stats["average_enemy_rank"] + defender_stats["current_points"]) / (challenger_stats["battles"] + 1)
        challenger_stats["battles"] = challenger_stats["battles"] + 1

        # solve point change amount for both players
        if challenger_stats['current_points'] > defender_stats['current_points']:
            point_change = standard_point_change + point_levels
            opponent_new_points = defender_stats['current_points'] + point_change # opponent gains points
            challenger_new_points = challenger_stats['current_points'] - point_change # challenger loses points
            
        elif challenger_stats['current_points'] < defender_stats['current_points']:
            point_change = max(standard_point_change - point_levels, minimum_point_change)
            opponent_new_points = defender_stats['current_points'] + point_change # opponent gains points
            challenger_new_points = challenger_stats['current_points'] - point_change # challenger loses points

        else:
            challenger_new_points = challenger_stats['current_points'] - standard_point_change
            opponent_new_points = defender_stats['current_points'] + standard_point_change
    
    # STORE THE NEW_POINTS TO DATABASE AS POINTS, AND CURRENT_POINTS AS OLD_POINTS

    # update challenger points
    cursor.execute("UPDATE clans SET battles = %s, wins = %s, average_enemy_rank = %s, points = %s, old_points = %s WHERE id = %s", (challenger_stats['battles'], challenger_stats['wins'], challenger_stats['average_enemy_rank'], challenger_new_points, challenger_stats['current_points'], challenger_clan_id,))
    # update defender points
    cursor.execute("UPDATE clans SET battles = %s, wins = %s, average_enemy_rank = %s, points = %s, old_points = %s WHERE id = %s", (defender_stats['battles'], defender_stats['wins'], defender_stats['average_enemy_rank'], opponent_new_points, defender_stats['current_points'], defender_clan_id,))
    return 
# update clan points ends


# UPDATE PLAYER POINTS IN DATABASE
async def update_player_points(challenger, opponent, challenger_win: bool):

    # these can be updated as need
    standard_point_change = 20
    point_level_divident = 60
    minimum_point_change = 2

    # fetch current points from database
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

    point_levels = point_difference // point_level_divident


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
            point_change = max(standard_point_change - point_levels, minimum_point_change)
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
            point_change = max(standard_point_change - point_levels, minimum_point_change)
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
    return 
# update player points ends



# ------- BOT COMMANDS (PUBLIC FUNCTIONS) ---------------

# GUIDE IN ENGLISH
@bot.slash_command(name="guide", description="Teaches commands of ludus-ranking-bot with English!")
async def guide(ctx):
    await ctx.respond(guides.guide_eng)
# guide in english ends

# GUIDE IN RUSSIAN
@bot.slash_command(name="гид", description="Обучает команды ludus-ranking-bot на русском языке!")
async def гид(ctx):
    await ctx.respond(guides.guide_rus)
# guide in russian ends

# GUIDE IN TURKISH
@bot.slash_command(name="rehber", description="ludus-ranking-bot komutlarını İngilizce ile öğretir!")
async def rehber(ctx):
    await ctx.respond(guides.guide_tr)
# guide in turkish ends

# FACTUAL ENG COMMAND
@bot.slash_command(name="factual", description="Bot will tell interesting facts!")
async def factual(ctx):
    answer = random.choice(facts.facts_eng)
    await ctx.respond(answer)  
# factual eng ends

# FACTUAL RUS COMMAND
@bot.slash_command(name="факт", description="Бот расскажет интересные факты!")
async def факт(ctx):
    answer = random.choice(facts.facts_rus)
    await ctx.respond(answer)  
# factual rus ends

# FACTUAL TR COMMAND
@bot.slash_command(name="gerçekler", description="Bot ilginç gerçekleri anlatacak")
async def gerçekler(ctx):
    answer = random.choice(facts.facts_tr)
    await ctx.respond(answer)  
# factual tr ends


# REGISTER PLAYER COMMAND
@bot.slash_command(name="registerplayer", description="Register yourself as a player!")
async def registerplayer(ctx, nickname: str):
    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)
    # NOTIFY USER THEY ARE ALREADY REGISTERED
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        await ctx.respond("You have already been registered! \nIf you want to reset your rank, please contact admins.")
    # ADD A NEW USER
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players", ())
        amount_of_lines = cursor.fetchone()[0]
        if (amount_of_lines < 10000):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, nickname, discord_id) VALUES (%s, %s, %s)", (username, nickname, str(ctx.author.id),))
            await ctx.respond(f"Your discord account has successfully been registered with nickname '{nickname}'! Nickname can be changed easily.")
        else:
            await ctx.respond("The database is full. Please contact admins.")
# register player ends


# REGISTER CLAN COMMAND
@bot.slash_command(name="registerclan", description="Add a new clanname before using clanname to other commands.")
async def registerclan(ctx, clanname: str):
    clanname = clanname.lower()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clans WHERE name = %s", (clanname,))
    existing_clan = cursor.fetchone()

    if existing_clan is not None:
        await ctx.respond(f"The clanname {clanname} already exists")
        return
    
    cursor.execute("INSERT INTO clans (name) VALUES (%s)", (clanname,))
    await ctx.respond(f"The clanname '{clanname}' has successfully been registered!")
    return
# registerclan ends


# REGISTER ADMIN COMMAND
@bot.slash_command(name="registeradmin", description="Register as admin to be able to use admin commands!")
async def registeradmin(ctx, password:str):
    if (password != settings.leaderpassword):
        await ctx.respond("You have given a wrong password. \nAsk Legion clan if you want to become an admin.")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    alreadyin = cursor.fetchone()
    if alreadyin is not None:
        await ctx.respond("You are already an admin!")
        return
    else:
        cursor.execute("INSERT INTO admins (discord_id) VALUES (%s)", (str(ctx.author.id),))
        await ctx.respond("Congratulations, your admin registration has been accepted!")
        return
# register admin ends


# CHANGEYOURNICKNAME COMMAND
@bot.slash_command(name="changeyournickname", description="Give yourself a new nickname!")
async def changeyournickname(ctx, nickname: str):
    # IF USERNAME EXISTS IN DATABASE, CHANGE THEIR NICKNAME
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_nickname = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET nickname = %s WHERE discord_id = %s", (nickname, str(ctx.author.id)))
        await ctx.respond(f"Your nickname has been updated! \nOld nickname: '{old_nickname}'. \nNew nickname: '{nickname}'")
        return
    else:
        await ctx.respond(f"Register before using this command or contact admins.")
        return
# change your nickname ends


# CHANGE YOUR CLAN COMMAND
@bot.slash_command(name="changeyourclan", description="Give yourself a new clanname!")
async def changeyourclan(ctx, new_clanname: str):
    new_clanname = new_clanname.lower()
    # IF USER ID EXISTS IN DATABASE, CHANGE THEIR CLANNAME
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        existing_clans = await fetchExistingClannames()
        if new_clanname not in existing_clans:
            await ctx.respond(f"'{new_clanname}' is not part of existing clans: \n{existing_clans} \nPlease use '/registerclan' to create a new clanname.")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_clan_id = cursor.fetchone()[0]
        cursor.execute("SELECT name FROM clans WHERE id = %s", (old_clan_id,))
        old_clanname = cursor.fetchone()[0]
        if (new_clanname == old_clanname):
            await ctx.respond(f"You already belong to the clan '{new_clanname}'")
            return
        else:
            cursor.execute("SELECT id FROM clans WHERE name = %s", (new_clanname,))
            new_clan_id = cursor.fetchone()[0]
            cursor.execute("UPDATE players SET clan_id = (%s)", (new_clan_id,))
            await ctx.respond(f"Your clanname has been updated! \nOld clanname: '{old_clanname}'. \nNew clanname: '{new_clanname}'")
            return
    else:
        await ctx.respond(f"Register before using this command or contact admins.")
        return
# change your clan ends


# MYSCORE COMMAND
@bot.slash_command(name="myscore", description="Print your personal scores!")
async def myscore(ctx):
    is_registered_result = await is_registered(str(ctx.author.id))
    if not is_registered_result:
        await ctx.respond(f"Register before using this command or contact admins.")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, points, battles, wins, average_enemy_rank, clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    score = cursor.fetchone()
    stats = {
        'nickname': score[0],
        'points': score[1],
        'battles': score[2],
        'wins': score[3],
        'average_enemy_rank': score[4],
        "clan_id": score[5]
    }
    cursor.execute("SELECT name FROM clans WHERE id = %s", (stats["clan_id"],))
    clanname = cursor.fetchone()[0]
    if stats["battles"] > 0:
        await ctx.respond(f"```{ctx.author.display_name}'s current stats are: \n  points: {stats['points']}, \n  winrate: {round((stats['wins'] / stats['battles'])*100, 2)}%, \n  battles: {stats['battles']}, \n  avrg enemy rank: {round(stats['average_enemy_rank'], 0)}, \n  clanname: {clanname}```")
    else:
        await ctx.respond(f"```{ctx.author.display_name}'s current stats are: \n  points: {stats['points']}, \n  winrate: 0%, \n  battles: {stats['battles']}, \n  avrg_enemy_rank: {round(stats['average_enemy_rank'], 0)}, \n  clanname: {clanname}```")
# myscore ends


# LEADERBOARD PLAYERS COMMAND
@bot.slash_command(name="leaderboardplayers", description="Print top players of all players!")
async def playerleaderboard(ctx, number: int):
    scores_per_player = []
    scores_per_player.append("``` ** LEADERBOARD OF PLAYERS **```")

    cursor = conn.cursor()
    cursor.execute("""SELECT players.nickname, players.points, players.battles, players.wins, players.average_enemy_rank, clans.name 
                   FROM players 
                   LEFT JOIN clans ON players.clan_id = clans.id 
                   ORDER BY points DESC""",())

    top_players = cursor.fetchmany(number)
    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        if (item[2] > 0):
            printable_text = f"        RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {round((item[3] / item[2]) * 100, 2)}%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        else:
            printable_text = f"        RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    scores_per_player.append(f"```  ** TOP{number} PLAYERS HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_player))
# player leaderboard ends


# LEADERBOARD PLAYERS OF CLAN COMMAND
@bot.slash_command(name="leaderboardplayersofclan", description="Print top players of a specific clan!")
async def leaderboardplayersofclan(ctx, number: int, clanname: str):
    scores_per_player = []
    scores_per_player.append(f"``` ** LEADERBOARD PLAYERS OF {clanname.upper()} **```")

    clanname = clanname.lower()
    current_clans = await fetchExistingClannames()
    if clanname not in current_clans:
        await ctx.respond(f"```{clanname} is not part of existing clans: \n{current_clans} \nPlease use '/registerclan' to create a new clan.```")
        return
    number = int(number)

    cursor = conn.cursor()
    cursor.execute("""SELECT players.nickname, players.points, players.battles, players.wins, players.average_enemy_rank, clans.name 
                   FROM players 
                   LEFT JOIN clans ON players.clan_id = clans.id
                   WHERE clans.name = %s
                   ORDER BY points DESC""",(clanname,))
    top_players = cursor.fetchmany(number)
    if (len(top_players) < 1):
        await ctx.send(f"No players were found with the clanname:'{clanname}'.")
        return

    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        if (item[2] > 0):
            printable_text = f"    RANK: {calculator} of {item[5]}. \n  nickname: {item[0]}, \n  points: {item[1]}, \n  battles: {item[2]}, \n  winrate: {round((item[3] / item[2]) * 100, 2)}%, \n  avrg_enemy_rank: {round(item[4], 0)}"
        else:
            printable_text = f"    RANK: {calculator} of {item[5]}. \n  nickname: {item[0]}, \n  points: {item[1]}, \n  battles: {item[2]}, \n  winrate: 0%, \n  avrg_enemy_rank: {round(item[4], 0)}"
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    scores_per_player.append(f"```** TOP{number} PLAYERS OF {clanname} HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_player))
# leaderboard players of clan ends


# LEADERBOARD CLAN COMMAND
# for example, user gives '/clanleaderboard 10' and bot gives scores of top10 clans
@bot.slash_command(name="leaderboardclans", description="Print top clans in order!")
async def leaderboardclans(ctx, number: int):
    scores_per_clan = []
    scores_per_clan.append(f"``` ** LEADERBOARD OF CLANS **```")

    number = int(number)
    cursor = conn.cursor()
    cursor.execute("""SELECT name, points, battles, wins, average_enemy_rank
                   FROM clans
                   ORDER BY points DESC""",())
    top_clans = cursor.fetchmany(number)

    calculator = 0
    for item in top_clans:
        calculator += 1
        printable_text = ""
        if (item[2] > 0):
            printable_text = f"       RANK: {calculator}. \n clanname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {round((item[3] / item[2]) * 100, 2)}%, \n avrg_enemyclan_rank: {round(item[4], 0)}"
        else:
            printable_text = f"       RANK: {calculator}. \n clanname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemyclan_rank: {round(item[4], 0)}"
        scores_per_clan.append(f"``` {printable_text.center(24)} ```")
    scores_per_clan.append(f"```  ** TOP{number} CLANS HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_clan))
# clanleaderboard ends
    

# REPORT CLANWAR COMMAND
@bot.slash_command(name="reportclanwar", description="Save clanwar scores permanently and gain rank for your clan!")
async def reportclanwar(ctx, year: int, month: int, day: int, challenger_clanname: str, challenger_score: int, defender_clanname: str, defender_score: int):
    challenger_clanname = challenger_clanname.lower()
    defender_clanname = defender_clanname.lower()
    # store here date for storing into database
    date = datetime.datetime(1900, 1, 1)
    # step1: validate that ctx.author is a registered admin
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    existing_leader = cursor.fetchone()
    if existing_leader is None:
        await ctx.respond("```Only admins registered with '/registeradmin' can report clanwar scores!```")
        return
    # step2: validate date
    date_is_valid = True
    try:
        date = datetime.datetime(year, month, day)
    except ValueError:
        date_is_valid = False
    if date_is_valid == False:
        await ctx.respond("```The date you gave is not a real date. Please make sure year, month and day are correct!```")
        return
    # step3: validate challenger and defender clannames and scores
    existing_clans = await fetchExistingClannames()
    if challenger_clanname not in existing_clans:
        await ctx.respond(f"```The challenger_clanname {challenger_clanname} wasn't part of: \n{existing_clans}. \nIf your clan's name is missing, please use '/registerclan'```")
        return
    
    if defender_clanname not in existing_clans:
        await ctx.respond(f"```The challenger_clanname {challenger_clanname} wasn't part of: \n{existing_clans}. \nIf your clan's name is missing, please use '/registerclan'```")
        return
    
    if challenger_score == defender_score:
        await ctx.respond(f"```{challenger_score} equals {defender_score}. \nScores may not be equal!```")
        return
    
    # step4: if all previous is ok, store given data into clanwars datatable
    cursor.execute("SELECT id from clans WHERE name = %s", (challenger_clanname,))
    challenger_clan_id = cursor.fetchone()[0]
    cursor.execute("SELECT id from clans WHERE name = %s", (defender_clanname,))
    defender_clan_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO clanwars (date, challenger_clan_id, defender_clan_id, challenger_won_rounds, defender_won_rounds) VALUES (%s, %s, %s, %s, %s)", (date, challenger_clan_id, defender_clan_id, challenger_score, defender_score,))

    # step5: solve first which clan won and then update points with update_clan_points()
    challenger_won = False
    if (challenger_score > defender_score):
        challenger_won = True
        await update_clan_points(challenger_clan_id, defender_clan_id, challenger_won)
    else:
        challenger_won = False
        await update_clan_points(challenger_clan_id, defender_clan_id, challenger_won)

    # step6: notify user of both clans new ranks
    cursor.execute("SELECT points, old_points FROM clans WHERE id = %s", (challenger_clan_id,))
    challenger_stats = cursor.fetchone()
    cursor.execute("SELECT points, old_points FROM clans WHERE id = %s", (defender_clan_id,))
    defender_stats = cursor.fetchone()

    if challenger_won:
        pointchange = challenger_stats[0] - challenger_stats[1]
        await ctx.respond(f"```{date.strftime('%x')} \n{challenger_clanname} has won the clanwar against {defender_clanname} with scores {challenger_score}-{defender_score}! \n{challenger_clanname} new points:{challenger_stats[0]}(+{pointchange}). \n{defender_clanname} new points:{defender_stats[0]}(-{pointchange}).```")
    else:
        pointchange = challenger_stats[1] - challenger_stats[0] 
        await ctx.respond(f"```{date.strftime('%x')} \n{defender_clanname} has won the clanwar against {challenger_clanname} with scores {defender_score}-{challenger_score}! \n{defender_clanname} new points:{defender_stats[0]}(+{pointchange}). \n{challenger_clanname} new points:{challenger_stats[0]}(-{pointchange}).```")
# reportclanwar ends


# PRINTCLANWARS COMMAND
@bot.slash_command(name="printclanwars", description="Print clanwar scores of a selected clanname")
async def printclanwars(ctx, clanname: str, number: int):
    clanname = clanname.lower()
    existing_clans = await fetchExistingClannames()
    if clanname not in existing_clans:
        await ctx.respond(f"```{clanname} is not part of existing clans: \n{existing_clans} \nYou may use '/registerclan' to create a new clan.```")
        return
    
    # first fetch the id of given clan, so it will be easier to find all clanwars containing that id in challenger or defender
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clans WHERE name = %s", (clanname,))
    wanted_clan_id = cursor.fetchone()[0]
    cursor.execute(""" SELECT clanwars.date, challenger_clan.name AS challenger_name, clanwars.challenger_won_rounds, defender_clan.name AS defender_name, clanwars.defender_won_rounds
                    FROM clanwars
                    LEFT JOIN clans AS challenger_clan ON clanwars.challenger_clan_id = challenger_clan.id
                    LEFT JOIN clans AS defender_clan ON clanwars.defender_clan_id = defender_clan.id
                    WHERE challenger_clan.id = %s OR defender_clan.id = %s
                    ORDER BY clanwars.date DESC, clanwars.id DESC""", (wanted_clan_id, wanted_clan_id,))
    clanwars = cursor.fetchmany(number)
    # print clanwar history
    if (len(clanwars) >= 1):
        scores = []
        scores.append(f"```** {number} CLANWARS OF {clanname.upper()}: **```")
        printable_text = ""
        # war[0] = date, war[1] = challenger name, war[2] = challenger points, war[3] = defender name, war[4] = defender points
        for war in clanwars: 
            printable_text = (f"```date: {war[0]} \n{war[1]} vs {war[3]} [{war[2]}-{war[4]}]```")
            scores.append(printable_text)

        scores.append(f"```** {number} MOST RECENT CLANWARS OF {clanname.upper()} HAVE BEEN PRINTED! **```")
        await ctx.respond("".join(scores))
        return
    else:
        await ctx.respond(f"```The clanwar history of clan {clanname} is currently empty! \nIf you think that there is a lack of information, please contact admins.```")
        return
# print clan wars ends


# PRINTCLANNAMES COMMAND
@bot.slash_command(name="printclannames", description="Print all existing clannames")
async def printclannames(ctx):
    existing_clans = await fetchExistingClannames()
    await ctx.respond(f"Currently existing clans are next: \n{existing_clans} \n If you miss a clan, use '/registerclan'!")
# print clannames ends


# PRINTMYDUELSAGAINST COMMAND
@bot.slash_command(name="printmyduelsagainst", description="Print your latest duels against a specific opponent")
async def printmyduelsagainst(ctx, opponent: discord.Member, number: int):
    duel_history = []
    duel_history.append(f"```** {number} DUELS OF {ctx.author.display_name.upper()} vs {opponent.display_name.upper()} **```")
    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(f"{ctx.author.mention} has not yet been registered. Please use '/registerplayer'.")
        return
    # make sure opponent is registered before trying to find him from the database
    opponent_is_registered = await is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.respond(f"{opponent.display_name} has not yet been registered. Please use '/registerplayer'.")
        return

    # fetch all duels of person and show the duels with correct nicknames
    # note that author can be either challenger or opponent in the database
    cursor = conn.cursor()
    cursor.execute("""SELECT duels.date, challenger_player.nickname, opponent_player.nickname, duels.challenger_won
                   FROM duels
                   LEFT JOIN players AS challenger_player ON duels.challenger_discord_id = challenger_player.discord_id
                   LEFT JOIN players AS opponent_player ON duels.opponent_discord_id = opponent_player.discord_id
                   WHERE (challenger_player.discord_id = %s OR challenger_player.discord_id = %s) 
                   AND (opponent_player.discord_id = %s OR opponent_player.discord_id = %s)
                   ORDER BY duels.date DESC""", (str(ctx.author.id), str(opponent.id), str(ctx.author.id), str(opponent.id),))
    duels = cursor.fetchmany(number)
    if len(duels) >= 1:
        for duel in duels: # 0 = date, 1 = challenger_nick, 2 = opponent_nick, 3 = challenger_won
            if duel[3] == True:
                message = f"```{duel[0]} \n{duel[1]} won vs {duel[2]}```"
                duel_history.append(message)
            else: 
                message = f"```{duel[0]} \n{duel[2]} won vs {duel[1]}```"
                duel_history.append(message)
        duel_history.append(f"```{number} MOST RECENT DUELS OF {ctx.author.display_name.upper()} vs {opponent.display_name.upper()} HAVE BEEN PRINTED!```")
        await ctx.respond("".join(duel_history))
        return
    else:
        await ctx.respond(f"{ctx.author.mention} does not have duels against {opponent.display_name}")
        return
# print my duels against ends


# PRINTMYDUELS
@bot.slash_command(name="printmyduels", description="Print your latest duels against anyone")
async def printmyduels(ctx, number: int):
    duel_history = []
    duel_history.append(f"```** {number} DUELS OF {ctx.author.display_name.upper()} **```")
    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(f"{ctx.author.mention} has not yet been registered. Please use '/registerplayer'.")
        return
    
    # fetch all duels where challenger or opponent was author
    cursor = conn.cursor()
    cursor.execute("""SELECT duels.date, challenger_player.nickname, opponent_player.nickname, duels.challenger_won
                   FROM duels
                   LEFT JOIN players AS challenger_player ON duels.challenger_discord_id = challenger_player.discord_id
                   LEFT JOIN players AS opponent_player ON duels.opponent_discord_id = opponent_player.discord_id
                   WHERE (challenger_player.discord_id = %s OR opponent_player.discord_id = %s)
                   ORDER BY duels.date DESC""", (str(ctx.author.id), str(ctx.author.id),))
    duels = cursor.fetchmany(number)

    if len(duels) >= 1:
        for duel in duels: # 0 = date, 1 = challenger_nick, 2 = opponent_nick, 3 = challenger_won
            if duel[3] == True:
                message = f"```{duel[0]} \n{duel[1]} won vs {duel[2]}```"
                duel_history.append(message)
            else: 
                message = f"```{duel[0]} \n{duel[2]} won vs {duel[1]}```"
                duel_history.append(message)
        duel_history.append(f"```{number} MOST RECENT DUELS OF {ctx.author.display_name.upper()} HAVE BEEN PRINTED!```")
        await ctx.respond("".join(duel_history))
        return
    else:
        await ctx.respond(f"{ctx.author.mention} does not have any duels!")
        return
# print my duels ends


# PRINTADMINS COMMAND
@bot.slash_command(name="printadmins", description="Print all admins who have registered with '/registeradmin'!")
async def printadmins(ctx):
    all_admins = []
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins", ())
    admin_ids = cursor.fetchall()
    admin_ids = [id[0] for id in admin_ids]
    if len(admin_ids) > 0:
        for id in admin_ids:
            cursor.execute("SELECT username FROM players WHERE discord_id = %s", (id,))
            username = cursor.fetchone()[0]
            all_admins.append(username)
        await ctx.respond(f"All currently registered admins: \n {all_admins}")
    else:
        await ctx.respond(f"There are no currently registered admins!")
# print admins ends


# EVENTANNOUNCE COMMAND
@bot.slash_command(name="eventannounce", description="Messages privately clan members about an approaching event!")
async def eventannounce(ctx, role: discord.Role, title: str, date: str, where: str, password: str):
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    existing_leader = cursor.fetchone()
    if existing_leader is None:
        await ctx.respond("```Only admins registered with '/registeradmin' can announce events!```")
        return
    await ctx.respond(f".")

    # basis for messages
    channel_message = f"on {date.lower()}! \nat {where.lower()} \n password: {password}  \n \n{role.mention} click ⚔️ to join"
    private_message = f"on {date}! \nPlease click ⚔️ in {ctx.guild.name} '{ctx.channel.name}' channel if you want to join!"
    
    # use embed message, otherwise cannot use bot emoticons on it to get "votes" how many will join
    channel_message_embed = discord.Embed(title=title.upper(),
    description=channel_message)
    private_message_embed = discord.Embed(title=title.upper(), description = private_message)


    interactive_channel_message = await ctx.send(embed=channel_message_embed)
    await interactive_channel_message.add_reaction("⚔️")

    # direct message all players with normal string and encourage to add a sword emoticon
    for member in ctx.guild.members:
        if member is None:
            continue
        if role in member.roles and not member.bot:
            try:
                await member.send(embed=private_message_embed)
                print(f'Message sent to {member.name}')
            except discord.Forbidden:
                print(f'Cannot send message to {member.name}')
            except discord.HTTPException as e:
                print(f'Failed to send message to {member.name}: {e}')
    print(f"All members of {ctx.guild.name} have been messaged about the coming event of {title}!")
    return
# event announce ends


# CHALLENGE COMMAND
challenge_status = []
@bot.slash_command(name="challenge", description="Challenge enemy player to duel and gain rank!")
async def challenge(ctx, opponent: discord.Member):
    global challenge_status

    # CHECK NOT CHALLENGE ONESELF
    if (opponent.id == ctx.author.id):
        await ctx.respond("You may not challenge yourself!")
        return

    # CHECK CHALLENGER AND OPPONENT ARE REGISTERED, OTHERWISE NOTIFY AND RETURN
    opponent_is_registered = await is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.respond(f"The opponent {opponent.mention} has not yet been registered. Please use '/registerplayer'.")
        return
    
    challenger_is_registered = await is_registered(str(ctx.author.id))
    if not challenger_is_registered:
        await ctx.respond(f"The challenger {ctx.author.mention} has not yet been registered. Please use '/registerplayer'.")
        return
    
    if (ctx.author.id in challenge_status):
        await ctx.respond(f"You {ctx.author.mention} have already challenged somebody.")
        return
    
    # THE REAL CHALLENGE FUNCTION BEGINS HERE
    await ctx.respond(".")
    # keep track that person cannot do more than 1 challenge at time
    challenge_status.append(ctx.author.id)

    # Step 1: Initial Challenge Message
    challenge_embed = discord.Embed(title=f"{ctx.author.display_name} has challenged {opponent.display_name} to ft7!",
                                    description=f"{opponent.mention} can select: \n*  🗡️{ctx.author.display_name} won \n*  🏰{opponent.display_name} won \n*  🚫refuse.")
    challenge_msg = await ctx.send(embed=challenge_embed)

    # Add reactions for Challenger won, Opponent won, Refuse
    await challenge_msg.add_reaction("🗡️")  # Challenger won
    await challenge_msg.add_reaction("🏰")  # Opponent won
    await challenge_msg.add_reaction("🚫")  # refuse

    # Wait for a reaction from only opponent reactions count
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: u == opponent and str(r.emoji) in ["🗡️", "🏰", "🚫"])
    except asyncio.TimeoutError:
        challenge_status.remove(ctx.author.id)
        await ctx.send(f"{ctx.author.mention}'s challenge against {opponent.display_name} expired.")
        return

    # HANDLE REACTIONS
    # challenger won
    if str(reaction.emoji) == "🗡️":
        challenge_status.remove(ctx.author.id)
        await update_player_points(ctx.author, opponent, True)
        await update_duels_history(str(ctx.author.id), str(opponent.id), True)
        # notify users of their new points and pointchange
        cursor = conn.cursor()
        cursor.execute("SELECT points, old_points FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        challenger_points = cursor.fetchone()
        challenger_new_points = challenger_points[0]
        challenger_old_points = challenger_points[1]
        cursor.execute("SELECT points, old_points FROM players WHERE discord_id = %s", (str(opponent.id),))
        opponent_points = cursor.fetchone()
        opponent_new_points = opponent_points[0]
        opponent_old_points = opponent_points[1]
        challenger_win_embed = discord.Embed(title=f"{ctx.author.display_name} has won against {opponent.display_name}!",
                                            description=f"{ctx.author.mention} new points: {challenger_new_points}(+{challenger_new_points-challenger_old_points}) \n{opponent.mention} new points: {opponent_new_points}(-{opponent_old_points - opponent_new_points})")
        await ctx.send(embed=challenger_win_embed)
    # opponent won
    elif str(reaction.emoji) == "🏰":
        challenge_status.remove(ctx.author.id)
        await update_player_points(ctx.author, opponent, False)
        await update_duels_history(str(ctx.author.id), str(opponent.id), False)
        # notify users of their new points and pointchange
        cursor = conn.cursor()
        cursor.execute("SELECT points, old_points FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        challenger_points = cursor.fetchone()
        challenger_new_points = challenger_points[0]
        challenger_old_points = challenger_points[1]
        cursor.execute("SELECT points, old_points FROM players WHERE discord_id = %s", (str(opponent.id),))
        opponent_points = cursor.fetchone()
        opponent_new_points = opponent_points[0]
        opponent_old_points = opponent_points[1]
        defender_win_embed = discord.Embed(title=f"{opponent.display_name} has won against {ctx.author.display_name}!",
                                            description=f"{opponent.mention} new points: {opponent_new_points}(+{opponent_new_points - opponent_old_points}) \n{ctx.author.mention} new points: {challenger_new_points}(-{challenger_old_points - challenger_new_points})")
        await ctx.send(embed=defender_win_embed)
    # refuse duel
    elif str(reaction.emoji) == "🚫":
        challenge_status.remove(ctx.author.id)
        await ctx.send(f"The FT7 has been refused!")
# challenge ends


# TOKEN OF BOT TO IDENTIFY AND USE IN CHANNELS
token = settings.bot_token
bot.run(token)
