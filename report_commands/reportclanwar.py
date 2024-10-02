# reportclanwar.py
# updated 2nd october 2024

import datetime
from services import conn
from private_functions import _fetch_existing_clannames, _update_clan_points
import discord
from bot_instance import bot
import asyncio


clanwar_status = []

async def cmd_reportclanwar(ctx, year: int, month: int, day: int, reporter_clanname: str, reporter_score: int, opponent_clanname: str, opponent_score: int):
    global clanwar_status
    all_admin_ids = []
    all_opponent_clanmember_ids = []
    opponent_admin_ids = []
    
    reporter_clanname = reporter_clanname.lower()
    opponent_clanname = opponent_clanname.lower()
    # store here date for storing into database
    date = datetime.datetime(1900, 1, 1)
    

    ### step1: validate that ctx.author is a registered admin and is not in clanwar already
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    existing_leader = cursor.fetchone()
    if existing_leader is None:
        await ctx.respond("```Only admins registered with '/registeradmin' can report clanwar scores!```", ephemeral=True)
        return
    
    if (ctx.author.id in clanwar_status):
        await ctx.respond(f"You {ctx.author.mention} are already in clanwar with some clan.", ephemeral=True)
        return
    
    ### step2: validate date
    date_is_valid = True
    try:
        date = datetime.datetime(year, month, day)
    except ValueError:
        date_is_valid = False
    if date_is_valid == False:
        await ctx.respond("```The date you gave is not a real date. Please make sure year, month and day are correct!```", ephemeral=True)
        return

    ### step3: validate challenger and defender clannames and scores
    existing_clans = await _fetch_existing_clannames()
    
    if reporter_clanname not in existing_clans:
        await ctx.respond(f"```The reporter_clanname {reporter_clanname} wasn't part of: \n{existing_clans}. \nIf your clan's name is missing, please use '/registerclan'```", ephemeral=True)
        return
    if opponent_clanname not in existing_clans:
        await ctx.respond(f"```The reporter_clanname {reporter_clanname} wasn't part of: \n{existing_clans}. \nIf your clan's name is missing, please use '/registerclan'```", ephemeral=True)
        return
    if reporter_score == opponent_score:
        await ctx.respond(f"```{reporter_score} equals {opponent_score}. \nScores may not be equal!```", ephemeral=True)
        return
    
    ### step 4: check that reporter_clanname is same as author's clanname
    cursor.execute("""SELECT clans.name 
                   FROM clans
                   LEFT JOIN players ON players.clan_id = clans.id
                   WHERE players.discord_id = %s""", (str(ctx.author.id),))
    authorclanname = cursor.fetchone()[0]
    if authorclanname != reporter_clanname:
        await ctx.respond(f"Reporter_clanname did not match to author's clan. \n{ctx.author.mention} belongs to clan '{authorclanname}', \nwhile reporter_clanname was '{reporter_clanname}'", ephemeral=True)
        return
    
    ### step 5: check that opponent_clanname has a registered admin, and store id for later use
    # first fetch opponent clan id
    cursor.execute("SELECT clans.id FROM clans WHERE clans.name = %s", (opponent_clanname,))
    opponent_clan_id = cursor.fetchone()[0]

    # second fetch all admin ids
    cursor.execute("SELECT discord_id FROM admins")
    all_admins = cursor.fetchall()
    for admin in all_admins:
        all_admin_ids.append(admin[0])

    # third fetch all opponent clan member ids
    cursor.execute("SELECT players.discord_id FROM players WHERE players.clan_id = %s", (opponent_clan_id,))
    opponent_players = cursor.fetchall()
    for player in opponent_players:
        all_opponent_clanmember_ids.append(player[0])

    for admin_id in all_admin_ids:
        if admin_id in all_opponent_clanmember_ids:
            opponent_admin_ids.append(admin_id)

    if len(opponent_admin_ids) < 1:
        await ctx.respond ("Opponent clan does not have a registered admin! They need one to confirm the clanwar results.", ephemeral=True)
        return


    ### step 6: send approval message to all opponent admins, or cancel after 24h wait time automatically
    clanwar_status.append(ctx.author.id)

    await ctx.respond(embed=discord.Embed(title="", description=f"Waiting for opponent clan's admins to confirm: \n{reporter_clanname} vs {opponent_clanname} \n{reporter_score}-{opponent_score}"))

    async def send_approval_message(admin_id, ctx, opponent_admin_ids, reporter_clanname, reporter_score, opponent_clanname, opponent_score, stop_listening_emoticons_event):
        opponent_admin = await bot.fetch_user(admin_id)
        approval_embed = discord.Embed(
            title=f"Confirm clanwar results:",
            description=f"{reporter_clanname} vs {opponent_clanname} \n{reporter_score}-{opponent_score}\n click ✅approve   🚫disagree."
        )
        approval_msg = await opponent_admin.send(embed=approval_embed)
        await approval_msg.add_reaction("✅")
        await approval_msg.add_reaction("🚫")

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=3600.0, check=lambda reaction, user: user == opponent_admin and str(reaction.emoji) in ["✅", "🚫"] and reaction.message.id == approval_msg.id)
        except asyncio.TimeoutError:
            await opponent_admin.send(f"Clanwar reporting expired!")
            return
        except asyncio.CancelledError:
            return

        # HANDLE REACTIONS
        if str(reaction.emoji) == "✅":
            if (stop_listening_emoticons_event.is_set()):
                return
            stop_listening_emoticons_event.set()
            clanwar_status.remove(ctx.author.id)
            ### step7: if all previous is ok, store given data into clanwars datatable
            cursor.execute("SELECT id from clans WHERE name = %s", (reporter_clanname,))
            challenger_clan_id = cursor.fetchone()[0]
            cursor.execute("SELECT id from clans WHERE name = %s", (opponent_clanname,))
            defender_clan_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO clanwars (date, challenger_clan_id, defender_clan_id, challenger_won_rounds, defender_won_rounds) VALUES (%s, %s, %s, %s, %s)", (date, challenger_clan_id, defender_clan_id, reporter_score, opponent_score,))

            ### step8: solve first which clan won and then update points with update_clan_points()
            challenger_won = False
            if (reporter_score > opponent_score):
                challenger_won = True
                await _update_clan_points(challenger_clan_id, defender_clan_id, challenger_won)
            else:
                challenger_won = False
                await _update_clan_points(challenger_clan_id, defender_clan_id, challenger_won)

            ### step9: notify author's channel and opponent admins of new clanwar scores and rankings
            cursor.execute("SELECT points, old_points FROM clans WHERE id = %s", (challenger_clan_id,))
            challenger_stats = cursor.fetchone()
            cursor.execute("SELECT points, old_points FROM clans WHERE id = %s", (defender_clan_id,))
            defender_stats = cursor.fetchone()

            if challenger_won:
                pointchange = challenger_stats[0] - challenger_stats[1]
                await ctx.respond(f"```{date.strftime('%x')} \n{reporter_clanname} has won the clanwar against {opponent_clanname} with scores {reporter_score}-{opponent_score}! \n{reporter_clanname} new points:{challenger_stats[0]}(+{pointchange}). \n{opponent_clanname} new points:{defender_stats[0]}(-{pointchange}).```")
                for id in opponent_admin_ids:
                    user = await bot.fetch_user(id)
                    await user.send(f"```{date.strftime('%x')} \n{reporter_clanname} has won the clanwar against {opponent_clanname} with scores {reporter_score}-{opponent_score}! \n{reporter_clanname} new points:{challenger_stats[0]}(+{pointchange}). \n{opponent_clanname} new points:{defender_stats[0]}(-{pointchange}).```")
                return
            else:
                pointchange = challenger_stats[1] - challenger_stats[0] 
                await ctx.respond(f"```{date.strftime('%x')} \n{opponent_clanname} has won the clanwar against {reporter_clanname} with scores {opponent_score}-{reporter_score}! \n{opponent_clanname} new points:{defender_stats[0]}(+{pointchange}). \n{reporter_clanname} new points:{challenger_stats[0]}(-{pointchange}).```")
                for id in opponent_admin_ids:
                    user = await bot.fetch_user(id)
                    await user.send(f"```{date.strftime('%x')} \n{opponent_clanname} has won the clanwar against {reporter_clanname} with scores {opponent_score}-{reporter_score}! \n{opponent_clanname} new points:{defender_stats[0]}(+{pointchange}). \n{reporter_clanname} new points:{challenger_stats[0]}(-{pointchange}).```")
                return

        elif str(reaction.emoji) == "🚫":
            if (stop_listening_emoticons_event.is_set()):
                return
            stop_listening_emoticons_event.set()
            clanwar_status.remove(ctx.author.id)
            await ctx.respond("Enemy admins have disagreed with the clanwar scores!")
            for id in opponent_admin_ids:
                user = await bot.fetch_user(id)
                await user.send("Admins have disagreed with the clanwar score!")
            return

    # because there can be multiple opponent clan leaders, we must use asyncio.gather to simultaneously message all of them
    stop_event = asyncio.Event()
    tasks = [send_approval_message(admin_id, ctx, opponent_admin_ids, reporter_clanname, reporter_score, opponent_clanname, opponent_score, stop_event) for admin_id in opponent_admin_ids]
    await asyncio.gather(*tasks)
# reportclanwar ends