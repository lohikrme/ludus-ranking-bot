# ludusbot.py
# updated 2nd october 2024

import settings
import random
import discord
import facts
import guides
from bot_instance import bot
from services import conn
from private_functions import _fetch_existing_clannames
from register_and_change_commands import cmd_registerplayer, cmd_registernewclan, cmd_registeradmin, cmd_changemynick, cmd_changemyclan
from leaderboard_commands import cmd_myscore, cmd_leaderboardplayers, cmd_leaderboardclans
from report_commands import cmd_reportclanwar, cmd_reportft7
from print_commands import cmd_printclanwars, cmd_printmyft7, cmd_printadmins


# keep these guilds real time, but store permanently in database
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

@bot.event
async def on_guild_join(guild):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO guilds (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING", (str(guild.id), str(guild.name),))
    current_guild_ids.append(guild.id)
    await bot.sync_commands(guild_ids=current_guild_ids)

@bot.event
async def on_guild_remove(guild):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM guilds WHERE id = %s", (str(guild.id),))
    current_guild_ids.remove(guild.id)
    await bot.sync_commands(guild_ids=current_guild_ids)

# BOT ENTERS THE CHANNEL
@bot.event
async def on_connect():
    current_guild_ids = await fetch_all_guild_ids()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.sync_commands(guild_ids=current_guild_ids)
    print("Slash commands have been cleared and updated... Wait a bit more before bot is ready...")
    print("Bot is finally ready to function!")



# --------------------------------------------------
# --------- GUIDE AND FACTUAL COMMANDS -------------

# GUIDE IN ENGLISH
@bot.slash_command(name="guide", description="Teaches commands of ludus-ranking-bot with English!")
async def guide(ctx):
    await ctx.respond(guides.guide_eng, ephemeral=True)
# guide in english ends

# GUIDE IN RUSSIAN
@bot.slash_command(name="гид", description="Обучает команды ludus-ranking-bot на русском языке!")
async def гид(ctx):
    await ctx.respond(guides.guide_rus, ephemeral=True)
# guide in russian ends

# GUIDE IN TURKISH
@bot.slash_command(name="rehber", description="ludus-ranking-bot komutlarını İngilizce ile öğretir!")
async def rehber(ctx):
    await ctx.respond(guides.guide_tr, ephemeral=True)
# guide in turkish ends

# FACTUAL ENG COMMAND
@bot.slash_command(name="factual", description="Bot will tell interesting facts!")
async def factual(ctx):
    answer = random.choice(facts.facts_eng)
    await ctx.respond(answer)  
# factual eng ends

# FACTUAL RUS COMMAND
@bot.slash_command(name="факт", description="Бот расскажет интересные факты!")
async def факт(ctx):
    answer = random.choice(facts.facts_rus)
    await ctx.respond(answer)  
# factual rus ends

# FACTUAL TR COMMAND
@bot.slash_command(name="gerçekler", description="Bot ilginç gerçekleri anlatacak")
async def gerçekler(ctx):
    answer = random.choice(facts.facts_tr)
    await ctx.respond(answer)  
# factual tr ends



# -------------------------------------------------------
# ---------- REGISTER AND CHANGE COMMANDS ---------------

# REGISTER PLAYER COMMAND
@bot.slash_command(name="registerplayer", description="Register yourself as a player!")
async def registerplayer(ctx, nickname: str):
    await cmd_registerplayer(ctx, nickname)
# register player ends


# REGISTER CLAN COMMAND
@bot.slash_command(name="registernewclan", description="Register a new clan if you cannot find yours in /printclans.")
async def registernewclan(ctx, clanname: str):
    await cmd_registernewclan(ctx, clanname)
# registerclan ends


# REGISTER ADMIN COMMAND
@bot.slash_command(name="registeradmin", description="Register as admin to be able to report/approve clanwars and announce events!")
async def registeradmin(ctx, password:str):
    await cmd_registeradmin(ctx, password)
# register admin ends


# CHANGEYOURNICKNAME COMMAND
@bot.slash_command(name="changemynick", description="Give yourself a new nickname!")
async def changemynick(ctx, nickname: str):
    await cmd_changemynick(ctx, nickname)
# change your nickname ends


# CHANGE YOUR CLAN COMMAND
@bot.slash_command(name="changemyclan", description="Give yourself a new clanname!")
async def changemyclan(ctx, new_clanname: str):
    await cmd_changemyclan(ctx, new_clanname)
# change your clan ends



# -------------------------------------------------------
# ---------- LEADERBOARD COMMANDS -----------------------

# MYSCORE COMMAND
@bot.slash_command(name="myscore", description="Print your personal scores!")
async def myscore(ctx):
    await cmd_myscore(ctx)
# myscore ends


# LEADERBOARD PLAYERS
@bot.slash_command(name="leaderboardplayers", description="Print top players of a specific clan (or all clans)!")
@discord.option("number", int, description="number of players to print")
@discord.option("clanname", str, description="'Please leave the clanname empty if you want to print players of all clans!", default=None)
async def leaderboardplayers(ctx, number: int, clanname: str):
    await cmd_leaderboardplayers(ctx, number, clanname)
# leaderboard players ends


# LEADERBOARD CLANS COMMAND
# for example, user gives '/clanleaderboard 10' and bot gives scores of top10 clans
@bot.slash_command(name="leaderboardclans", description="Print top clans in order!")
@discord.option("number", int, description="number of clans to print")
async def leaderboardclans(ctx, number: int):
    await cmd_leaderboardclans(ctx, number)
# leaderboard clans ends
    


# -------------------------------------------------------
# -------------- REPORT COMMANDS -----------------------

# REPORT CLANWAR COMMAND
@bot.slash_command(name="reportclanwar", description="Save clanwar scores permanently and gain rank for your clan!")
async def reportclanwar(ctx, year: int, month: int, day: int, reporter_clanname: str, reporter_score: int, opponent_clanname: str, opponent_score: int):
    await cmd_reportclanwar(ctx, year, month, day, reporter_clanname, reporter_score, opponent_clanname, opponent_score)
# reportclanwar ends


# REPORTFT7 COMMAND
@bot.slash_command(name="reportft7", description="Discreetly via private chat save duel ft7 scores permanently and gain personal ranking points!")
async def reportft7(ctx, opponent: discord.Member, my_score: int, opponent_score: int):
    await cmd_reportft7(ctx, opponent, my_score, opponent_score)
# report ft7 ends



# -------------------------------------------------------
# ---------------- PRINT COMMANDS -----------------------

# PRINTCLANWARS COMMAND
@bot.slash_command(name="printclanwars", description="Print clanwar scores of a selected clanname")
@discord.option("number", int, description="number of clanwars to print")
async def printclanwars(ctx, clanname: str, number: int):
    await cmd_printclanwars(ctx, clanname, number)
# print clan wars ends


# PRINTCLANNAMES COMMAND
@bot.slash_command(name="printclans", description="Print all existing clannames")
async def printclans(ctx):
    existing_clans = await _fetch_existing_clannames()
    await ctx.respond(f"Currently existing clans are next: \n{existing_clans} \n If you miss a clan, please use '/registerclan'!")
# print clannames ends


# PRINTMYDUELS
@bot.slash_command(name="printmyft7", description="Print your latest duels against a specific opponent or every opponent")
@discord.option("number", int, description="number of ft7 to print")
@discord.option("opponent", discord.Member, description="'Please leave the opponent empty if you want to print against all players", default=None)
async def printmyft7(ctx, number: int, opponent: discord.Member):
    await cmd_printmyft7(ctx, number, opponent)
# print my duels ends


# PRINTADMINS COMMAND
@bot.slash_command(name="printadmins", description="Print all admins who have registered with '/registeradmin'!")
async def printadmins(ctx):
    await cmd_printadmins(ctx)
# print admins ends



# -------------------------------------------------------
# ---------------- OTHER COMMANDS -----------------------

# EVENTANNOUNCE COMMAND
@bot.slash_command(name="eventannounce", description="Messages privately clan members about an approaching event!")
async def eventannounce(ctx, role: discord.Role, title: str, date: str, where: str, password: str):
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    existing_leader = cursor.fetchone()
    if existing_leader is None:
        await ctx.respond("```Only admins registered with '/registeradmin' can announce events!```", ephemeral=True)
        return
    await ctx.respond(f".")

    # basis for messages
    channel_message = f"on {date.lower()}! \nat {where.lower()} \n password: {password}  \n \n{role.mention} click ⚔️ to join"
    private_message = f"on {date}! \nPlease click ⚔️ in {ctx.guild.name} '{ctx.channel.name}' channel if you want to join!"
    
    # use embed message, otherwise cannot use bot emoticons on it to get "votes" how many will join
    channel_message_embed = discord.Embed(title=title.upper(),
    description=channel_message)
    private_message_embed = discord.Embed(title=title.upper(), description = private_message)


    interactive_channel_message = await ctx.send(embed=channel_message_embed)
    await interactive_channel_message.add_reaction("⚔️")

    # direct message all players with normal string and encourage to add a sword emoticon
    for member in ctx.guild.members:
        if member is None:
            continue
        if role in member.roles and not member.bot:
            try:
                await member.send(embed=private_message_embed)
                print(f'Message sent to {member.name}')
            except discord.Forbidden:
                print(f'Cannot send message to {member.name}')
            except discord.HTTPException as e:
                print(f'Failed to send message to {member.name}: {e}')
    print(f"All members of {ctx.guild.name} have been messaged about the coming event of {title}!")
    return
# event announce ends


# TOKEN OF BOT TO IDENTIFY AND USE IN CHANNELS
token = settings.bot_token
bot.run(token)
