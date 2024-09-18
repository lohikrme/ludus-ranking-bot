# ludusbot.py
# updated 18th septemper 2024

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

bot = commands.Bot(command_prefix='!', intents=intents)  # use slash as start of command

# keep these guilds real time, but store permanently in database
current_guild_ids = []

# return integer array of guild ids from database
async def fetch_all_guild_ids():
    ids = []
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM guilds", ())
    all_guild_ids = cursor.fetchall()
    for id in all_guild_ids:
        ids.append(int(id[0]))
    return ids

@bot.event
async def on_guild_join(guild):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO guilds (id, name) VALUES (%s, %s,) ON CONFLICT (id) DO NOTHING", (str(guild.id), str(guild.name),))
    current_guild_ids.append(guild.id)
    await bot.sync_commands(guild_ids=current_guild_ids)

@bot.event
async def on_guild_remove(guild):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM guilds WHERE id = %s", (str(guild.id),))
    current_guild_ids.remove(guild.id)
    await bot.sync_commands(guild_ids=current_guild_ids)

# BOT ENTERS THE CHANNEL
@bot.event
async def on_connect():
    current_guild_ids = await fetch_all_guild_ids()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.sync_commands(guild_ids=current_guild_ids)
    print("Slash commands have been cleared and updated... Wait a bit more before bot is ready...")
    print("Bot is finally ready to function!")


# -------- PRIVATE FUNCTIONS -----------

# USE THIS TO UPDATE DUELS DATATABLE HISTORY
async def update_duels_history(challenger_discord_id: str, opponent_discord_id: str, challenger_score: int, opponent_score: int):
    date = datetime.datetime.now()
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO duels (date, challenger_discord_id, opponent_discord_id, challenger_score, opponent_score) VALUES (%s, %s, %s, %s, %s,)", (date, challenger_discord_id, opponent_discord_id, challenger_score, opponent_score))
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
    await ctx.respond(guides.guide_eng, ephemeral=True)
# guide in english ends

# GUIDE IN RUSSIAN
@bot.slash_command(name="гид", description="Обучает команды ludus-ranking-bot на русском языке!")
async def гид(ctx):
    await ctx.respond(guides.guide_rus, ephemeral=True)
# guide in russian ends

# GUIDE IN TURKISH
@bot.slash_command(name="rehber", description="ludus-ranking-bot komutlarını İngilizce ile öğretir!")
async def rehber(ctx):
    await ctx.respond(guides.guide_tr, ephemeral=True)
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
        await ctx.respond("You have already been registered! \nIf you want to reset your rank, please contact admins.", ephemeral=True)
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
        await ctx.respond(f"The clanname {clanname} already exists", ephemeral=True)
        return
    
    cursor.execute("INSERT INTO clans (name) VALUES (%s)", (clanname,))
    await ctx.respond(f"The clanname '{clanname}' has successfully been registered!")
    return
# registerclan ends


# REGISTER ADMIN COMMAND
@bot.slash_command(name="registeradmin", description="Register as admin to be able to report/approve clanwars and announce events!")
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
    # check admin belongs to a clan
    cursor.execute("SELECT clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    author_clan_id = cursor.fetchone()[0]
    if(author_clan_id == 1):
        await ctx.respond("You must join a clan before becoming an admin. Admins represent their clans.")
        return
    # all ok, add the new admin
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
        await ctx.respond(f"Your nickname has been updated! \nOld nickname: '{old_nickname}'. \nNew nickname: '{nickname}'", ephemeral=True)
        return
    else:
        await ctx.respond(f"Please register before changing your nickname.", ephemeral=True)
        return
# change your nickname ends


# CHANGE YOUR CLAN COMMAND
@bot.slash_command(name="changeyourclan", description="Give yourself a new clanname!")
async def changeyourclan(ctx, new_clanname: str):
    new_clanname = new_clanname.lower()
    # check if user has registered
    is_registered_result = await is_registered(str(ctx.author.id))
    if not is_registered_result:
        await ctx.respond(f"Register before using this command or contact admins.", ephemeral=True)
        return
    # check that selected new clanname is registered as clan
    existing_clans = await fetchExistingClannames()
    if new_clanname not in existing_clans:
        await ctx.respond(f"'{new_clanname}' is not part of existing clans: \n{existing_clans} \nPlease use '/registerclan' to create a new clanname.", ephemeral=True)
        return
    # fetch old clanname and compare it is not same as new clanname
    cursor = conn.cursor()
    cursor.execute("SELECT clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    old_clan_id = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM clans WHERE id = %s", (old_clan_id,))
    old_clanname = cursor.fetchone()[0]
    if (new_clanname == old_clanname):
        await ctx.respond(f"You already belong to the clan '{new_clanname}'", ephemeral=True)
        return
    # change the clanname of the user
    else:
        cursor.execute("SELECT id FROM clans WHERE name = %s", (new_clanname,))
        new_clan_id = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET clan_id = (%s) WHERE players.discord_id = %s", (new_clan_id, str(ctx.author.id),))
        await ctx.respond(f"Your clanname has been updated! \nOld clanname: '{old_clanname}'. \nNew clanname: '{new_clanname}'", ephemeral=True)
        return
# change your clan ends


# MYSCORE COMMAND
@bot.slash_command(name="myscore", description="Print your personal scores!")
async def myscore(ctx):
    is_registered_result = await is_registered(str(ctx.author.id))
    if not is_registered_result:
        await ctx.respond(f"Please register before printing your scores.")
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
        await ctx.respond(f"```{clanname} is not part of existing clans: \n{current_clans} \nPlease use '/registerclan' to create a new clan.```", ephemeral=True)
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
        await ctx.respond(f"No players were found with the clanname:'{clanname}'.")
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
    

clanwar_status = []
# REPORT CLANWAR COMMAND
@bot.slash_command(name="reportclanwar", description="Save clanwar scores permanently and gain rank for your clan!")
async def reportclanwar(ctx, year: int, month: int, day: int, reporter_clanname: str, reporter_score: int, opponent_clanname: str, opponent_score: int):

    global clanwar_status
    all_admin_ids = []
    all_opponent_clanmember_ids = []
    opponent_admin_ids = []
    
    reporter_clanname = reporter_clanname.lower()
    opponent_clanname = opponent_clanname.lower()
    # store here date for storing into database
    date = datetime.datetime(1900, 1, 1)
    

    ### step1: validate that ctx.author is a registered admin and is not in clanwar already
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    existing_leader = cursor.fetchone()
    if existing_leader is None:
        await ctx.respond("```Only admins registered with '/registeradmin' can report clanwar scores!```", ephemeral=True)
        return
    
    if (ctx.author.id in clanwar_status):
        await ctx.respond(f"You {ctx.author.mention} are already in clanwar with some clan.", ephemeral=True)
        return
    
    ### step2: validate date
    date_is_valid = True
    try:
        date = datetime.datetime(year, month, day)
    except ValueError:
        date_is_valid = False
    if date_is_valid == False:
        await ctx.respond("```The date you gave is not a real date. Please make sure year, month and day are correct!```", ephemeral=True)
        return

    ### step3: validate challenger and defender clannames and scores
    existing_clans = await fetchExistingClannames()
    if reporter_clanname not in existing_clans:
        await ctx.respond(f"```The reporter_clanname {reporter_clanname} wasn't part of: \n{existing_clans}. \nIf your clan's name is missing, please use '/registerclan'```", ephemeral=True)
        return
    if opponent_clanname not in existing_clans:
        await ctx.respond(f"```The reporter_clanname {reporter_clanname} wasn't part of: \n{existing_clans}. \nIf your clan's name is missing, please use '/registerclan'```", ephemeral=True)
        return
    if reporter_score == opponent_score:
        await ctx.respond(f"```{reporter_score} equals {opponent_score}. \nScores may not be equal!```", ephemeral=True)
        return
    
    ### step 4: check that reporter_clanname is same as author's clanname
    cursor.execute("""SELECT clans.name 
                   FROM clans
                   LEFT JOIN players ON players.clan_id = clans.id
                   WHERE players.discord_id = %s""", (str(ctx.author.id),))
    authorclanname = cursor.fetchone()[0]
    if authorclanname != reporter_clanname:
        await ctx.respond(f"Reporter_clanname did not match to author's clan. \n{ctx.author.mention} belongs to clan '{authorclanname}', \nwhile reporter_clanname was '{reporter_clanname}'", ephemeral=True)
        return
    
    ### step 5: check that opponent_clanname has a registered admin, and store id for later use
    # first fetch opponent clan id
    cursor.execute("SELECT clans.id FROM clans WHERE clans.name = %s", (opponent_clanname,))
    opponent_clan_id = cursor.fetchone()[0]

    # second fetch all admin ids
    cursor.execute("SELECT discord_id FROM admins")
    all_admins = cursor.fetchall()
    for admin in all_admins:
        all_admin_ids.append(admin[0])

    # third fetch all opponent clan member ids
    cursor.execute("SELECT players.discord_id FROM players WHERE players.clan_id = %s", (opponent_clan_id,))
    opponent_players = cursor.fetchall()
    for player in opponent_players:
        all_opponent_clanmember_ids.append(player[0])

    for admin_id in all_admin_ids:
        if admin_id in all_opponent_clanmember_ids:
            opponent_admin_ids.append(admin_id)

    if len(opponent_admin_ids) < 1:
        await ctx.respond ("Opponent clan does not have a registered admin! They need one to confirm the clanwar results.", ephemeral=True)
        return


    ### step 6: send approval message to all opponent admins, or cancel after 24h wait time automatically
    clanwar_status.append(ctx.author.id)

    await ctx.respond(embed=discord.Embed(title="", description=f"Waiting for opponent clan's admins to confirm: \n{reporter_clanname} vs {opponent_clanname} \n{reporter_score}-{opponent_score}"))

    async def send_approval_message(admin_id, ctx, opponent_admin_ids, reporter_clanname, reporter_score, opponent_clanname, opponent_score, stop_listening_emoticons_event):
        opponent_admin = await bot.fetch_user(admin_id)
        approval_embed = discord.Embed(
            title=f"Confirm clanwar results:",
            description=f"{reporter_clanname} vs {opponent_clanname} \n{reporter_score}-{opponent_score}\n click ✅approve   🚫disagree."
        )
        approval_msg = await opponent_admin.send(embed=approval_embed)
        await approval_msg.add_reaction("✅")
        await approval_msg.add_reaction("🚫")

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=3600.0, check=lambda reaction, user: user == opponent_admin and str(reaction.emoji) in ["✅", "🚫"] and reaction.message.id == approval_msg.id)
        except asyncio.TimeoutError:
            await opponent_admin.send(f"Clanwar reporting expired!")
            return
        except asyncio.CancelledError:
            return

        # HANDLE REACTIONS
        if str(reaction.emoji) == "✅":
            if (stop_listening_emoticons_event.is_set()):
                return
            stop_listening_emoticons_event.set()
            clanwar_status.remove(ctx.author.id)
            ### step7: if all previous is ok, store given data into clanwars datatable
            cursor.execute("SELECT id from clans WHERE name = %s", (reporter_clanname,))
            challenger_clan_id = cursor.fetchone()[0]
            cursor.execute("SELECT id from clans WHERE name = %s", (opponent_clanname,))
            defender_clan_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO clanwars (date, challenger_clan_id, defender_clan_id, challenger_won_rounds, defender_won_rounds) VALUES (%s, %s, %s, %s, %s)", (date, challenger_clan_id, defender_clan_id, reporter_score, opponent_score,))

            ### step8: solve first which clan won and then update points with update_clan_points()
            challenger_won = False
            if (reporter_score > opponent_score):
                challenger_won = True
                await update_clan_points(challenger_clan_id, defender_clan_id, challenger_won)
            else:
                challenger_won = False
                await update_clan_points(challenger_clan_id, defender_clan_id, challenger_won)

            ### step9: notify author's channel and opponent admins of new clanwar scores and rankings
            cursor.execute("SELECT points, old_points FROM clans WHERE id = %s", (challenger_clan_id,))
            challenger_stats = cursor.fetchone()
            cursor.execute("SELECT points, old_points FROM clans WHERE id = %s", (defender_clan_id,))
            defender_stats = cursor.fetchone()

            if challenger_won:
                pointchange = challenger_stats[0] - challenger_stats[1]
                await ctx.respond(f"```{date.strftime('%x')} \n{reporter_clanname} has won the clanwar against {opponent_clanname} with scores {reporter_score}-{opponent_score}! \n{reporter_clanname} new points:{challenger_stats[0]}(+{pointchange}). \n{opponent_clanname} new points:{defender_stats[0]}(-{pointchange}).```")
                for id in opponent_admin_ids:
                    user = await bot.fetch_user(id)
                    await user.send(f"```{date.strftime('%x')} \n{reporter_clanname} has won the clanwar against {opponent_clanname} with scores {reporter_score}-{opponent_score}! \n{reporter_clanname} new points:{challenger_stats[0]}(+{pointchange}). \n{opponent_clanname} new points:{defender_stats[0]}(-{pointchange}).```")
                return
            else:
                pointchange = challenger_stats[1] - challenger_stats[0] 
                await ctx.respond(f"```{date.strftime('%x')} \n{opponent_clanname} has won the clanwar against {reporter_clanname} with scores {opponent_score}-{reporter_score}! \n{opponent_clanname} new points:{defender_stats[0]}(+{pointchange}). \n{reporter_clanname} new points:{challenger_stats[0]}(-{pointchange}).```")
                for id in opponent_admin_ids:
                    user = await bot.fetch_user(id)
                    await user.send(f"```{date.strftime('%x')} \n{opponent_clanname} has won the clanwar against {reporter_clanname} with scores {opponent_score}-{reporter_score}! \n{opponent_clanname} new points:{defender_stats[0]}(+{pointchange}). \n{reporter_clanname} new points:{challenger_stats[0]}(-{pointchange}).```")
                return

        elif str(reaction.emoji) == "🚫":
            if (stop_listening_emoticons_event.is_set()):
                return
            stop_listening_emoticons_event.set()
            clanwar_status.remove(ctx.author.id)
            await ctx.respond("Enemy admins have disagreed with the clanwar scores!")
            for id in opponent_admin_ids:
                user = await bot.fetch_user(id)
                await user.send("Admins have disagreed with the clanwar score!")
            return

    # because there can be multiple opponent clan leaders, we must use asyncio.gather to simultaneously message all of them
    stop_event = asyncio.Event()
    tasks = [send_approval_message(admin_id, ctx, opponent_admin_ids, reporter_clanname, reporter_score, opponent_clanname, opponent_score, stop_event) for admin_id in opponent_admin_ids]
    await asyncio.gather(*tasks)
# reportclanwar ends



ft7_status = []
# REPORTFT7 COMMAND
@bot.slash_command(name="reportft7", description="Discreetly via private chat save duel ft7 scores permanently and gain personal ranking points!")
async def reportft7(ctx, opponent: discord.Member, my_score: int, opponent_score: int):

    global ft7_status

    # step 0: check opponent is different than challenger
    if (opponent.id == ctx.author.id):
        await ctx.respond("You may not ft7 yourself!", ephemeral=True)
        return
    
    # step 1: check challenger and opponent are registered
    challenger_is_registered = await is_registered(str(ctx.author.id))
    if not challenger_is_registered:
        await ctx.respond("You have not been registered. Please use '/registerplayer' before reportduel.", ephemeral=True)
        return
    
    opponent_is_registered = await is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.respond(f"Your opponent {opponent.display_name} has not been registered. Please use '/registerplayer'.", ephemeral=True)
        return
    
    # step 2: check that scores are not equal, and challenger is not already in ft7 (to avoid spam)
    if my_score == opponent_score:
        await ctx.respond(f"Your score {my_score} and opponent score {opponent_score} are equal. Stalemate is not counted.", ephemeral=True)
        return
    
    if (ctx.author.id in ft7_status):
        await ctx.respond(f"You {ctx.author.mention} are already in ft7 with somebody.", ephemeral=True)
        return

    # step 3: program begins! add author to ft7_status to prevent spam
    ft7_status.append(ctx.author.id)
    await ctx.respond(f"Please wait for {opponent.display_name} to verify the ft7 scores!", ephemeral=True)

    # step 4: send to opponent private embed message which asks for approval of scores
    approval_embed = discord.Embed(
        title=f"Confirm ft7 results:",
        description=f"{ctx.author.display_name} vs {opponent.display_name} \n{my_score}-{opponent_score}\n click ✅approve   🚫disagree."
    )
    approval_msg = await opponent.send(embed=approval_embed)
    await approval_msg.add_reaction("✅")
    await approval_msg.add_reaction("🚫")

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=lambda reaction, user: user == opponent and str(reaction.emoji) in ["✅", "🚫"] and reaction.message.id == approval_msg.id)
    except asyncio.TimeoutError:
        await opponent.send(f"FT7 {ctx.author.display_name} vs {opponent.display_name} expired!")
        await ctx.author.send(f"FT7 {ctx.author.display_name} vs {opponent.display_name} expired!")
        return
    except asyncio.CancelledError:
        return

    # step 5: if scores are approved, calculate winner
    if str(reaction.emoji) == "✅":
        challenger_won = False
        if my_score > opponent_score:
            challenger_won = True

        # step 6: store scores and ranks into database
        if challenger_won:
            await update_player_points(ctx.author, opponent, True)
            await update_duels_history(str(ctx.author.id), str(opponent.id), my_score, opponent_score)
        else:
            await update_player_points(ctx.author, opponent, False)
            await update_duels_history(str(ctx.author.id), str(opponent.id), my_score, opponent_score)

        # step 7: notify users of their new points and pointchange
        if challenger_won:
            ft7_status.remove(ctx.author.id)
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
            await ctx.author.send(embed=challenger_win_embed)
            await opponent.send(embed=challenger_win_embed)
            return
        
        else:
            ft7_status.remove(ctx.author.id)
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
            await ctx.author.send(embed=defender_win_embed)
            await opponent.send(embed=defender_win_embed)
            return

    # step 8: if scores are disagreed, notify challenger that opponent disagrees and interact with opponent
    if str(reaction.emoji) == "🚫":
        await ctx.author.send(f"{opponent.display_name} has disagreed with your ft7 scores!")
        await opponent.send(f"You have disagreed with {ctx.author.display_name}'s ft7 scores ")
        return
# report ft7 ends


# PRINTCLANWARS COMMAND
@bot.slash_command(name="printclanwars", description="Print clanwar scores of a selected clanname")
async def printclanwars(ctx, clanname: str, number: int):
    clanname = clanname.lower()
    existing_clans = await fetchExistingClannames()
    if clanname not in existing_clans:
        await ctx.respond(f"```{clanname} is not part of existing clans: \n{existing_clans} \nYou may use '/registerclan' to create a new clan.```", ephemeral=True)
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
    await ctx.respond(f"Currently existing clans are next: \n{existing_clans} \n If you miss a clan, please use '/registerclan'!")
# print clannames ends


# PRINTMYDUELSAGAINST COMMAND
@bot.slash_command(name="printmyduelsagainst", description="Print your latest duels against a specific opponent")
async def printmyduelssagainst(ctx, opponent: discord.Member, number: int):
    duel_history = []
    duel_history.append(f"```** {number} FT7s OF {ctx.author.display_name.upper()} vs {opponent.display_name.upper()} **```")
    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(f"{ctx.author.mention} has not yet been registered. Please use '/registerplayer'.", ephemeral=True)
        return
    # make sure opponent is registered before trying to find him from the database
    opponent_is_registered = await is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.respond(f"{opponent.display_name} has not yet been registered. Please use '/registerplayer'.", ephemeral=True)
        return

    # fetch all duels of person and show the duels with correct nicknames
    # note that author can be either challenger or opponent in the database
    cursor = conn.cursor()
    cursor.execute("""SELECT duels.date, challenger_player.nickname, opponent_player.nickname, duels.challenger_score, duels.opponent_score
                   FROM duels
                   LEFT JOIN players AS challenger_player ON duels.challenger_discord_id = challenger_player.discord_id
                   LEFT JOIN players AS opponent_player ON duels.opponent_discord_id = opponent_player.discord_id
                   WHERE (challenger_player.discord_id = %s OR challenger_player.discord_id = %s) 
                   AND (opponent_player.discord_id = %s OR opponent_player.discord_id = %s)
                   ORDER BY duels.date DESC""", (str(ctx.author.id), str(opponent.id), str(ctx.author.id), str(opponent.id),))
    duels = cursor.fetchmany(number)
    if len(duels) >= 1:
        for duel in duels: # 0 = date, 1 = challenger_nick, 2 = opponent_nick, 3 = challenger_score, 4 = opponent_score
            message = f"```ft7 on {duel[0]} \n{duel[1]} vs {duel[2]} [{duel[3]}-{duel[4]}]```"
            duel_history.append(message)
        duel_history.append(f"```{number} MOST RECENT FT7s OF {ctx.author.display_name.upper()} vs {opponent.display_name.upper()} HAVE BEEN PRINTED!```")
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
    duel_history.append(f"```** {number} FT7's OF {ctx.author.display_name.upper()} **```")
    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(f"{ctx.author.mention} has not yet been registered. Please use '/registerplayer'.", ephemeral=True)
        return
    
    # fetch all duels where challenger or opponent was author
    cursor = conn.cursor()
    cursor.execute("""SELECT duels.date, challenger_player.nickname, opponent_player.nickname, duels.challenger_score, duels.opponent_score
                   FROM duels
                   LEFT JOIN players AS challenger_player ON duels.challenger_discord_id = challenger_player.discord_id
                   LEFT JOIN players AS opponent_player ON duels.opponent_discord_id = opponent_player.discord_id
                   WHERE (challenger_player.discord_id = %s OR opponent_player.discord_id = %s)
                   ORDER BY duels.date DESC""", (str(ctx.author.id), str(ctx.author.id),))
    duels = cursor.fetchmany(number)

    if len(duels) >= 1:
        for duel in duels: # 0 = date, 1 = challenger_nick, 2 = opponent_nick, 3 = challenger_score, 4 = opponent_score
            message = f"```ft7 on {duel[0]} \n{duel[1]} vs {duel[2]} [{duel[3]}-{duel[4]}]```"
            duel_history.append(message)
        duel_history.append(f"```{number} MOST RECENT FT7's OF {ctx.author.display_name.upper()} HAVE BEEN PRINTED!```")
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
    all_admins.append("```All currently registered admins:```")
    calculator = 0
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins", ())
    admin_ids = cursor.fetchall()
    admin_ids = [id[0] for id in admin_ids]
    if len(admin_ids) > 0:
        for id in admin_ids:
            calculator += 1
            cursor.execute("""SELECT players.nickname, players.username, clans.name 
                           FROM players 
                           LEFT JOIN clans ON players.clan_id = clans.id
                           WHERE discord_id = %s""", (id,))
            admin_info = cursor.fetchone()
            all_admins.append(f"```NUMBER {calculator}: \nnickname: {admin_info[0]} \ndiscord_username: {admin_info[1]} \nclanname: {admin_info[2]}```")
        await ctx.respond("".join(all_admins))
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
        await ctx.respond("```Only admins registered with '/registeradmin' can announce events!```", ephemeral=True)
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


# TOKEN OF BOT TO IDENTIFY AND USE IN CHANNELS
token = settings.bot_token
bot.run(token)
