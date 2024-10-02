# printmyft7.py
# updated 2nd october 2024

import discord
from services import conn
from private_functions import _print_myft7s_against

async def cmd_printmyft7(ctx, number: int, opponent: discord.Member):
    if (opponent!=None):
        await _print_myft7s_against(ctx, opponent, number)
        return
    duel_history = []
    duel_history.append(f"```** {number} FT7's OF {ctx.author.display_name.upper()} **```")
    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await _is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(f"{ctx.author.mention} has not yet been registered. Please use '/registerplayer'.", ephemeral=True)
        return
    
    # fetch all duels where challenger or opponent was author
    cursor = conn.cursor()
    cursor.execute("""SELECT duels.date, challenger_player.nickname, opponent_player.nickname, duels.challenger_score, duels.opponent_score
                   FROM duels
                   LEFT JOIN players AS challenger_player ON duels.challenger_discord_id = challenger_player.discord_id
                   LEFT JOIN players AS opponent_player ON duels.opponent_discord_id = opponent_player.discord_id
                   WHERE (challenger_player.discord_id = %s OR opponent_player.discord_id = %s)
                   ORDER BY duels.date DESC""", (str(ctx.author.id), str(ctx.author.id),))
    duels = cursor.fetchmany(number)

    if len(duels) < 1:
        await ctx.respond(f"{ctx.author.mention} does not have any duels!")
        return
    
    for duel in duels: # 0 = date, 1 = challenger_nick, 2 = opponent_nick, 3 = challenger_score, 4 = opponent_score
        message = f"```{duel[0]} \n{duel[1]} vs {duel[2]} [{duel[3]}-{duel[4]}]```"
        duel_history.append(message)
    duel_history.append(f"```{number} MOST RECENT FT7'S OF {ctx.author.display_name.upper()} HAVE BEEN PRINTED!```")
    await ctx.respond("".join(duel_history))
    return