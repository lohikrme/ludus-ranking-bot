# leaderboardclans.py
# updated 2nd october 2024

from services import conn

async def cmd_leaderboardclans(ctx, number: int):
    scores_per_clan = []
    scores_per_clan.append(f"``` ** LEADERBOARD CLANS **```")

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
            printable_text = f"    RANK: {calculator}. \n clanname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: {round((item[3] / item[2]) * 100, 2)}%, \n avrg_enemyclan_rank: {round(item[4], 0)}"
        else:
            printable_text = f"    RANK: {calculator}. \n clanname: {item[0]}, \n points: {item[1]}, \n battles: {item[2]}, \n winrate: 0%, \n avrg_enemyclan_rank: {round(item[4], 0)}"
        scores_per_clan.append(f"``` {printable_text.center(24)} ```")
    scores_per_clan.append(f"```  ** TOP{number} CLANS HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_clan))
# leaderboardclans ends