# ludusbot.py
# Made by Chinese Parrot 25th july 2024

import random
import psycopg2
import discord
import settings
import facts
from discord.ext import commands
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

guilds = [
    1060303582487908423, # middle-earth
    1194360639544635482 # legion
]

leader_password = "Ao823jsd7KGRAAAAGK421&?!"


# BOT ENTERS THE CHANNEL
@bot.event
async def on_connect():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.sync_commands(guild_ids=guilds)
    print("Slash commands have been cleared and updated... Wait a bit more before bot is ready...")
    print("Bot is finally ready to function!")


# -------- PRIVATE FUNCTIONS -----------

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
    cursor.execute("SELECT clanname FROM clans", ())
    clannames = cursor.fetchall()
    current_clans = []
    for item in clannames:
        current_clans.append(item[0])
    return current_clans
# fetch existing clannames ends


# UPDATE PLAYER POINTS IN DATABASE
async def update_player_points(context, challenger, opponent, challenger_win: bool):

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
    await context.send(f"{new_scores_tittle.center(24)}")
    await context.send(f"Challenger {challenger.mention} old_points are: {challenger_stats['current_points']}. \n Challenger {challenger.mention} new points are {challenger_new_points} \n")
    await context.send(f"Opponent {opponent.mention} old_points are: {opponent_stats['current_points']}. \n Opponent {opponent.mention} new points are {opponent_new_points}")

    return 
# update player points ends



# ------- BOT COMMANDS (PUBLIC FUNCTIONS) ---------------

# SLASH COMMAND VERSION OF LEARN COMMANDS IN ENGLISH
@bot.slash_command(name="learncommands", description="Teaches commands of ludus-ranking-bot with English.")
async def learncommands(ctx):
    commands_list = [
        "```The commands of ludus-ranking-bot are next:```",
        "```'/register', \n e.g '/register Sauron', \n to register into player database to be able to earn rank```",
        "```'/clanregister, \n e.g '/clanregister Marchia' \n to register clan into clans database.```",
        "```'/challenge', \n e.g '/challenge @Sauron', \n to challenge another player in duel, winner gains ranking points, loser loses points ```",
        "```'/changenick' \n e.g  '/changenick Sauron', \n to change your nickname in your statistics```",
        "```'/changeclan' \n e.g  '/changeclan Legion', \n defaultly clanname is empty, so u add clanname using this. also able to change clanname with this.```",
        "```'/iamclanleader \n e.g '/iamclanleader 12345osman', \n become a clanleader to be able to announce events and report clanwar scores```",
        "```'/printclanleaders \n e.g '/printclanleaders', \n print all clan leaders who have registered with '/iamclanleader'```",
        "```'/reportclanwar \n e.g '/reportclanwar Legion 12 Valkyria 4' \n store information of clanwar scores into database ```",
        "```'/eventannounce \n e.g '/eventannounce all clanwar Legion vs Valkuria saturday 19:00 CE!, \n bot private messages about event to all or specific role in channel.```",
        "```'/myscore' \n to print own statistics```",
        "```'/top' \n e.g  '/top 10', \n to print top players from any clan```",
        "```'/topclanplayers' \n e.g  '/topclanplayers 3 Marchia', \n to print top players of a single clan.```",
        "```'/clanleaderboard \n e.g '/clanleaderboard 10', \n print top clans in order.```",
        "```'/clanwarhistory \n e.g '/clanwarhistory Legion', \n print clanwar scores of the selected clan. ```",
        "```'/printclans' \n e.g '/printclans', \n print all existing clannames```",
        "```'/factual' \n prints interesting facts from variety of topics in English. also useful to test if bot is active. ```",
        "```'/learncommands' \n teaches commands of ludus-ranking-bot with English. ```"
    ]
    await ctx.respond("\n".join(commands_list))


# LEARN COMMANDS IN RUSSIAN
@bot.slash_command(name="изучатькоманды", description="обучает командам ludus-ranking-bot на английском языке.")
async def изучатькоманды(ctx):
    commands_list = [
        "```Команды ludus-ranking-bot следующие:```",
        "```'/register прозвище', \n например '/register Sauron', \n чтобы зарегистрироваться в базе данных игроков и иметь возможность зарабатывать рейтинг```",
        "```'/clanregister названиеклана, \n например '/clanregister Marchia' \n зарегистрировать клан в базе данных кланов.```",
        "```'/challenge прозвище', \n например '/challenge @Sauron', \n чтобы вызвать другого игрока на дуэль, победитель получает очки рейтинга, проигравший теряет очки```",
        "```'/changenick @прозвище' \n например '/changenick Sauron', \n чтобы изменить свой никнейм в статистике```",
        "```'/changeclan названиеклана' \n например '/changeclan Legion', \n по умолчанию имя клана пустое, поэтому вы добавляете имя клана с помощью этой команды. также можно изменить имя клана с помощью этой команды.```",
        "```'/myscore' \n чтобы вывести свою статистику```",
        "```'/top число' \n например '/top 10', \n чтобы вывести топ игроков из любого клана```",
        "```'/topclanplayers число названиеклана' \n например '/topclanplayers 3 Marchia', \n чтобы вывести топ игроков одного клана```",
        "```'/факт' \n печатает интересные факты из самых разных тем. также полезно проверить, активен ли бот.```",
        "```'/изучатькоманды' \n обучает командам ludus-ranking-bot на английском языке.```"
    ]
    await ctx.respond("\n".join(commands_list))



# FACTUAL ENG COMMAND
@bot.slash_command(name="factual", description="Bot will tell interesting facts")
async def factual(ctx):
    answer = random.choice(facts.facts_eng)
    await ctx.respond(answer)  
# factual eng ends

# FACTUAL RUS COMMAND
@bot.slash_command(name="факт", description="Бот расскажет интересные факты")
async def факт(ctx):
    answer = random.choice(facts.facts_rus)
    await ctx.respond(answer)  
# factual rus ends


# REGISTER COMMAND
@bot.slash_command(name="register", description="Register to players database")
async def register(ctx, nickname: str):
    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)
    # NOTIFY USER THEY ARE ALREADY REGISTERED
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        await ctx.respond("You have already been registered! If you want to reset your rank, please contact admins.")
    # ADD A NEW USER
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players", ())
        amount_of_lines = cursor.fetchone()[0]
        if (amount_of_lines < 10000):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, nickname, discord_id) VALUES (%s, %s, %s)", (username, nickname, str(ctx.author.id),))
            await ctx.respond(f"Your discord account has successfully been registered with the current nickname {nickname} to participate ranked games! You can later change your nickname if you want.")
        else:
            await ctx.respond("The database is full. Please contact admins.")
# register ends


# CHANGENICK COMMAND
@bot.slash_command(name="changenick", description="Give yourself a new nickname")
async def changenick(ctx, nickname: str):
    # IF USERNAME EXISTS IN DATABASE, CHANGE THEIR NICKNAME
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_nickname = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET nickname = %s WHERE discord_id = %s", (nickname, str(ctx.author.id)))
        await ctx.respond(f"Your nickname has been updated! Your old nickname was {old_nickname}. Your new nickname is {nickname}")
        return
    else:
        ctx.respond(f"You have not yet registered. Please register by writing /register nickname. If problem persists contact admins.")
        return
# change nickname ends


# PRINTCLANS COMMAND
@bot.slash_command(name="printclans", description="Print all existing clannames")
async def printclans(ctx):
    existing_clans = await fetchExistingClannames()
    await ctx.respond("Currently existing clans are next: ")
    await ctx.send(existing_clans)
    await ctx.send("If you miss a clan, use '/registerclan' command!")  
# printclans ends


# CHANGECLAN COMMAND
@bot.slash_command(name="changeclan", description="Give yourself a new clanname")
async def changeclan(ctx, new_clanname: str):
    new_clanname = new_clanname.lower()
    # IF USER ID EXISTS IN DATABASE, CHANGE THEIR CLANNAME
    is_registered_result = await is_registered(str(ctx.author.id))
    if is_registered_result:
        existing_clans = await fetchExistingClannames()
        if new_clanname not in existing_clans:
            await ctx.respond(f"The clanname {new_clanname} is not part of existing clan names. First use '/registerclan'.")
            await ctx.send(f"Alternatively there was a typo. The currently existing clannames are: {existing_clans}. Clannames are automatically lower letters!")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_clan_id = cursor.fetchone()[0]
        cursor.execute("SELECT clanname FROM clans WHERE id = %s", (old_clan_id,))
        old_clanname = cursor.fetchone()[0]
        if (new_clanname == old_clanname):
            await ctx.respond(f"You already belong to the clan {new_clanname}")
            return
        else:
            cursor.execute("SELECT id FROM clans WHERE clanname = %s", (new_clanname,))
            new_clan_id = cursor.fetchone()[0]
            cursor.execute("UPDATE players SET clan_id = (%s)", (new_clan_id,))
            await ctx.respond(f"Your clanname has been updated. Your old clanname was {old_clanname}. Your new clanname is {new_clanname}")
            return
    else:
        await ctx.respond(f"You have not yet registered. Please register by writing /register nickname. If problem persists contact admins.")
        return
# change clanname ends

# ADD CLAN COMMAND
@bot.slash_command(name="registerclan", description="Give yourself a new clanname")
async def registerclan(ctx, clanname: str):
    clanname = clanname.lower()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clans WHERE clanname = %s", (clanname,))
    existing_clan = cursor.fetchone()

    if existing_clan is not None:
        await ctx.respond(f"The clan {clanname} already exists")
        return
    
    cursor.execute("INSERT INTO clans (clanname) VALUES (%s)", (clanname,))
    await ctx.respond(f"The clan {clanname} has been registered as a new clan!")
    return


# MYSCORE COMMAND
@bot.slash_command(name="myscore", description="Print your personal score and statistics")
async def myscore(ctx):
    is_registered_result = await is_registered(str(ctx.author.id))
    if not is_registered_result:
        ctx.respond(f"```You have not yet registered. Please register by writing /register nickname. If problem persists contact admins.```")
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
    cursor.execute("SELECT clanname FROM clans WHERE id = %s", (stats["clan_id"],))
    clanname = cursor.fetchone()[0]
    if stats["battles"] > 0:
        await ctx.respond(f"```Your {ctx.author.display_name} current stats are: \n points: {stats['points']}, \n winrate: {(stats['wins'] / stats['battles'])*100}%, \n battles: {stats['battles']}, \n avrg enemy rank: {round(stats['average_enemy_rank'], 0)}, \n clanname: {clanname}```")
    else:
        await ctx.respond(f"```Your {ctx.author.display_name} current stats are: \n points: {stats['points']}, \n winrate: 0%, \n battles: {stats['battles']}, \n avrg_enemy_rank: {round(stats['average_enemy_rank'], 0)}, \n clanname: {clanname}```")
# myscore ends


# TOP X COMMAND
# for example, user gives '/top 10' and bot gives scores of top10 players
@bot.slash_command(name="top", description="Print top players of all players")
async def top(ctx, number: int):

    number = int(number)
    scoreboard_text = f"SCOREBOARD TOP{number} PLAYERS"
    await ctx.respond("```**" + scoreboard_text.center(24) + "**```")

    cursor = conn.cursor()
    cursor.execute("""SELECT players.nickname, players.points, players.battles, players.wins, players.average_enemy_rank, clans.clanname 
                   FROM players 
                   LEFT JOIN clans ON players.clan_id = clans.id 
                   ORDER BY points DESC""",())

    scores_per_player = []
    top_players = cursor.fetchmany(number)
    
    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        if (item[2] > 0):
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {(item[3] / item[2]) * 100}%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        else:
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    await ctx.send("\n".join(scores_per_player))
    await ctx.send(f"```** Top{number} players have been printed! **```")
# top X ends


# CLANTOP X COMMAND
@bot.slash_command(name="topclanplayers", description="Print top players of a specific clan")
async def topclanplayers(ctx, number: int, clanname: str):

    clanname = clanname.lower()
    current_clans = await fetchExistingClannames()

    if clanname not in current_clans:
        await ctx.respond(f"```The clan {clanname} is not currently part of existing clans.```")
        await ctx.send(f"```Existing clans are: \n {current_clans}```")
        await ctx.send("```If you miss a clan, use '/registerclan' command!```")
        return

    number = int(number)
    scoreboard_text = f"SCOREBOARD TOP{number} PLAYERS OF {clanname}"
    await ctx.respond("```**" + scoreboard_text.center(24) + "**```")

    cursor = conn.cursor()
    cursor.execute("""SELECT players.nickname, players.points, players.battles, players.wins, players.average_enemy_rank, clans.clanname 
                   FROM players 
                   LEFT JOIN clans ON players.clan_id = clans.id
                   WHERE clans.clanname = %s
                   ORDER BY points DESC""",(clanname,))

    scores_per_player = []
    top_players = cursor.fetchmany(number)

    if (len(top_players) < 1):
        await ctx.send(f"```No players were found with clanname: '{clanname}'.```")
        await ctx.send(f"```Currently existing clannames are: \n {current_clans}```")
        return

    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        if (item[2] > 0):
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {(item[3] / item[2]) * 100}%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        else:
            printable_text = f"RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    await ctx.send("\n".join(scores_per_player))
    await ctx.send(f"```** Top{number} players of {clanname} have been printed! **```")
# clantop X ends


# CLAN LEADERBOARD COMMAND
# TOP X COMMAND
# for example, user gives '/top 10' and bot gives scores of top10 players
@bot.slash_command(name="clanleaderboard", description="Print top clans in order")
async def clanleaderboard(ctx, number: int):

    number = int(number)
    scoreboard_text = f"LEADERBOARD TOP{number} CLANS"
    await ctx.respond("```**" + scoreboard_text.center(24) + "**```")

    cursor = conn.cursor()
    cursor.execute("""SELECT clanname, points, battles, wins, average_enemyclan_rank
                   FROM clans
                   ORDER BY points DESC""",())

    scores_per_clan = []
    top_clans = cursor.fetchmany(number)
    
    calculator = 0
    for item in top_clans:
        calculator += 1
        printable_text = ""
        if (item[2] > 0):
            printable_text = f"RANK: {calculator}. \n clanname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {(item[3] / item[2]) * 100}%, \n avrg_enemyclan_rank: {round(item[4], 0)}"
        else:
            printable_text = f"RANK: {calculator}. \n clanname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemyclan_rank: {round(item[4], 0)}"
        scores_per_clan.append(f"``` {printable_text.center(24)} ```")
    await ctx.send("\n".join(scores_per_clan))
    await ctx.send(f"```** Top{number} clans have been printed! **```")
# clanleaderboard ends


@bot.slash_command(name="clanwarhistory", description="Print clanwar scores of the selected clan")
async def clanwarhistory(ctx, clanname: str, number: int):
    clanname = clanname.lower()
    existing_clans = await fetchExistingClannames()
    if clanname not in existing_clans:
        await ctx.respond(f"```The clanname {clanname} you selected is not currently existing.```")
        await ctx.send(f"```The clannames existing are: \n {existing_clans}```")
        await ctx.send("```If you are missing a clan, use command '/registerclan'```")
        return
    
    # first fetch the id of given clan, so it will be easier to find all clanwars containing that id in challenger or defender
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clans WHERE clanname = %s", (clanname,))
    wanted_clan_id = cursor.fetchone()[0]
    cursor.execute(""" SELECT clanwars.date, challenger_clan.clanname AS challenger_name, clanwars.challenger_won_rounds, defender_clan.clanname AS defender_name, clanwars.defender_won_rounds
                    FROM clanwars
                    LEFT JOIN clans AS challenger_clan ON clanwars.challenger_clan_id = challenger_clan.id
                    LEFT JOIN clans AS defender_clan ON clanwars.defender_clan_id = defender_clan.id
                    WHERE challenger_clan.id = %s OR defender_clan.id = %s
                    ORDER BY clanwars.date DESC""", (wanted_clan_id, wanted_clan_id,))
    clanwars = cursor.fetchmany(number)
    if (len(clanwars) >= 1):
        await ctx.respond(f"```The last {number} clanwars of clan {clanname} had next scores:```")
        for war in clanwars:
            await ctx.send(f"```date: {war[0]} \nchallenger_clanname {war[1]}, \nchallenger_points: {war[2]}, \ndefender_clanname: {war[3]}, \ndefender_points: {war[4]}```")
        await ctx.send(f"")
        return
    else:
        await ctx.respond(f"```The clanwarhistory of clan {clanname} is currently empty!```")
        await ctx.send("```If you think that there is a lack of information, please contact admins.```")
        await ctx.send(f"```Admins are supposed to use '/reportclanwar' to store scores received```")
        return
    # clanwarhistory ends
    

# REPORT CLANWAR COMMAND
@bot.slash_command(name="reportclanwar", description="After war with enemy clan, write scores here!")
async def reportclanwar(ctx):
    await ctx.respond("This command will be hard to do. i need to make sure both clans exist. I need to make sure there wont be douple reporting too.")
    await ctx.send("Also i will need to update not just clanwars datatable, but also clans datatable, and use already existing ranking system calculator for clans too...")
# reportclanwar ends


# EVENTANNOUNCE COMMAND
@bot.slash_command(name="eventannounce", description="Messages privately all players of channel about an approaching event!")
async def eventannounce(ctx, title: str, date: str, description:str):
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM clanleaders WHERE discord_id = %s", (str(ctx.author.id),))
    existing_leader = cursor.fetchone()
    if existing_leader is None:
        await ctx.respond("```You are currently not eligible to announce events.```")
        await ctx.send("```If you are a clan leader or clan admin, please contact Parrot.```")
        await ctx.send("```Parrot will give you a password for '/iamclanleader' command to register as a clan leader.```")
        return
    await ctx.respond(f"```{ctx.author.display_name}, I will help you to announce the event... \n. \n. \n```")

    # basis for messages
    channel_message = f"@everyone \nThere will be an important \n{title.upper()} \non {date.upper()} \nwhere \n{description}! \n. \n. \nClick this sword emoticon if you plan to join! \n. \n."
    private_message = f"There will be an important \n{title.upper()} \non {date.upper()} \nwhere \n{description}! \n. \n. \nPlease go to events of {ctx.guild.name} to click sword emoticon if u plan to join! \n. \n."
    
    # embed message everyone inside channel, add in sword emoticon
    # use embed message, otherwise cannot use bot emoticons on it
    channel_message_embed = discord.Embed(title="Event",
    description=channel_message)
    interactive_channel_message = await ctx.send(embed=channel_message_embed)
    await interactive_channel_message.add_reaction("⚔️")

    # direct message all players with normal string and encourage to add a sword emoticon
    for member in ctx.guild.members:
        if member is None:
            continue
        try:
            await member.send(private_message)
            print(f'Message sent to {member.name}')
        except discord.Forbidden:
            print(f'Cannot send message to {member.name}')
        except discord.HTTPException as e:
            print(f'Failed to send message to {member.name}: {e}')
    print(f"All members of {ctx.guild.name} have been messaged about the coming event of {title}!")
    return
# eventannounce ends


# EVENTANNOUNCE COMMAND
@bot.slash_command(name="iamclanleader", description="If you have password, use this to register as an admin or clanleader!")
async def iamclanleader(ctx, password:str):
    if (password != leader_password):
        await ctx.respond("```You have given wrong password to '/iamleader' command. \n If you are an admin or clanleader, ask Parrot for password.```")
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clanleaders WHERE discord_id = %s", (str(ctx.author.id),))
    alreadyin = cursor.fetchone()
    if alreadyin is not None:
        await ctx.respond("```You are already a registered clan leader!```")
        return
    else:
        cursor.execute("INSERT INTO clanleaders (discord_id) VALUES (%s)", (str(ctx.author.id),))
        await ctx.respond("```Congratulations. You have been added to clanleaders! \n Now you will be able to use '/eventannounce' and '/reportclanwarscores' commands```")
        return
# iamclanleader ends


@bot.slash_command(name="printclanleaders", description="Print all clan leaders who have registered with '/iamclanleader'!")
async def printclanleaders(ctx):
    cursor = conn.cursor()
    cursor.execute("SELECT players.username FROM players LEFT JOIN clanleaders ON players.discord_id = clanleaders.discord_id ORDER BY players.username DESC")
    allleaders = []
    allleadersdata = cursor.fetchall()
    for leader in allleadersdata:
        allleaders.append(leader[0])
    await ctx.respond(f"All currently registered leaders are: \n {allleaders}")



# CHALLENGE COMMAND
challenge_status = []
@bot.slash_command(name="challenge", description="Challenge enemy to duel!")
async def challenge(ctx, opponent: discord.Member):
    global challenge_status

    # CHECK NOT CHALLENGE ONESELF
    if (opponent.id == ctx.author.id):
        await ctx.respond("You may not challenge yourself!")
        return

    # CHECK CHALLENGER AND OPPONENT ARE REGISTERED, OTHERWISE NOTIFY AND RETURN
    opponent_is_registered = await is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.respond(f"The opponent {opponent.mention} has not yet been registered. Ask him to register before duel.")
        return
    
    challenger_is_registered = await is_registered(str(ctx.author.id))
    if not challenger_is_registered:
        await ctx.respond(f"The challenger {ctx.author.mention} has not yet been registered. Please register to be able to duel.")
        return
    
    if (ctx.author.id in challenge_status):
        await ctx.respond(f"You {ctx.author.mention} have already challenged somebody. Please cancel that before challenging a new player.")
        return
    
    await ctx.respond("Prosessing challenge...")

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
            await ctx.respond("FT7 expired.")
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
