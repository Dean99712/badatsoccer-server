from flask import jsonify, request


def get_teams_by_field_and_date(con):
    try:
        cursor = con.cursor()

        query = "SELECT DISTINCT REPLACE(LOWER(team_to_pick), ' Team', '') as team from [dbo].[team_selection] WHERE field_auto = ? AND date = ?"

        field = request.args.get("field_auto")
        entered_date = request.args.get("date")
        cursor.execute(query, (field, entered_date))

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        con.close()


def get_all_players(con):
    try:
        cursor = con.cursor()
        query = 'SELECT * FROM team_selection WHERE date = ?'
        value = request.args.get("date")

        cursor.execute(query, value)
        rows = cursor.fetchall()
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_team_by_player_name(con):
    try:
        cursor = con.cursor()
        query = ("SELECT DISTINCT p2.player_id, p2.player_name AS player_name, p1.team_to_pick, p1.team "
                 "FROM team_selection p1"
                 " JOIN team_selection p2 ON p1.team = p2.team"
                 " WHERE p1.player_name = ? "
                 "AND p1.date = ? "
                 "AND p2.date = p1.date "
                 "GROUP BY p2.player_id, p2.player_name, p1.team, p1.team_to_pick "
                 "ORDER BY p2.player_id;")

        player_name = request.args.get("player_name")
        date = request.args.get("date")

        cursor.execute(query, (player_name, date))
        rows = cursor.fetchall()
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
