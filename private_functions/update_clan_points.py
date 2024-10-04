# update_clan_points.py
# updated 4th october 2024

from services import conn


# UPDATE CLAN POINTS IN DATABASE
async def _update_clan_points(challenger_clan_id: int, opponent_clan_id: int, challenger_win: bool):
    # initiate new points and db connection
    challenger_new_points = challenger_stats["current_points"]
    opponent_new_points = opponent_stats["current_points"]
    cursor = conn.cursor()

    ### standard_point_change is the change of ranking points if opponents have equal rank
    # point_level_divident determines, how much rank difference affects to point_change
    standard_point_change = 20
    point_level_divident = 60
    minimum_point_change = 2

    ### FETCH CURRENT STATS FROM DATABASE

    # challenger stats
    cursor.execute(
        "SELECT battles, wins, average_enemy_rank, points FROM clans WHERE id = %s",
        (challenger_clan_id,),
    )
    result = cursor.fetchone()
    challenger_stats = {
        "battles": result[0],
        "wins": result[1],
        "average_enemy_rank": result[2],
        "current_points": result[3],
    }

    # opponent stats
    cursor.execute(
        "SELECT battles, wins, average_enemy_rank, points FROM clans WHERE id = %s",
        (opponent_clan_id,),
    )
    result = cursor.fetchone()
    opponent_stats = {
        "battles": result[0],
        "wins": result[1],
        "average_enemy_rank": result[2],
        "current_points": result[3],
    }

    ### -----------------------------------------------
    ### -----IF CHALLENGER WINS------------------------
    if challenger_win:

        ### update average_enemy_rank, battles and wins for both participants

        # challenger's average_enemy_rank
        challenger_stats["average_enemy_rank"] = (
            challenger_stats["battles"] * challenger_stats["average_enemy_rank"]
            + opponent_stats["current_points"]
        ) / (challenger_stats["battles"] + 1)
        # challenger's battles
        challenger_stats["battles"] = challenger_stats["battles"] + 1
        # challenger's wins
        challenger_stats["wins"] = challenger_stats["wins"] + 1

        # opponent's average enemy rank
        opponent_stats["average_enemy_rank"] = (
            opponent_stats["battles"] * opponent_stats["average_enemy_rank"]
            + challenger_stats["current_points"]
        ) / (opponent_stats["battles"] + 1)
        # opponent's battles
        opponent_stats["battles"] = opponent_stats["battles"] + 1

        ### -----------------CHALLENGER WON------------------------------
        ### solve point_change for both players based on rank differences

        # first solve how rank difference affects point change
        point_difference = abs(challenger_stats["current_points"] - opponent_stats["current_points"])
        point_levels = point_difference // point_level_divident

        # if challenger has bigger rank:
        if challenger_stats["current_points"] > opponent_stats["current_points"]:
            point_change = max(standard_point_change - point_levels, minimum_point_change)
            # challenger gains less points than standard
            challenger_new_points = challenger_stats["current_points"] + point_change
            # opponent loses less points than standard
            opponent_new_points = opponent_stats["current_points"] - point_change

        # if opponent has bigger rank:
        elif challenger_stats["current_points"] < opponent_stats["current_points"]:
            point_change = standard_point_change + point_levels
            # challenger gains more points than standard
            challenger_new_points = challenger_stats["current_points"] + point_change
            # opponent loses more points than standard
            opponent_new_points = opponent_stats["current_points"] - point_change

        # if ranks are exactly equal, challenger gains standard, opponent loses standard
        else:
            challenger_new_points = challenger_stats["current_points"] + standard_point_change
            opponent_new_points = opponent_stats["current_points"] - standard_point_change

    ### ----------------------------------------------------
    ### -----IF OPPONENT WINS-------------------------------
    else:

        # update both players battles, wins, average_enemy_rank

        # opponent's average_enemy_rank
        opponent_stats["average_enemy_rank"] = (
            opponent_stats["battles"] * opponent_stats["average_enemy_rank"]
            + challenger_stats["current_points"]
        ) / (opponent_stats["battles"] + 1)
        # opponent's battles
        opponent_stats["battles"] = opponent_stats["battles"] + 1
        # opponent's wins
        opponent_stats["wins"] = opponent_stats["wins"] + 1

        # challenger's average_enemy_rank
        challenger_stats["average_enemy_rank"] = (
            challenger_stats["battles"] * challenger_stats["average_enemy_rank"]
            + opponent_stats["current_points"]
        ) / (challenger_stats["battles"] + 1)
        # challenger's battles
        challenger_stats["battles"] = challenger_stats["battles"] + 1

        ### --------------OPPONENT WON-----------------------------------
        ### solve point_change for both players based on rank differences

        # first solve how rank difference affects point change
        point_difference = abs(challenger_stats["current_points"] - opponent_stats["current_points"])
        point_levels = point_difference // point_level_divident

        # if challenger has bigger rank:
        if challenger_stats["current_points"] > opponent_stats["current_points"]:
            point_change = standard_point_change + point_levels
            # opponent gains more points than standard
            opponent_new_points = opponent_stats["current_points"] + point_change
            # challenger loses more points than standard
            challenger_new_points = challenger_stats["current_points"] - point_change

        # if opponent has bigger rank:
        elif challenger_stats["current_points"] < opponent_stats["current_points"]:
            point_change = max(standard_point_change - point_levels, minimum_point_change)
            # opponent gains less points than standard
            opponent_new_points = opponent_stats["current_points"] + point_change
            # challenger loses less points than standard
            challenger_new_points = challenger_stats["current_points"] - point_change

        # if ranks are exactly equal, challenger loses standard, opponent gains standard
        else:
            challenger_new_points = challenger_stats["current_points"] - standard_point_change
            opponent_new_points = opponent_stats["current_points"] + standard_point_change

    ### --------------------------------------------
    ### STORE THE NEW AND CURRENT POINTS TO DATABASE

    # update challenger points
    cursor.execute(
        """
        UPDATE clans 
        SET 
            battles = %s, 
            wins = %s, 
            average_enemy_rank = %s, 
            points = %s, 
            old_points = %s 
        WHERE id = %s
        """,
        (
            challenger_stats["battles"],
            challenger_stats["wins"],
            challenger_stats["average_enemy_rank"],
            challenger_new_points,
            challenger_stats["current_points"],
            challenger_clan_id,
        ),
    )

    # update opponent points
    cursor.execute(
        """
        UPDATE clans 
        SET 
            battles = %s, 
            wins = %s, 
            average_enemy_rank = %s, 
            points = %s, 
            old_points = %s 
        WHERE id = %s
        """,
        (
            opponent_stats["battles"],
            opponent_stats["wins"],
            opponent_stats["average_enemy_rank"],
            opponent_new_points,
            opponent_stats["current_points"],
            opponent_clan_id,
        ),
    )
    # all points have been updated!
    return


# _update_clan_points ends
