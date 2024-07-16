from flask import jsonify, request


def get_all_fields(con):
    try:
        cursor = con.cursor()
        query = 'SELECT DISTINCT field_auto as field FROM [dbo].[team_selection] WHERE date = ?'
        value = request.args.get("date")
        cursor.execute(query, value)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_field_by_date_and_team(con):
    try:
        cursor = con.cursor()

        query = 'SELECT DISTINCT team_to_pick FROM [dbo].[team_selection] WHERE field_auto = ? AND date = ?'
        field = request.args.get("field_auto")
        date = request.args.get("date")
        cursor.execute(query, [field, date])
        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
