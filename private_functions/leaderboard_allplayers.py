# leaderboard_allplayers.py
# updated 2nd october 2024

from services import conn

# LEADERBOARD ALLPLAYERS
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