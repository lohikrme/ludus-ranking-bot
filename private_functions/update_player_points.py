# update_player_points.py
# updated 2nd october 2024

from services import conn


# UPDATE PLAYER POINTS IN DATABASE
async def _update_player_points(challenger, opponent, challenger_win: bool):

    # these can be updated as need
    standard_point_change = 20
    point_level_divident = 60
    minimum_point_change = 2

    # fetch current points from database
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT battles, wins, average_enemy_rank, points 
        FROM players WHERE discord_id = %s
        """,
        (str(challenger.id),),
    )
    result = cursor.fetchone()
    challenger_stats = {
        "battles": result[0],
        "wins": result[1],
        "average_enemy_rank": result[2],
        "current_points": result[3],
    }
    cursor.execute(
        """
        SELECT battles, wins, average_enemy_rank, points 
        FROM players WHERE discord_id = %s
        """,
        (str(opponent.id),),
    )
    result = cursor.fetchone()
    opponent_stats = {
        "battles": result[0],
        "wins": result[1],
        "average_enemy_rank": result[2],
        "current_points": result[3],
    }

    # CALCULATE TOTAL POINT CHANGE, AND THEN, HOW MANY POINT_lEVEL DIFFERENCES THERE ARE
    point_difference = abs(challenger_stats["current_points"] - opponent_stats["current_points"])

    point_levels = point_difference // point_level_divident

    # INITIATE NEW POINTS, AND THEN CALCULATE THE NEW POINTS BASED ON THE FORMULA
    challenger_new_points = challenger_stats["current_points"]
    opponent_new_points = opponent_stats["current_points"]

    # IF CHALLENGER WINS
    if challenger_win:
        # update both players battles, wins, average_enemy_rank
        challenger_stats["average_enemy_rank"] = (
            challenger_stats["battles"] * challenger_stats["average_enemy_rank"]
            + opponent_stats["current_points"]
        ) / (challenger_stats["battles"] + 1)
        challenger_stats["battles"] = challenger_stats["battles"] + 1
        challenger_stats["wins"] = challenger_stats["wins"] + 1

        opponent_stats["average_enemy_rank"] = (
            opponent_stats["battles"] * opponent_stats["average_enemy_rank"]
            + challenger_stats["current_points"]
        ) / (opponent_stats["battles"] + 1)
        opponent_stats["battles"] = opponent_stats["battles"] + 1

        # solve point change amount for both players
        if challenger_stats["current_points"] > opponent_stats["current_points"]:
            point_change = max(standard_point_change - point_levels, minimum_point_change)
            challenger_new_points = (
                challenger_stats["current_points"] + point_change
            )  # challenger gains points
            opponent_new_points = (
                opponent_stats["current_points"] - point_change
            )  # opponent loses points

        elif challenger_stats["current_points"] < opponent_stats["current_points"]:
            point_change = standard_point_change + point_levels
            challenger_new_points = (
                challenger_stats["current_points"] + point_change
            )  # challenger gains points
            opponent_new_points = (
                opponent_stats["current_points"] - point_change
            )  # opponent loses points

        else:
            challenger_new_points = challenger_stats["current_points"] + standard_point_change
            opponent_new_points = opponent_stats["current_points"] - standard_point_change

    # IF OPPONENT WINS
    else:
        # update both players battles, wins, average_enemy_rank
        opponent_stats["average_enemy_rank"] = (
            opponent_stats["battles"] * opponent_stats["average_enemy_rank"]
            + challenger_stats["current_points"]
        ) / (opponent_stats["battles"] + 1)
        opponent_stats["battles"] = opponent_stats["battles"] + 1
        opponent_stats["wins"] = opponent_stats["wins"] + 1

        challenger_stats["average_enemy_rank"] = (
            challenger_stats["battles"] * challenger_stats["average_enemy_rank"]
            + opponent_stats["current_points"]
        ) / (challenger_stats["battles"] + 1)
        challenger_stats["battles"] = challenger_stats["battles"] + 1

        # solve point change amount for both players
        if challenger_stats["current_points"] > opponent_stats["current_points"]:
            point_change = standard_point_change + point_levels
            opponent_new_points = (
                opponent_stats["current_points"] + point_change
            )  # opponent gains points
            challenger_new_points = (
                challenger_stats["current_points"] - point_change
            )  # challenger loses points

        elif challenger_stats["current_points"] < opponent_stats["current_points"]:
            point_change = max(standard_point_change - point_levels, minimum_point_change)
            opponent_new_points = (
                opponent_stats["current_points"] + point_change
            )  # opponent gains points
            challenger_new_points = (
                challenger_stats["current_points"] - point_change
            )  # challenger loses points

        else:
            challenger_new_points = challenger_stats["current_points"] - standard_point_change
            opponent_new_points = opponent_stats["current_points"] + standard_point_change

    # STORE THE NEW POINTS TO DATABASE AS POINTS, AND CURRENT POINTS AND OLD_POINTS
    # update challenger points
    cursor.execute(
        """
        UPDATE players 
        SET 
            battles = %s, 
            wins = %s, 
            average_enemy_rank = %s, 
            points = %s, 
            old_points = %s 
        WHERE discord_id = %s
        """,
        (
            challenger_stats["battles"],
            challenger_stats["wins"],
            challenger_stats["average_enemy_rank"],
            challenger_new_points,
            challenger_stats["current_points"],
            str(challenger.id),
        ),
    )
    # update opponent points
    cursor.execute(
        """
        UPDATE players 
        SET 
            battles = %s, 
            wins = %s, 
            average_enemy_rank = %s, 
            points = %s, 
            old_points = %s 
        WHERE discord_id = %s
        """,
        (
            opponent_stats["battles"],
            opponent_stats["wins"],
            opponent_stats["average_enemy_rank"],
            opponent_new_points,
            opponent_stats["current_points"],
            str(opponent.id),
        ),
    )
    return


# update player points ends
