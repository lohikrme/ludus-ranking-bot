
# changemynick.py
# updated 2nd october 2024

from private_functions import _is_registered
from services import conn

async def cmd_changemynick(ctx, nickname: str):
    # IF USERNAME EXISTS IN DATABASE, CHANGE THEIR NICKNAME
    is_registered_result = await _is_registered(str(ctx.author.id))
    if is_registered_result:
        cursor = conn.cursor()
        cursor.execute("SELECT nickname FROM players WHERE discord_id = %s", (str(ctx.author.id),))
        old_nickname = cursor.fetchone()[0]
        cursor.execute("UPDATE players SET nickname = %s WHERE discord_id = %s", (nickname, str(ctx.author.id)))
        await ctx.respond(f"Your nickname has been updated! \nOld nickname: '{old_nickname}'. \nNew nickname: '{nickname}'", ephemeral=True)
        return
    else:
        await ctx.respond(f"Please register before changing your nickname.", ephemeral=True)
        return
# change your nickname ends