# leaderboardclans.py
# updated 4th october 2024

from services import conn


async def cmd_leaderboardclans(ctx, number: int):
    scores_per_clan = []
    scores_per_clan.append(f"``` ** LEADERBOARD CLANS **```")

    number = int(number)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name, points, battles, wins, average_enemy_rank
        FROM clans
        ORDER BY points DESC
        """,
        (),
    )
    top_clans = cursor.fetchmany(number)

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
    scores_per_clan.append(f"```  ** TOP{number} CLANS HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_clan))


# cmd_leaderboardclans ends
