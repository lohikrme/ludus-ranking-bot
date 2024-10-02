# fetch_existing_clannames.py
# updated 2nd october 2024

from services import conn

# FETCH EXISTING CLANNAMES
async def _fetch_existing_clannames():
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM clans", ())
    clannames = cursor.fetchall()
    current_clans = []
    for item in clannames:
        current_clans.append(item[0])
    return current_clans
# fetch existing clannames ends