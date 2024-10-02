# registerplayer.py
# updated 2nd october 2024

from services import conn
from private_functions import _is_registered

async def cmd_registerplayer(ctx, nickname: str):
    # FETCH USER'S OFFICIAL DISCORD NAME
    username = str(ctx.author.name)
    # NOTIFY USER THEY ARE ALREADY REGISTERED
    is_registered_result = await _is_registered(str(ctx.author.id))
    if is_registered_result:
        await ctx.respond("You have already been registered! \nIf you want to reset your rank, please contact admins.", ephemeral=True)
    # ADD A NEW USER
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players", ())
        amount_of_lines = cursor.fetchone()[0]
        if (amount_of_lines < 10000):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, nickname, discord_id) VALUES (%s, %s, %s)", (username, nickname, str(ctx.author.id),))
            await ctx.respond(f"Your discord account has successfully been registered with nickname '{nickname}'! Nickname can be changed easily.")
        else:
            await ctx.respond("The database is full. Please contact admins.")
# register player ends