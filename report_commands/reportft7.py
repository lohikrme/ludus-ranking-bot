# reportft7.py
# updated 4th october 2024

import discord
import asyncio
from bot_instance import bot
from private_functions import (
    _is_registered,
    _update_player_points,
    _update_duels_history,
)
from services import conn


# store here ft7 status globally, so one player can only be reporting one ft7 at time
ft7_status = []


# CMD_REPORTFT7 STARTS
async def cmd_reportft7(ctx, opponent: discord.Member, my_score: int, opponent_score: int):
    cursor = conn.cursor()
    global ft7_status

    # step 0: check opponent is different than challenger
    if opponent.id == ctx.author.id:
        await ctx.respond("You may not ft7 yourself!", ephemeral=True)
        return

    # step 1: check challenger and opponent are registered
    challenger_is_registered = await _is_registered(str(ctx.author.id))
    if not challenger_is_registered:
        await ctx.respond(
            "You have not been registered. Please use '/registerplayer' before reportduel.",
            ephemeral=True,
        )
        return

    opponent_is_registered = await _is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.respond(
            f"Your opponent {opponent.display_name} has not been registered. "
            f"Please use '/registerplayer'.",
            ephemeral=True,
        )
        return

    # step 2: check that scores are not equal, and challenger is not already in ft7 (to avoid spam)
    if my_score == opponent_score:
        await ctx.respond(
            f"Your score {my_score} and opponent score {opponent_score} are equal. "
            f"Stalemate is not counted.",
            ephemeral=True,
        )
        return

    if ctx.author.id in ft7_status:
        await ctx.respond(
            f"You {ctx.author.mention} are already in ft7 with somebody.",
            ephemeral=True,
        )
        return

    # step 3: program begins! add author to ft7_status to prevent spam
    ft7_status.append(ctx.author.id)
    await ctx.respond(
        f"Please wait for {opponent.display_name} to verify the ft7 scores!",
        ephemeral=True,
    )

    # step 4: send to opponent private embed message which asks for approval of scores
    approval_embed = discord.Embed(
        title=f"Confirm ft7 results:",
        description=(
            f"{ctx.author.display_name} vs {opponent.display_name} \n"
            f"{my_score}-{opponent_score}\n click ✅approve   🚫disagree."
        ),
    )
    approval_msg = await opponent.send(embed=approval_embed)
    await approval_msg.add_reaction("✅")
    await approval_msg.add_reaction("🚫")

    try:
        reaction, user = await bot.wait_for(
            "reaction_add",
            timeout=300.0,
            check=lambda reaction, user: user == opponent
            and str(reaction.emoji) in ["✅", "🚫"]
            and reaction.message.id == approval_msg.id,
        )
    except asyncio.TimeoutError:
        await opponent.send(f"FT7 {ctx.author.display_name} vs {opponent.display_name} expired!")
        await ctx.author.send(f"FT7 {ctx.author.display_name} vs {opponent.display_name} expired!")
        return
    except asyncio.CancelledError:
        return

    # step 5: if scores are approved, calculate winner
    if str(reaction.emoji) == "✅":
        challenger_won = False
        if my_score > opponent_score:
            challenger_won = True

        # step 6: store scores and ranks into database
        if challenger_won:
            await _update_player_points(ctx.author, opponent, True)
            await _update_duels_history(str(ctx.author.id), str(opponent.id), my_score, opponent_score)
        else:
            await _update_player_points(ctx.author, opponent, False)
            await _update_duels_history(str(ctx.author.id), str(opponent.id), my_score, opponent_score)

        # step 7: notify users of their new points and pointchange
        if challenger_won:
            ft7_status.remove(ctx.author.id)
            cursor.execute(
                "SELECT points, old_points FROM players WHERE discord_id = %s",
                (str(ctx.author.id),),
            )
            challenger_points = cursor.fetchone()
            challenger_new_points = challenger_points[0]
            challenger_old_points = challenger_points[1]
            cursor.execute(
                "SELECT points, old_points FROM players WHERE discord_id = %s",
                (str(opponent.id),),
            )
            opponent_points = cursor.fetchone()
            opponent_new_points = opponent_points[0]
            opponent_old_points = opponent_points[1]
            challenger_win_embed = discord.Embed(
                title=f"{ctx.author.display_name} has won against {opponent.display_name}!",
                description=(
                    f"{ctx.author.mention} new points: "
                    f"{challenger_new_points}(+{challenger_new_points-challenger_old_points}) \n"
                    f"{opponent.mention} new points: "
                    f"{opponent_new_points}(-{opponent_old_points - opponent_new_points})"
                ),
            )
            await ctx.author.send(embed=challenger_win_embed)
            await opponent.send(embed=challenger_win_embed)
            return

        else:
            ft7_status.remove(ctx.author.id)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT points, old_points FROM players WHERE discord_id = %s",
                (str(ctx.author.id),),
            )
            challenger_points = cursor.fetchone()
            challenger_new_points = challenger_points[0]
            challenger_old_points = challenger_points[1]
            cursor.execute(
                "SELECT points, old_points FROM players WHERE discord_id = %s",
                (str(opponent.id),),
            )
            opponent_points = cursor.fetchone()
            opponent_new_points = opponent_points[0]
            opponent_old_points = opponent_points[1]
            defender_win_embed = discord.Embed(
                title=f"{opponent.display_name} has won against {ctx.author.display_name}!",
                description=(
                    f"{opponent.mention} new points: "
                    f"{opponent_new_points}(+{opponent_new_points - opponent_old_points}) \n"
                    f"{ctx.author.mention} new points: "
                    f"{challenger_new_points}(-{challenger_old_points - challenger_new_points})"
                ),
            )
            await ctx.author.send(embed=defender_win_embed)
            await opponent.send(embed=defender_win_embed)

            # databases updated and players notified of new stats successfully
            return

    # step 8: if scores are disagreed, notify challenger that opponent disagrees
    if str(reaction.emoji) == "🚫":
        await ctx.author.send(f"{opponent.display_name} has disagreed with your ft7 scores!")
        await opponent.send(f"You have disagreed with {ctx.author.display_name}'s ft7 scores ")
        return


# report ft7 ends
