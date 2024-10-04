# printadmins.py
# updated 4th october 2024

from services import conn


async def cmd_printadmins(ctx):
    all_admins = []
    all_admins.append("```All currently registered admins:```")
    calculator = 0
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id FROM admins", ())
    admin_ids = cursor.fetchall()
    admin_ids = [id[0] for id in admin_ids]
    if len(admin_ids) > 0:
        for id in admin_ids:
            calculator += 1
            cursor.execute(
                """
                SELECT players.nickname, players.username, clans.name 
                FROM players 
                LEFT JOIN clans ON players.clan_id = clans.id
                WHERE discord_id = %s
                """,
                (id,),
            )
            admin_info = cursor.fetchone()
            all_admins.append(
                f"```NUMBER {calculator}: \n"
                f"nickname: {admin_info[0]} \n"
                f"discord_username: {admin_info[1]} \n"
                f"clanname: {admin_info[2]}```"
            )
        await ctx.respond("".join(all_admins), ephemeral=True)
    else:
        await ctx.respond(f"There are no currently registered admins!", ephemeral=True)


# cmd_printadmins ends
