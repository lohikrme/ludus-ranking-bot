
# updated 2nd october 2024

import datetime
from services import conn
import discord


# -------- PRIVATE FUNCTIONS -----------

# USE THIS TO UPDATE DUELS DATATABLE HISTORY
async def _update_duels_history(challenger_discord_id: str, opponent_discord_id: str, challenger_score: int, opponent_score: int):
    date = datetime.datetime.now()
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO duels (date, challenger_discord_id, opponent_discord_id, challenger_score, opponent_score) VALUES (%s, %s, %s, %s, %s)", (date, challenger_discord_id, opponent_discord_id, challenger_score, opponent_score,))
# update duels history ends  
  

# USE THIS TO CHECK IF USER REGISTERED
async def _is_registered(discord_id: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE discord_id = %s", (discord_id,))
    existing_user = cursor.fetchone()

    if existing_user is not None: # user is registered
        return True
    
    return False # user is not registered
# is registered ends


# USE TO INFO USER OF EXISTING CLANNAMES
async def _fetchExistingClannames():
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM clans", ())
    clannames = cursor.fetchall()
    current_clans = []
    for item in clannames:
        current_clans.append(item[0])
    return current_clans
# fetch existing clannames ends


# print all players
async def _leaderboard_allplayers(ctx, number: int):
    scores_per_player = []
    scores_per_player.append("``` ** LEADERBOARD PLAYERS **```")

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
            printable_text = f"    RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {round((item[3] / item[2]) * 100, 2)}%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        else:
            printable_text = f"    RANK: {calculator}. \n nickname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    scores_per_player.append(f"```  ** TOP{number} PLAYERS HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_player))
# leaderboard_allplayers ends


# PRINTMYDUELSAGAINST 
async def _printmyduelssagainst(ctx, opponent: discord.Member, number: int):
    duel_history = []
    duel_history.append(f"```** {number} FT7s OF {ctx.author.display_name.upper()} vs {opponent.display_name.upper()} **```")
    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await _is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(f"You have not been registered yet! Please use '/registerplayer'.", ephemeral=True)
        return
    # make sure opponent is registered before trying to find him from the database
    opponent_is_registered = await _is_registered(str(opponent.id))
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
    if len(duels) < 1:
        await ctx.respond(f"{ctx.author.mention} does not have duels against {opponent.display_name}")
        return

    for duel in duels: # 0 = date, 1 = challenger_nick, 2 = opponent_nick, 3 = challenger_score, 4 = opponent_score
        message = f"```ft7 on {duel[0]} \n{duel[1]} vs {duel[2]} [{duel[3]}-{duel[4]}]```"
        duel_history.append(message)
    duel_history.append(f"```{number} MOST RECENT FT7s OF {ctx.author.display_name.upper()} vs {opponent.display_name.upper()} HAVE BEEN PRINTED!```")
    await ctx.respond("".join(duel_history))
    return
        
# print my duels against ends


# UPDATE CLAN POINTS IN DATABASE
async def _update_clan_points(challenger_clan_id: int, defender_clan_id: int, challenger_win: bool):
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
async def _update_player_points(challenger, opponent, challenger_win: bool):

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