# leaderboardclans.py
# updated 16th december 2024

from services import conn


async def cmd_leaderboardclans(ctx):
    cursor = conn.cursor()

    # initiate print
    scores_per_clan = []
    scores_per_clan.append(f"``` ** LEADERBOARD CLANS **```")

    # fetch stats of active clans who have battles > 0
    cursor.execute(
        """
        SELECT clans.name, clans.points, clans.battles, clans.wins, clans.average_enemy_rank
        FROM clans
        WHERE clans.battles > 0
        ORDER BY clans.points DESC
        """,
        (),
    )
    top_clans = cursor.fetchmany(50)

    # item 0 = name, 1 = points, 2 = battles, 3 = wins, 4 = avrg_enemy_rank
    calculator = 0
    for item in top_clans:
        if item[0] == "none":
            continue
        calculator += 1
        printable_text = ""
        if item[2] > 0:
            printable_text = (
                f"   RANK {calculator}. CLAN: \n "
                f"clanname: {item[0]}, \n "
                f"points: {item[1]}, \n "
                f"battles: {item[2]}, \n "
                f"winrate: {round((item[3] / item[2]) * 100, 2)}%, \n "
                f"avrg_enemy_rank: {round(item[4], 0)}"
            )
        else:
            printable_text = (
                f"   RANK {calculator}. CLAN: \n "
                f"clanname: {item[0]}, \n "
                f"points: {item[1]}, \n "
                f"battles: {item[2]}, \n "
                f"winrate: 0%, \n "
                f"avrg_enemy_rank: {round(item[4], 0)}"
            )
        scores_per_clan.append(f"``` {printable_text.center(24)} ```")
    scores_per_clan.append(f"```  ** TOP CLANS HAVE BEEN PRINTED! **```")

    # print 14 records at time!
    first_message = True
    for i in range(0, len(scores_per_clan), 14):
        chunk = scores_per_clan[i : i + 14]
        if first_message:
            await ctx.respond("".join(chunk))
            first_message = False
        else:
            await ctx.send("".join(chunk))
