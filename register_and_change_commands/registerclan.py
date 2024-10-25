# registernewclan.py
# updated 24th october 2024

from services import conn
import re
from private_functions import _fetch_existing_admins
import discord
from settings import host_discord_id
from bot_instance import bot


async def cmd_registerclan(ctx, clanname: str):
    cursor = conn.cursor()
    allowed_characters = re.compile(r"^[\w\-\_\[\]\(\)\^]+$")

    # check if author is a registered admin
    current_admins = await _fetch_existing_admins()

    cursor.execute("SELECT discord_id FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    author_is_admin = cursor.fetchone()
    if author_is_admin is None:
        await ctx.respond(
            "```Only admins registered with '/registeradmin' can register a new clanname!```"
            f"```Currently registered admins are: \n{current_admins}",
            ephemeral=True,
        )
        return

    # check clanname contains only allowed characters
    if not allowed_characters.match(clanname):
        await ctx.respond(
            "Clan name contains invalid characters. "
            "Only A-Z a-z, 0-9, _, -, [, ], (, ) and ^ are allowed!",
            ephemeral=True,
        )
        return

    # check clan does not already exist
    cursor.execute("SELECT * FROM clans WHERE name = %s", (clanname,))
    existing_clan = cursor.fetchone()

    if existing_clan is not None:
        await ctx.respond(f"The clanname {clanname} already exists", ephemeral=True)
        return

    # add a new clan
    cursor.execute("INSERT INTO clans (name) VALUES (%s)", (clanname,))
    await ctx.respond(f"The clanname '{clanname}' has successfully been registered!")

    # message Host about the new clan, so they can update the clannames.py file
    clan_register_embed = discord.Embed(
        title=f"A new clan {clanname}!",
        description=f"{ctx.author.mention} has registered a new clan called '{clanname}'"
        "\nPlease update the clannames.py file and restart the bot.",
    )
    host = await bot.fetch_user(host_discord_id)
    await host.send(embed=clan_register_embed)
    return


# registerclan ends
