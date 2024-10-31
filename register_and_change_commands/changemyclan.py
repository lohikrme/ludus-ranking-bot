# changemyclan.py
# updated 4th october 2024

from private_functions import _is_registered, _fetch_existing_clannames
from services import conn


async def cmd_changemyclan(ctx, new_clanname: str):

    # check if user has registered
    is_registered_result = await _is_registered(str(ctx.author.id))
    if not is_registered_result:
        await ctx.respond(f"Register before using this command or contact admins.", ephemeral=True)
        return

    # check that selected new clanname is registered as clan
    existing_clans = await _fetch_existing_clannames()
    if new_clanname not in existing_clans:
        await ctx.respond(
            f"'{new_clanname}' is not part of existing clans: \n{existing_clans} \n"
            f"Please use '/registerclan' to create a new clanname.",
            ephemeral=True,
        )
        return

    # fetch old clanname and compare it is not same as new clanname
    cursor = conn.cursor()
    cursor.execute("SELECT clan_id FROM players WHERE discord_id = %s", (str(ctx.author.id),))
    old_clan_id = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM clans WHERE id = %s", (old_clan_id,))
    old_clanname = cursor.fetchone()[0]
    if new_clanname == old_clanname:
        await ctx.respond(f"You already belong to the clan '{new_clanname}'", ephemeral=True)
        return

    # change the clanname of the user
    else:
        cursor.execute("SELECT id FROM clans WHERE name = %s", (new_clanname,))
        new_clan_id = cursor.fetchone()[0]
        cursor.execute(
            "UPDATE players SET clan_id = (%s) WHERE players.discord_id = %s",
            (
                new_clan_id,
                str(ctx.author.id),
            ),
        )
        await ctx.respond(
            f"Your clanname has been updated! \n"
            f"Old clanname: '{old_clanname}'. \n"
            f"New clanname: '{new_clanname}'",
            ephemeral=True,
        )
        return


# change your clan ends
