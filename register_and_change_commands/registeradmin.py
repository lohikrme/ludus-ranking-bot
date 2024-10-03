# registeradmin.py
# updated 2nd october 2024

import settings
from services import conn


async def cmd_registeradmin(ctx, password: str):
    if password != settings.leaderpassword:
        await ctx.respond(
            f"You have given a wrong password. \n"
            f"Ask Legion clan if you want to become an admin.",
            ephemeral=True,
        )
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE discord_id = %s", (str(ctx.author.id),))
    alreadyin = cursor.fetchone()
    if alreadyin is not None:
        await ctx.respond("You are already an admin!", ephemeral=True)
        return
    # check admin belongs to a clan
    cursor.execute("SELECT clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    author_clan_id = cursor.fetchone()[0]
    if author_clan_id == 1:
        await ctx.respond(
            "You must join a clan before becoming an admin. "
            "Admins represent their clans. Please use '/changemyclan'.",
            ephemeral=True,
        )
        return
    # all ok, add the new admin
    cursor.execute("INSERT INTO admins (discord_id) VALUES (%s)", (str(ctx.author.id),))
    await ctx.respond("Congratulations, your admin registration has been accepted!")
    return


# register admin ends
