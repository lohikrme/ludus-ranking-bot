# is_registered.py
# updated 2nd october 2024

from services import conn

# USE THIS TO CHECK IF USER REGISTERED
async def _is_registered(discord_id: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE discord_id = %s", (discord_id,))
    existing_user = cursor.fetchone()

    if existing_user is not None: # user is registered
        return True
    
    return False # user is not registered
# is registered ends