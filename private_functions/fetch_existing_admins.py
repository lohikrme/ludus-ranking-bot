# fetch_existing_admins.py
# updated 9th october 2024

from services import conn


async def _fetch_existing_admins():
    cursor = conn.cursor()
    answer = []
    cursor.execute(
        """SELECT players.username, clans.name
                FROM players
                JOIN admins ON admins.discord_id = players.discord_id
                JOIN clans ON clans.id = players.clan_id
        """,
        (),
    )
    admins = cursor.fetchall()
    for admin in admins:
        answer.append(f"{admin[0]} of {admin[1]}")
    return answer
