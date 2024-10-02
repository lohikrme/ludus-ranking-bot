# myscore.py
# updated 2nd october 2024

from private_functions import _is_registered
from services import conn

async def cmd_myscore(ctx):
    is_registered_result = await _is_registered(str(ctx.author.id))
    if not is_registered_result:
        await ctx.respond(f"Please register before printing your scores.", ephemeral=True)
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