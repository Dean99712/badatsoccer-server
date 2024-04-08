from flask import jsonify, request


def format_date(d):
    return d.strftime('%Y-%m-%d')


def get_games_dates(con):
    try:
        cursor = con.cursor()

        cursor.execute('SET DATEFORMAT dmy;')

        query = 'SELECT DISTINCT TOP(5) CONVERT(DATE, date) AS date FROM [dbo].[team_selection] ORDER BY date DESC;'

        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        result = [{'date': format_date(row['date'])} for row in rows]

        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_team_by_field(con):
    try:
        cursor = con.cursor()
        query = 'SELECT DISTINCT team_1, team_2, team_3 from [dbo].[games] WHERE field = ?'
        value = request.args.get("field")
        cursor.execute(query, value)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def add_game(con):
    if request.method == 'POST':
        try:
            data = request.get_json()

            cursor = con.cursor()

            insert_query = (
                "INSERT INTO [dbo].[games] (date, field, team_1, team_2, team_3)"
                " VALUES (?, ?, ?, ?, ?)")

            cursor.execute(insert_query, (data['date'], data['field'], data['team_1'], data['team_2'], data['team_3']))

            con.commit()
            cursor.close()
            message = "Data inserted successfully"
            response = {message}
            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400


def get_games_statistics_by_team_and_date(con):
    try:
        cursor = con.cursor()
        query = 'SELECT DISTINCT team_a, score_a, team_b, score_b from scores where entered_date = ? and field = ?'

        entered_date = request.args.get("entered_date")
        field = request.args.get("field")

        cursor.execute(query, (entered_date, field))

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
