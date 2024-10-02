# update_duels_history.py
# updated 2nd october 2024

import datetime
from services import conn

# USE THIS TO UPDATE DUELS DATATABLE HISTORY
async def _update_duels_history(challenger_discord_id: str, opponent_discord_id: str, challenger_score: int, opponent_score: int):
    date = datetime.datetime.now()
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO duels (date, challenger_discord_id, opponent_discord_id, challenger_score, opponent_score) VALUES (%s, %s, %s, %s, %s)", (date, challenger_discord_id, opponent_discord_id, challenger_score, opponent_score,))
# update duels history ends  