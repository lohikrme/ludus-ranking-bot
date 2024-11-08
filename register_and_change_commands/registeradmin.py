# registeradmin.py
# updated 4th october 2024

import settings
from services import conn
from private_functions import _is_registered


async def cmd_registeradmin(ctx, password: str):
    cursor = conn.cursor()

    # check if admin is a registered player
    registered = await _is_registered(str(ctx.author.id))
    if not registered:
        await ctx.respond("Please use '/registerplayer' first to register as a player!", ephemeral=True)
        return

    # check if admin has already been registered
    cursor.execute("SELECT * FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    alreadyin = cursor.fetchone()
    if alreadyin is not None:
        await ctx.respond("You are already an admin!", ephemeral=True)
        return

    # check author belongs to a clan
    # cursor.execute("SELECT clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    # author_clan_id = cursor.fetchone()[0]
    # if author_clan_id == 1:
    #    await ctx.respond(
    #        "You must join a clan before becoming an admin. "
    #        "Admins represent their clans. Please use '/changemyclan'.",
    #        ephemeral=True,
    #    )
    #    return

    # check password is correct
    if password != settings.leaderpassword:
        await ctx.respond(
            f"You have given a wrong password. \nAsk Legion clan if you want to become an admin.",
            ephemeral=True,
        )
        return

    # all ok, add the new admin
    cursor.execute("INSERT INTO admins (discord_id) VALUES (%s)", (str(ctx.author.id),))
    await ctx.respond("Congratulations, your admin registration has been accepted!")
    return


# register admin ends
