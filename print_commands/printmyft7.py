# printmyft7.py
# updated 10th october 2024

import discord
from services import conn
from private_functions import _is_registered


async def cmd_printmyft7(ctx, number: int, opponent: discord.Member):
    # print ft7s against a specific opponent
    if opponent != None:
        await _print_myft7s_against(ctx, number, opponent)
        return
    # print ft7s against any opponent
    else:
        await _print_myft7s(ctx, number)


# cmd_printmyft7 ends


# ---------------------------------------------------
# -----------_PRINT_MYFT7S_AGAINST ------------------
async def _print_myft7s_against(ctx, number: int, opponent: discord.Member):
    cursor = conn.cursor()

    duel_history = []

    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await _is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(
            f"You have not been registered yet! Please use '/registerplayer'.",
            ephemeral=True,
        )
        return

    # make sure opponent is registered before trying to find him from the database
    opponent_is_registered = await _is_registered(str(opponent.id))
    if not opponent_is_registered:
        await ctx.respond(
            f"{opponent.display_name} has not yet been registered. Please use '/registerplayer'.",
            ephemeral=True,
        )
        return

    # fetch author's and opponent's nickname from database
    cursor.execute("SELECT nickname FROM players where discord_id = %s", (str(ctx.author.id),))
    author_nickname = cursor.fetchone()[0]

    cursor.execute("SELECT nickname FROM players where discord_id = %s", (str(opponent.id),))
    opponent_nickname = cursor.fetchone()[0]

    # add first sentence to the printable text
    duel_history.append(
        f"```** {number} FT7s OF {author_nickname.upper()} vs {opponent_nickname.upper()} **```"
    )

    # fetch all duels of author agains the specific person
    # note that author can be either challenger or opponent in the database
    cursor.execute(
        """
        SELECT 
            duels.date, 
            challenger_player.nickname, 
            opponent_player.nickname, 
            duels.challenger_score, 
            duels.opponent_score
        FROM duels
        LEFT JOIN players AS challenger_player ON duels.challenger_discord_id = challenger_player.discord_id
        LEFT JOIN players AS opponent_player ON duels.opponent_discord_id = opponent_player.discord_id
        WHERE (challenger_player.discord_id = %s OR challenger_player.discord_id = %s) 
        AND (opponent_player.discord_id = %s OR opponent_player.discord_id = %s)
        ORDER BY duels.date DESC
        """,
        (
            str(ctx.author.id),
            str(opponent.id),
            str(ctx.author.id),
            str(opponent.id),
        ),
    )

    duels = cursor.fetchmany(number)
    if len(duels) < 1:
        await ctx.respond(f"{author_nickname} does not have duels against {opponent_nickname}")
        return

    # 0 = date, 1 = chall_nick, 2 = oppo_nick, 3 = chall_score, 4 = oppo_score
    for duel in duels:
        message = f"```ft7 on {duel[0]} \n{duel[1]} vs {duel[2]} [{duel[3]}-{duel[4]}]```"
        duel_history.append(message)
    duel_history.append(
        f"```{number} MOST RECENT FT7s OF {author_nickname.upper()}"
        f" vs {opponent_nickname.upper()} HAVE BEEN PRINTED!```"
    )
    await ctx.respond("".join(duel_history))
    return


# _print_myft7s_against ends


# ---------------------------------------
# ------------ _PRINT_MYFT7S-------------
async def _print_myft7s(ctx, number: int):
    cursor = conn.cursor()
    duel_history = []

    # make sure challenger is registered before trying to find him from the database
    author_is_registered = await _is_registered(str(ctx.author.id))
    if not author_is_registered:
        await ctx.respond(
            f"{ctx.author.mention} has not yet been registered. Please use '/registerplayer'.",
            ephemeral=True,
        )
        return

    # fetch author's nickname from database
    cursor.execute("SELECT nickname FROM players where discord_id = %s", (str(ctx.author.id),))
    author_nickname = cursor.fetchone()[0]

    # add first sentence to the printable text
    duel_history.append(f"```** {number} FT7s OF {author_nickname.upper()} **```")

    # fetch all duels where author was either challenger or opponent
    cursor.execute(
        """
        SELECT 
            duels.date, 
            challenger_player.nickname, 
            opponent_player.nickname, 
            duels.challenger_score, 
            duels.opponent_score
        FROM duels
        LEFT JOIN players AS challenger_player ON duels.challenger_discord_id = challenger_player.discord_id
        LEFT JOIN players AS opponent_player ON duels.opponent_discord_id = opponent_player.discord_id
        WHERE (challenger_player.discord_id = %s OR opponent_player.discord_id = %s)
        ORDER BY duels.date DESC""",
        (
            str(ctx.author.id),
            str(ctx.author.id),
        ),
    )
    duels = cursor.fetchmany(number)

    if len(duels) < 1:
        await ctx.respond(f"{author_nickname} does not have any duels!")
        return

    # duel 0 = date, 1 = chall_nick, 2 = oppo_nick, 3 = chall_score, 4 = oppo_score
    for duel in duels:
        message = f"```{duel[0]} \n{duel[1]} vs {duel[2]} [{duel[3]}-{duel[4]}]```"
        duel_history.append(message)

    duel_history.append(
        f"```{number} MOST RECENT FT7'S OF {author_nickname.upper()} HAVE BEEN PRINTED!```"
    )

    await ctx.respond("".join(duel_history))
    return


# _print_myft7s ends
