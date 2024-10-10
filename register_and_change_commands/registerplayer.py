# registerplayer.py
# updated 10th october 2024

from services import conn
from private_functions import _is_registered


async def cmd_registerplayer(ctx, nickname: str):
    cursor = conn.cursor()

    # check user is not already registered
    is_registered_result = await _is_registered(str(ctx.author.id))
    if is_registered_result:
        await ctx.respond(
            "You have already been registered! \n"
            "If you want to reset your rank, please contact admins.",
            ephemeral=True,
        )

    # check database is not full
    cursor.execute("SELECT COUNT(*) FROM players", ())
    amount_of_lines = cursor.fetchone()[0]
    if amount_of_lines >= 10000:
        await ctx.respond("The database is full. Please contact admins.")
        return

    # add a new user
    else:
        username = str(ctx.author.name)
        cursor.execute(
            "INSERT INTO players (username, nickname, discord_id) VALUES (%s, %s, %s)",
            (
                username,
                nickname,
                str(ctx.author.id),
            ),
        )
        await ctx.respond(
            f"Your discord account has successfully been registered with nickname '{nickname}'. "
            f"Nickname can be changed easily."
        )


# register player ends
