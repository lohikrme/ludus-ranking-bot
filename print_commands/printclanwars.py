# printclanwars.py
# 2nd october 2024

from services import conn
from private_functions import _fetch_existing_clannames

async def cmd_printclanwars(ctx, clanname: str, number: int):
    clanname = clanname.lower()
    existing_clans = await _fetch_existing_clannames()
    if clanname not in existing_clans:
        await ctx.respond(f"```{clanname} is not part of existing clans: \n{existing_clans} \nYou may use '/registerclan' to create a new clan.```", ephemeral=True)
        return
    
    # first fetch the id of given clan, so it will be easier to find all clanwars containing that id in challenger or defender
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clans WHERE name = %s", (clanname,))
    wanted_clan_id = cursor.fetchone()[0]
    cursor.execute(""" SELECT clanwars.date, challenger_clan.name AS challenger_name, clanwars.challenger_won_rounds, defender_clan.name AS defender_name, clanwars.defender_won_rounds
                    FROM clanwars
                    LEFT JOIN clans AS challenger_clan ON clanwars.challenger_clan_id = challenger_clan.id
                    LEFT JOIN clans AS defender_clan ON clanwars.defender_clan_id = defender_clan.id
                    WHERE challenger_clan.id = %s OR defender_clan.id = %s
                    ORDER BY clanwars.date DESC, clanwars.id DESC""", (wanted_clan_id, wanted_clan_id,))
    clanwars = cursor.fetchmany(number)
    # print clanwar history
    if (len(clanwars) >= 1):
        scores = []
        scores.append(f"```** {number} CLANWARS OF {clanname.upper()}: **```")
        printable_text = ""
        # war[0] = date, war[1] = challenger name, war[2] = challenger points, war[3] = defender name, war[4] = defender points
        for war in clanwars: 
            printable_text = (f"```date: {war[0]} \n{war[1]} vs {war[3]} [{war[2]}-{war[4]}]```")
            scores.append(printable_text)

        scores.append(f"```** {number} MOST RECENT CLANWARS OF {clanname.upper()} HAVE BEEN PRINTED! **```")
        await ctx.respond("".join(scores))
        return
    else:
        await ctx.respond(f"```Currently there are no reported clanwars by {clanname}! Please use '/reportclanwar'.```")
        return
# print clan wars ends