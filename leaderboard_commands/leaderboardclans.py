# leaderboardclans.py
# updated 1st december 2024

from services import conn


async def cmd_leaderboardclans(ctx, number: int):
    cursor = conn.cursor()

    # initiate print
    scores_per_clan = []
    scores_per_clan.append(f"``` ** LEADERBOARD CLANS **```")

    number = int(number)

    # fetch stats of active clans who have a registered admin
    # cursor.execute(
    #    """
    #    SELECT clans.name, clans.points, clans.battles, clans.wins, clans.average_enemy_rank
    #    FROM clans
    #    INNER JOIN players ON players.clan_id = clans.id
    #    INNER JOIN admins ON admins.discord_id = players.discord_id
    #    ORDER BY clans.points DESC
    #    """,
    #    (),
    # )

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

    # print 14 records at time!
    first_message = True
    for i in range(0, len(scores_per_clan), 14):
        chunk = scores_per_clan[i : i + 14]
        if first_message:
            await ctx.respond("".join(chunk))
            first_message = False
        else:
            await ctx.send("".join(chunk))
    # await ctx.respond("".join(scores_per_clan))


# cmd_leaderboardclans ends
