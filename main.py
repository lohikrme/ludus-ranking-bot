# main.py
# updated 16th december 2024

import settings
import random
import discord
import facts
import guides
from bot_instance import bot
from services import conn
from private_functions import _fetch_existing_clannames
from register_and_change_commands import (
    cmd_registerplayer,
    cmd_registerclan,
    cmd_registeradmin,
    cmd_changemynick,
    cmd_changemyclan,
)
from leaderboard_commands import (
    cmd_myscore,
    cmd_leaderboardplayers,
    cmd_leaderboardclans,
)
from report_commands import cmd_reportclanwar, cmd_reportft7, cmd_challengeft7
from print_commands import cmd_printclanwars, cmd_printmyft7, cmd_printadmins
from clannames import clans, clans_with_none


# use this array to update guilds, but also store them permanently in database
current_guild_ids = []


# return integer array of guild ids from database
async def fetch_all_guild_ids():
    ids = []
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM guilds", ())
    all_guild_ids = cursor.fetchall()
    for id in all_guild_ids:
        ids.append(int(id[0]))
    return ids


# automaticly update guilds datatable if bot is added or removed from a server
@bot.event
async def on_guild_join(guild):
    cursor = conn.cursor()
    print("Bot has been added to the next server: ")
    print(f"guild-name: {guild.name} \nguild-id: {str(guild.id)}\n")
    cursor.execute("INSERT INTO guilds (id, name) VALUES (%s, %s)", (str(guild.id), guild.name))
    current_guild_ids = await fetch_all_guild_ids()
    await bot.sync_commands(guild_ids=current_guild_ids)


@bot.event
async def on_guild_remove(guild):
    cursor = conn.cursor()
    print("Bot has been removed from the next server: ")
    print(f"guild-name: {guild.name} \nguild-id: {str(guild.id)}\n")
    cursor.execute("DELETE FROM guilds WHERE id = (%s)", (str(guild.id),))
    current_guild_ids = await fetch_all_guild_ids()
    await bot.sync_commands(guild_ids=current_guild_ids)


# BOT ENTERS THE CHANNEL
@bot.event
async def on_connect():
    # fetch all guilds who adopted bot (Discord servers)
    current_guild_ids = await fetch_all_guild_ids()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    # update commands of bot to all guilds
    await bot.sync_commands(guild_ids=current_guild_ids)
    print("Slash commands have been cleared and updated...")
    print("Wait a bit more before bot is ready...")
    print("Print all clans: ", clans)
    print("Bot is finally ready to function!\n")


# --------------------------------------------------
# --------- GUIDE AND FACTUAL COMMANDS -------------


# GUIDE IN ENGLISH
@bot.slash_command(name="guide", description="Teaches commands of ludus-ranking-bot in English!")
async def guide(ctx):
    await ctx.respond(guides.guide_eng, ephemeral=True)


# GUIDE IN RUSSIAN
@bot.slash_command(name="гид", description="Обучает команды ludus-ranking-bot на русском языке!")
async def гид(ctx):
    await ctx.respond(guides.guide_rus, ephemeral=True)


# GUIDE IN TURKISH
@bot.slash_command(name="rehber", description="ludus-ranking-bot komutlarını İngilizce ile öğretir!")
async def rehber(ctx):
    await ctx.respond(guides.guide_tr, ephemeral=True)


# FACTUAL ENG COMMAND
@bot.slash_command(name="factual", description="Bot will tell interesting facts!")
async def factual(ctx):
    answer = random.choice(facts.facts_eng)
    await ctx.respond(answer)


# FACTUAL RUS COMMAND
@bot.slash_command(name="факт", description="Бот расскажет интересные факты!")
async def факт(ctx):
    answer = random.choice(facts.facts_rus)
    await ctx.respond(answer)


# FACTUAL TR COMMAND
@bot.slash_command(name="gerçekler", description="Bot ilginç gerçekleri anlatacak")
async def gerçekler(ctx):
    answer = random.choice(facts.facts_tr)
    await ctx.respond(answer)


# -------------------------------------------------------
# ---------- REGISTER AND CHANGE COMMANDS ---------------


# REGISTER PLAYER COMMAND
@bot.slash_command(name="registerplayer", description="Register yourself as a player!")
@discord.option("clanname", str, description="A specific clan.", choices=clans_with_none)
async def registerplayer(ctx, nickname: str, clanname: str):
    await cmd_registerplayer(ctx, nickname, clanname)


# REGISTER CLAN COMMAND
@bot.slash_command(
    name="registerclan",
    description="An admin can register a new clanname. Changes will take a few days.",
)
async def registerclan(ctx, clanname: str):
    await cmd_registerclan(ctx, clanname)


# REGISTER ADMIN COMMAND
@bot.slash_command(name="registeradmin", description="Register to be a admin!")
async def registeradmin(ctx, password: str):
    await cmd_registeradmin(ctx, password)


# CHANGEMYNICKNAME COMMAND
@bot.slash_command(name="changemynick", description="Give yourself a new nickname!")
async def changemynick(ctx, nickname: str):
    await cmd_changemynick(ctx, nickname)


# CHANGEMYCLAN COMMAND
@bot.slash_command(name="changemyclan", description="Give yourself a new clanname!")
@discord.option("new_clanname", str, description="List of currently existing clans", choices=clans)
async def changemyclan(ctx, new_clanname: str):
    await cmd_changemyclan(ctx, new_clanname)


# -------------------------------------------------------
# ---------- LEADERBOARD COMMANDS -----------------------


# MYSCORE COMMAND
@bot.slash_command(name="myscore", description="Print your personal scores!")
async def myscore(ctx):
    await cmd_myscore(ctx)


# LEADERBOARD PLAYERS
@bot.slash_command(name="leaderboardplayers", description="Print top players!")
@discord.option("number", int, description="Number of players.")
@discord.option("clanname", str, description="(Optional). A specific clan.", choices=clans, default=None)
async def leaderboardplayers(ctx, number: int, clanname: str):
    await cmd_leaderboardplayers(ctx, number, clanname)


# LEADERBOARD CLANS COMMAND
@bot.slash_command(name="leaderboardclans", description="Print top clans!")
async def leaderboardclans(ctx):
    await cmd_leaderboardclans(ctx)


# -------------------------------------------------------
# -------------- REPORT COMMANDS -----------------------


# REPORT CLANWAR COMMAND
@bot.slash_command(name="reportclanwar", description="Save clanwar scores permanently!")
@discord.option("reporter_clanname", str, description="Your own clan's name.", choices=clans)
@discord.option("reporter_clanscore", int, description="Your own clan's score.")
@discord.option("opponent_clanname", str, description="Your enemy's clan's name.", choices=clans)
@discord.option("opponent_clanscore", int, description="Your enemy's clan's score.")
async def reportclanwar(
    ctx,
    year: int,
    month: int,
    day: int,
    reporter_clanname: str,
    reporter_score: int,
    opponent_clanname: str,
    opponent_score: int,
):
    await cmd_reportclanwar(
        ctx,
        year,
        month,
        day,
        reporter_clanname,
        reporter_score,
        opponent_clanname,
        opponent_score,
    )


# REPORTFT7 COMMAND
@bot.slash_command(name="reportft7", description="Report ft7 duel scores via private chat!")
@discord.option("opponent", discord.Member, description="Select opponent from the list.")
async def reportft7(ctx, opponent: discord.Member, my_score: int, opponent_score: int):
    await cmd_reportft7(ctx, opponent, my_score, opponent_score)


# CHALLENGEFT7 COMMAND
@bot.slash_command(name="challengeft7", description="Challenge an opponent publicly to ft7!")
@discord.option("opponent", discord.Member, description="Select opponent from the list.")
async def challengeft7(ctx, opponent: discord.Member, my_score: int, opponent_score: int):
    await cmd_challengeft7(ctx, opponent, my_score, opponent_score)


# -------------------------------------------------------
# ---------------- PRINT COMMANDS -----------------------


# PRINTCLANWARS COMMAND
@bot.slash_command(name="printclanwars", description="Print clanwar history of a clan.")
@discord.option("clanname", str, description="A specific clan.", choices=clans)
@discord.option("number", int, description="Number of clanwars.")
async def printclanwars(ctx, clanname: str, number: int):
    await cmd_printclanwars(ctx, clanname, number)


# PRINTCLANNAMES COMMAND
@bot.slash_command(name="printclannames", description="Print all existing clannames")
async def printclannames(ctx):
    existing_clans = await _fetch_existing_clannames()
    clans = []
    calculator = 0
    clans.append(f"Currently existing clans are: \n")
    for clan in existing_clans:
        calculator += 1
        clans.append(f"{calculator}: {clan} \n")
    clans.append("If you miss a clan, please ask a registered admin \n")
    clans.append("to use '/registerclan'!")
    await ctx.respond("".join(clans))


# PRINTMYDUELS
@bot.slash_command(name="printmyft7", description="Print your latest ft7s.")
@discord.option("number", int, description="Number of ft7s to print.")
@discord.option("opponent", discord.Member, description="(Optional). Specific enemy.", default=None)
async def printmyft7(ctx, number: int, opponent: discord.Member):
    await cmd_printmyft7(ctx, number, opponent)


# PRINTADMINS COMMAND
@bot.slash_command(name="printadmins", description="Print all registered admins!")
async def printadmins(ctx):
    await cmd_printadmins(ctx)


# -------------------------------------------------------
# ---------------- OTHER COMMANDS -----------------------


# EVENTANNOUNCE COMMAND
@bot.slash_command(name="eventannounce", description="Message clan members of an event!")
@discord.option("role", discord.Role, description="@everyone or a specific role?")
@discord.option("title", str, description="A short description of the event!")
@discord.option("date", str, description="When will the event start?")
@discord.option("where", str, description="(Optional). Where event take place?", default="-")
@discord.option("password", str, description="(Optional). Event password?", default="-")
async def eventannounce(ctx, role: discord.Role, title: str, date: str, where: str, password: str):
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    existing_leader = cursor.fetchone()
    if existing_leader is None:
        await ctx.respond("```Only registered admins can announce events!```", ephemeral=True)
        return
    await ctx.respond(f".")

    # basis for messages
    channel_message = (
        f"on {date.lower()} \n"
        f"at {where.lower()} \n"
        f"password: {password}  \n \n"
        f"{role.mention} click ⚔️ to join!"
    )
    private_message = (
        f"on {date.lower()}! \nPlease click ⚔️ on "
        f"{ctx.guild.name} '{ctx.channel.name}' channel if you want to join!"
    )

    # use embed message, otherwise cannot use emoticons to get "votes"
    channel_message_embed = discord.Embed(title=title.upper(), description=channel_message)
    private_message_embed = discord.Embed(title=title.upper(), description=private_message)

    interactive_channel_message = await ctx.send(embed=channel_message_embed)
    await interactive_channel_message.add_reaction("⚔️")

    # sends a direct message to players which encourages to click the channel's sword emoticon
    for member in ctx.guild.members:
        if member is None:
            continue
        if role in member.roles and not member.bot:
            try:
                await member.send(embed=private_message_embed)
                print(f"Message sent to {member.name}")
            except discord.Forbidden:
                print(f"Cannot send message to {member.name}")
            except discord.HTTPException as e:
                print(f"Failed to send message to {member.name}: {e}")
    print(f"All members of {ctx.guild.name} have been messaged" f" about the coming event of {title}!")
    return


# TOKEN OF BOT TO IDENTIFY AND USE IN CHANNELS
token = settings.development_bot_token
bot.run(token)
