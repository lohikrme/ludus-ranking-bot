# reportclanwar.py
# updated 4th october 2024

import datetime
from services import conn
from private_functions import _fetch_existing_clannames, _update_clan_points
import discord
from bot_instance import bot
import asyncio


# store here clanwar status globally, so one admin can only be reporting one clanwar at time
clanwar_status = []


# CMD_REPORTCLANWAR STARTS
async def cmd_reportclanwar(
    ctx,
    year: int,
    month: int,
    day: int,
    challenger_clanname: str,
    challenger_score: int,
    opponent_clanname: str,
    opponent_score: int,
):
    # initiate important variables
    global clanwar_status
    all_admin_ids = []
    all_opponent_clanmember_ids = []
    opponent_admin_ids = []

    ### step1: validate that ctx.author is a registered admin and is not in clanwar already
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    author_is_admin = cursor.fetchone()
    if author_is_admin is None:
        await ctx.respond(
            "```Only admins registered with '/registeradmin' can report clanwar scores!```",
            ephemeral=True,
        )
        return

    if ctx.author.id in clanwar_status:
        await ctx.respond(
            f"You {ctx.author.mention} are already in clanwar with some clan.",
            ephemeral=True,
        )
        return

    ### step2: validate date
    date_is_valid = True
    try:
        date = datetime.datetime(year, month, day)
    except ValueError:
        date_is_valid = False
    if date_is_valid == False:
        await ctx.respond(
            "```The date you gave is not a real date. "
            "Please make sure year, month and day are correct!```",
            ephemeral=True,
        )
        return

    ### step3: validate challenger and opponent clannames
    existing_clans = await _fetch_existing_clannames()

    # challenger clan must exist
    if challenger_clanname not in existing_clans:
        await ctx.respond(
            f"```The challenger_clanname {challenger_clanname} wasn't part of: \n"
            f"{existing_clans}. \n"
            f"If your clan's name is missing, please use '/registerclan'```",
            ephemeral=True,
        )
        return

    # opponent clan must exist
    if opponent_clanname not in existing_clans:
        await ctx.respond(
            f"```The challenger_clanname {challenger_clanname} wasn't part of: \n"
            f"{existing_clans}. \n"
            f"If your clan's name is missing, please use '/registerclan'```",
            ephemeral=True,
        )
        return

    ### step 4: check that challenger_clanname is same as author's clanname
    cursor.execute(
        """SELECT clans.name 
                   FROM clans
                   LEFT JOIN players ON players.clan_id = clans.id
                   WHERE players.discord_id = %s""",
        (str(ctx.author.id),),
    )
    authorclanname = cursor.fetchone()[0]
    if authorclanname != challenger_clanname:
        await ctx.respond(
            f"challenger_clanname did not match to author's clan. \n"
            f"{ctx.author.mention} belongs to clan '{authorclanname}', \n"
            f"while challenger_clanname was '{challenger_clanname}'",
            ephemeral=True,
        )
        return

    ### step 5: check that opponent_clanname has a registered admin, and store id for later use

    # first fetch opponent clan id
    cursor.execute("SELECT id FROM clans WHERE name = %s", (opponent_clanname,))
    opponent_clan_id = cursor.fetchone()[0]

    # second fetch all admin ids
    cursor.execute("SELECT discord_id FROM admins")
    all_admins = cursor.fetchall()
    for admin in all_admins:
        all_admin_ids.append(admin[0])

    # third fetch all opponent clan member ids
    cursor.execute(
        "SELECT players.discord_id FROM players WHERE players.clan_id = %s",
        (opponent_clan_id,),
    )

    # see if an admin id is part of all opponent clanmembers
    opponent_players = cursor.fetchall()
    for player in opponent_players:
        all_opponent_clanmember_ids.append(player[0])

    for admin_id in all_admin_ids:
        if admin_id in all_opponent_clanmember_ids:
            opponent_admin_ids.append(admin_id)

    if len(opponent_admin_ids) < 1:
        await ctx.respond(
            "Opponent clan does not have a registered admin! "
            "They need one to confirm the clanwar results.",
            ephemeral=True,
        )
        return

    ### step 6: send approval message to all opponent admins, or cancel after 24h wait time
    clanwar_status.append(ctx.author.id)

    await ctx.respond(
        embed=discord.Embed(
            title="",
            description=f"Waiting for opponent clan's admins to confirm: \n"
            f"{challenger_clanname} vs {opponent_clanname} \n{challenger_score}-{opponent_score}",
        )
    )

    # define a function that messages all opponent admins about the score
    # this function will be called several times, one admin at a time
    async def send_approval_message(
        admin_id,
        ctx,
        opponent_admin_ids,
        challenger_clanname,
        challenger_score,
        opponent_clanname,
        opponent_score,
        stop_listening_emoticons_event,
    ):
        # this fetch will later use the previously found opponent_admin_ids array
        opponent_admin = await bot.fetch_user(admin_id)
        # this embed message will be sent to all opponent admins
        approval_embed = discord.Embed(
            title=f"Confirm clanwar results:",
            description=(
                f"{challenger_clanname} vs {opponent_clanname} \n"
                f"{challenger_score}-{opponent_score}\n click ✅approve   🚫disagree."
            ),
        )
        approval_msg = await opponent_admin.send(embed=approval_embed)
        await approval_msg.add_reaction("✅")
        await approval_msg.add_reaction("🚫")

        # after message has been sent, bot will wait for reactions until message expires
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                timeout=3600.0,
                check=lambda reaction, user: user == opponent_admin
                and str(reaction.emoji) in ["✅", "🚫"]
                and reaction.message.id == approval_msg.id,
            )
        except asyncio.TimeoutError:
            await opponent_admin.send(f"Clanwar reporting expired!")
            clanwar_status.remove(ctx.author.id)
            return
        except asyncio.CancelledError:
            await opponent_admin.send(f"Clanwar reporting expired!")
            clanwar_status.remove(ctx.author.id)
            return

        # HANDLE REACTIONS
        if str(reaction.emoji) == "✅":
            # if an admin has already answered, do not listen
            if stop_listening_emoticons_event.is_set():
                return
            # so far no admin has answered, so stop listening now on
            stop_listening_emoticons_event.set()
            clanwar_status.remove(ctx.author.id)

            ### step7: if all previous is ok, store given data into clanwars datatable
            cursor.execute("SELECT id from clans WHERE name = %s", (challenger_clanname,))
            challenger_clan_id = cursor.fetchone()[0]
            cursor.execute("SELECT id from clans WHERE name = %s", (opponent_clanname,))
            opponent_clan_id = cursor.fetchone()[0]
            cursor.execute(
                """
                INSERT INTO clanwars (
                    date, 
                    challenger_clan_id, 
                    opponent_clan_id, 
                    challenger_score, 
                    opponent_score
                ) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    date,
                    challenger_clan_id,
                    opponent_clan_id,
                    challenger_score,
                    opponent_score,
                ),
            )

            ### step8: solves first which clan won, then update_clan_points()
            challenger_won = False
            stalemate = False

            # stalemate
            if challenger_score == opponent_score:
                stalemate = True
                challenger_won = False
                await _update_clan_points(
                    challenger_clan_id, opponent_clan_id, challenger_won, stalemate
                )

            # challenger clan won
            if challenger_score > opponent_score:
                challenger_won = True
                await _update_clan_points(
                    challenger_clan_id, opponent_clan_id, challenger_won, stalemate
                )

            # opponent clan won
            else:
                challenger_won = False
                await _update_clan_points(
                    challenger_clan_id, opponent_clan_id, challenger_won, stalemate
                )

            ### step9: notify author's channel and opponent admins of clanwar results and ranks
            cursor.execute(
                "SELECT points, old_points FROM clans WHERE id = %s",
                (challenger_clan_id,),
            )
            challenger_stats = cursor.fetchone()
            cursor.execute(
                "SELECT points, old_points FROM clans WHERE id = %s",
                (opponent_clan_id,),
            )
            opponent_stats = cursor.fetchone()

            if stalemate:

                challenger_new_points = challenger_stats[0]
                challenger_old_points = challenger_stats[1]

                opponent_new_points = opponent_stats[0]
                opponent_old_points = opponent_stats[1]

                pointchange = abs(challenger_new_points - challenger_old_points)

                opponent_sign = ""
                challenger_sign = ""

                if challenger_new_points - challenger_old_points > 0:
                    challenger_sign = "+"
                    opponent_sign = "-"

                elif challenger_new_points - challenger_old_points < 0:
                    opponent_sign = "+"
                    challenger_sign = "-"

                await ctx.respond(
                    f"```{date.strftime('%x')} \n"
                    f"STALEMATE {challenger_clanname} vs {opponent_clanname} "
                    f"with scores {challenger_score}-{opponent_score}! \n"
                    f"{challenger_clanname} new points:"
                    f"{challenger_new_points}({challenger_sign}{pointchange}). \n"
                    f"{opponent_clanname} new points:"
                    f"{opponent_new_points}({opponent_sign}{pointchange}).```"
                )
                for id in opponent_admin_ids:
                    user = await bot.fetch_user(id)
                    await user.send(
                        f"```{date.strftime('%x')} \n"
                        f"STALEMATE {challenger_clanname} vs {opponent_clanname} "
                        f"with scores {challenger_score}-{opponent_score}! \n"
                        f"{challenger_clanname} new points:"
                        f"{challenger_stats[0]}(+{pointchange}). \n"
                        f"{opponent_clanname} new points:"
                        f"{opponent_stats[0]}(-{pointchange}).```"
                    )
                return

            elif challenger_won:
                pointchange = challenger_stats[0] - challenger_stats[1]
                await ctx.respond(
                    f"```{date.strftime('%x')} \n"
                    f"{challenger_clanname} has won the clanwar "
                    f"against {opponent_clanname} with scores "
                    f"{challenger_score}-{opponent_score}! \n"
                    f"{challenger_clanname} new points:"
                    f"{challenger_stats[0]}(+{pointchange}). \n"
                    f"{opponent_clanname} new points:"
                    f"{opponent_stats[0]}(-{pointchange}).```"
                )
                for id in opponent_admin_ids:
                    user = await bot.fetch_user(id)
                    await user.send(
                        f"```{date.strftime('%x')} \n"
                        f"{challenger_clanname} has won the clanwar against {opponent_clanname} "
                        f"with scores {challenger_score}-{opponent_score}! \n"
                        f"{challenger_clanname} new points:{challenger_stats[0]}(+{pointchange}). \n"
                        f"{opponent_clanname} new points:{opponent_stats[0]}(-{pointchange}).```"
                    )
                return
            else:
                pointchange = challenger_stats[1] - challenger_stats[0]
                await ctx.respond(
                    f"```{date.strftime('%x')} \n"
                    f"{opponent_clanname} has won the clanwar against {challenger_clanname} "
                    f"with scores {opponent_score}-{challenger_score}! \n"
                    f"{opponent_clanname} new points:{opponent_stats[0]}(+{pointchange}). \n"
                    f"{challenger_clanname} new points:{challenger_stats[0]}(-{pointchange}).```"
                )
                for id in opponent_admin_ids:
                    user = await bot.fetch_user(id)
                    await user.send(
                        f"```{date.strftime('%x')} \n"
                        f"{opponent_clanname} has won the clanwar against {challenger_clanname} "
                        f"with scores {opponent_score}-{challenger_score}! \n"
                        f"{opponent_clanname} new points:{opponent_stats[0]}(+{pointchange}). \n"
                        f"{challenger_clanname} new points:{challenger_stats[0]}(-{pointchange}).```"
                    )
                return

        elif str(reaction.emoji) == "🚫":
            # an admin as already asnwered so do not listen
            if stop_listening_emoticons_event.is_set():
                return
            # so far no admin has answered, so stop listening now on
            stop_listening_emoticons_event.set()
            clanwar_status.remove(ctx.author.id)
            await ctx.respond("Enemy admins have disagreed with the clanwar scores!")
            for id in opponent_admin_ids:
                user = await bot.fetch_user(id)
                await user.send("Admins have disagreed with the clanwar score!")
            return

    # asyncio.gather to simultaneously message all of opponent clan admins, any of them can decide
    stop_event = asyncio.Event()
    tasks = [
        send_approval_message(
            admin_id,
            ctx,
            opponent_admin_ids,
            challenger_clanname,
            challenger_score,
            opponent_clanname,
            opponent_score,
            stop_event,
        )
        for admin_id in opponent_admin_ids
    ]
    await asyncio.gather(*tasks)


# reportclanwar ends
