# is_registered.py
# updated 4th october 2024

from services import conn


# CHECK IF USER IS REGISTERED
async def _is_registered(discord_id: str):
    # checks if the discord_id is found from registered players
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE discord_id = %s", (discord_id,))
    existing_user = cursor.fetchone()

    # user is registered
    if existing_user is not None:
        return True
    # user is not registered
    else:
        return False


# _is_registered ends
