# registernewclan.py
# updated 2nd october 2024

from services import conn
import re

async def cmd_registernewclan(ctx, clanname: str):
    allowed_characters = re.compile(r'^[\w\-\_\[\]\(\)\^]+$')

    if not allowed_characters.match(clanname):
        await ctx.respond("Clan name contains invalid characters. Only a-z, 0-9, _, -, [, ], (, ) and ^ are allowed!", ephemeral=True)
        return

    clanname = clanname.lower()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clans WHERE name = %s", (clanname,))
    existing_clan = cursor.fetchone()

    if existing_clan is not None:
        await ctx.respond(f"The clanname {clanname} already exists", ephemeral=True)
        return
    
    cursor.execute("INSERT INTO clans (name) VALUES (%s)", (clanname,))
    await ctx.respond(f"The clanname '{clanname}' has successfully been registered!")
    return
# registerclan ends