from services import conn


async def _fetch_nickname(discord_id: str):
    cursor = conn.cursor()
    cursor.execute(
        """SELECT nickname
                FROM players
                WHERE discord_id = %s
        """,
        (discord_id,),
    )
    return cursor.fetchone()[0]
