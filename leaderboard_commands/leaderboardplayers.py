# leaderboardplayers.py
# updated 4th october 2024

from private_functions import _fetch_existing_clannames
from services import conn


async def cmd_leaderboardplayers(ctx, number: int, clanname: str):
    # print players of all clans
    if clanname == None:
        await _leaderboard_allplayers(ctx, number)
        return
    # print players of a specific clan
    else:
        await _leaderboard_clanplayers(ctx, number, clanname)
        return


# cmd_leaderboard_players ends


# ----------------------------------------
# ----------_LEADERBOARD_ALLPLAYERS-------
async def _leaderboard_allplayers(ctx, number: int):
    scores_per_player = []
    scores_per_player.append("``` ** LEADERBOARD PLAYERS **```")

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            players.nickname, 
            players.points, 
            players.battles, 
            players.wins, 
            players.average_enemy_rank, 
            clans.name 
        FROM players 
        LEFT JOIN clans ON players.clan_id = clans.id 
        ORDER BY points DESC
        """,
        (),
    )

    top_players = cursor.fetchmany(number)
    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        if item[2] > 0:
            printable_text = (
                f"    RANK: {calculator}. \n "
                f"nickname: {item[0]}, \n "
                f"points: {item[1]}, \n "
                f"battles: {item[2]}, \n "
                f"winrate: {round((item[3] / item[2]) * 100, 2)}%, \n "
                f"avrg_enemy_rank: {round(item[4], 0)}, \n "
                f"clanname: {item[5]}"
            )
        else:
            printable_text = (
                f"    RANK: {calculator}. \n "
                f"nickname: {item[0]}, \n "
                f"points: {item[1]}, \n "
                f"battles: {item[2]}, \n "
                f"winrate: 0%, \n "
                f"avrg_enemy_rank: {round(item[4], 0)}, \n "
                f"clanname: {item[5]}"
            )
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    scores_per_player.append(f"```  ** TOP{number} PLAYERS HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_player))


# _leaderboard_allplayers ends


# -------------------------------------------
# ----------_LEADERBOARD_CLANPLAYERS --------
async def _leaderboard_clanplayers(ctx, number: int, clanname: str):
    scores_per_player = []
    scores_per_player.append(f"``` ** LEADERBOARD PLAYERS OF {clanname.upper()} **```")

    clanname = clanname.lower()
    current_clans = await _fetch_existing_clannames()

    if clanname not in current_clans:
        await ctx.respond(
            f"```{clanname} is not part of existing clans: \n {current_clans} \n"
            f"Please use '/registerclan' to create a new clan.```",
            ephemeral=True,
        )
        return
    number = int(number)

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            players.nickname, 
            players.points, 
            players.battles, 
            players.wins, 
            players.average_enemy_rank, 
            clans.name 
        FROM players 
        LEFT JOIN clans ON players.clan_id = clans.id
        WHERE clans.name = %s
        ORDER BY points DESC
        """,
        (clanname,),
    )
    top_players = cursor.fetchmany(number)
    if len(top_players) < 1:
        await ctx.respond(f"No players were found with the clanname:'{clanname}'.")
        return

    calculator = 0
    for item in top_players:
        calculator += 1
        printable_text = ""
        if item[2] > 0:
            printable_text = (
                f"  RANK: {calculator}. \n "
                f"nickname: {item[0]}, \n "
                f"points: {item[1]}, \n "
                f"battles: {item[2]}, \n "
                f"winrate: {round((item[3] / item[2]) * 100, 2)}%, \n "
                f"avrg_enemy_rank: {round(item[4], 0)}, \n clanname: {item[5]}"
            )
        else:
            printable_text = (
                f"  RANK: {calculator}. \n "
                f"nickname: {item[0]}, \n "
                f"points: {item[1]}, \n "
                f"battles: {item[2]}, \n "
                f"winrate: 0%, \n "
                f"avrg_enemy_rank:  {round(item[4], 0)}, \n "
                f"clanname: {item[5]}"
            )
        scores_per_player.append(f"``` {printable_text.center(24)} ```")
    scores_per_player.append(f"``` ** TOP{number} PLAYERS OF {clanname} HAVE BEEN PRINTED! **```")
    await ctx.respond("".join(scores_per_player))


# _leaderboard_clanplayers ends
