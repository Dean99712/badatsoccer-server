from flask import jsonify, request


def format_date(d):
    return d.strftime('%Y-%m-%d')


def get_games_dates(con):
    try:
        cursor = con.cursor()

        cursor.execute('SET DATEFORMAT dmy;')

        query = 'SELECT DISTINCT TOP(5) CONVERT(DATE, date) AS date FROM team_selection ORDER BY date DESC;'

        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        result = [{'date': format_date(row['date'])} for row in rows]

        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_games_statistics_by_team_and_date(con):
    try:
        cursor = con.cursor()
        entered_date = request.args.get("entered_date")
        field = request.args.get("field")
        query = 'SELECT * FROM scores where entered_date = ? and field = ?'
        cursor.execute(query, (entered_date, field))

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
