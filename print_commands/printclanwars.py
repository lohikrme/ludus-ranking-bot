# printclanwars.py
# 4th october 2024

from services import conn
from private_functions import _fetch_existing_clannames


async def cmd_printclanwars(ctx, clanname: str, number: int):

    # make sure given clan exists
    existing_clans = await _fetch_existing_clannames()
    if clanname not in existing_clans:
        await ctx.respond(
            f"```{clanname} is not part of existing clans: \n{existing_clans} \n"
            f"You may use '/registerclan' to create a new clan.```",
            ephemeral=True,
        )
        return

    # fetches the id of given clan
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clans WHERE name = %s", (clanname,))
    wanted_clan_id = cursor.fetchone()[0]
    cursor.execute(
        """ 
        SELECT 
            clanwars.date, 
            challenger_clan.name AS challenger_name, 
            clanwars.challenger_score, 
            opponent_clan.name AS opponent_name, 
            clanwars.opponent_score
        FROM clanwars
        LEFT JOIN clans AS challenger_clan ON clanwars.challenger_clan_id = challenger_clan.id
        LEFT JOIN clans AS opponent_clan ON clanwars.opponent_clan_id = opponent_clan.id
        WHERE challenger_clan.id = %s OR opponent_clan.id = %s
        ORDER BY clanwars.date DESC, clanwars.id DESC""",
        (
            wanted_clan_id,
            wanted_clan_id,
        ),
    )

    # print clanwar history
    clanwars = cursor.fetchmany(number)

    if len(clanwars) >= 1:
        scores = []
        scores.append(f"```** {number} CLANWARS OF {clanname.upper()}: **```")
        printable_text = ""
        # war 0 = date, 1 = challenger name, 2 = chall points, 3 = def name, 4 = def points
        for war in clanwars:
            printable_text = f"```date: {war[0]} \n{war[1]} vs {war[3]} [{war[2]}-{war[4]}]```"
            scores.append(printable_text)

        scores.append(
            f"```** {number} MOST RECENT CLANWARS OF {clanname.upper()}" f" HAVE BEEN PRINTED! **```"
        )
        await ctx.respond("".join(scores))
        return
    else:
        await ctx.respond(
            f"```Currently there are no reported clanwars by {clanname}!"
            f" Please use '/reportclanwar'.```"
        )
        return


# cmd_printclanwars ends
