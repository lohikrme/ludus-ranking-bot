# myscore.py
# updated 4th october 2024

from private_functions import _is_registered
from services import conn


async def cmd_myscore(ctx):
    # checks if player is registered
    is_registered_result = await _is_registered(str(ctx.author.id))
    if not is_registered_result:
        await ctx.respond(f"Please register before printing your scores.", ephemeral=True)
        return

    # fetches data of player from the db
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT nickname, points, battles, wins, average_enemy_rank, clan_id 
        FROM players 
        WHERE discord_id = %s
        """,
        (str(ctx.author.id),),
    )
    score = cursor.fetchone()
    stats = {
        "nickname": score[0],
        "points": score[1],
        "battles": score[2],
        "wins": score[3],
        "average_enemy_rank": score[4],
        "clan_id": score[5],
    }

    # prints player's score
    cursor.execute("SELECT name FROM clans WHERE id = %s", (stats["clan_id"],))
    clanname = cursor.fetchone()[0]
    if stats["battles"] > 0:
        await ctx.respond(
            f"```     {stats['nickname'].upper()}: \n "
            f"points: {stats['points']}, \n "
            f"winrate: {round((stats['wins'] / stats['battles'])*100, 2)}%, \n "
            f"battles: {stats['battles']}, \n "
            f"avrg enemy rank: {round(stats['average_enemy_rank'], 0)}, \n "
            f"clanname: {clanname}```"
        )
    else:
        await ctx.respond(
            f"```     {stats['nickname'].upper()}: \n "
            f"points: {stats['points']}, \n "
            f"winrate: 0%, \n "
            f"battles: {stats['battles']}, \n "
            f"avrg_enemy_rank: {round(stats['average_enemy_rank'], 0)}, \n "
            f"clanname: {clanname}```"
        )


# myscore ends
