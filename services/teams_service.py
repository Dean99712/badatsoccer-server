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
        query = 'SELECT * FROM team_selection WHERE date = ? AND field_auto = ?'
        date = request.args.get("date")
        field = request.args.get("field")

        cursor.execute(query, (date, field))

        rows = cursor.fetchall()
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_team(con):
    try:
        cursor = con.cursor()
        query = ("SELECT * FROM [dbo].[team_selection] "
                 "WHERE team_to_pick = ? "
                 "AND field_auto = ? "
                 "AND date = ?")

        team_to_pick = request.args.get("team_to_pick")
        field_auto = request.args.get("field_auto")
        date = request.args.get("date")

        cursor.execute(query, (team_to_pick, field_auto, date))
        rows = cursor.fetchall()
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
