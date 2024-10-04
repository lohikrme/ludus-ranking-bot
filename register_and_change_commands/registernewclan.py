# registernewclan.py
# updated 4th october 2024

from services import conn
import re


async def cmd_registernewclan(ctx, clanname: str):
    cursor = conn.cursor()
    allowed_characters = re.compile(r"^[\w\-\_\[\]\(\)\^]+$")
    clanname = clanname.lower()

    # check clanname contains only allowed characters
    if not allowed_characters.match(clanname):
        await ctx.respond(
            "Clan name contains invalid characters. "
            "Only a-z, 0-9, _, -, [, ], (, ) and ^ are allowed!",
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
    return


# registerclan ends
