# print_myft7s_against.py
# updated 2nd october 2024

from services import conn
import discord

# PRINT PLAYER'S FT7S
async def _print_myft7s_against(ctx, opponent: discord.Member, number: int):
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
# print my ft7s against ends