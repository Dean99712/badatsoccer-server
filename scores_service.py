from datetime import datetime

from flask import jsonify, request


def convert_date_format(iso_str):
    date_obj = datetime.strptime(iso_str, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    return formatted_date


def get_scores(con):
    try:

        cursor = con.cursor()
        cursor.execute(f'SELECT * FROM [dbo].[scores] ORDER BY entered_time DESC')

        rows = cursor.fetchall()

        data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def add_score(con):
    if request.method == 'POST':

        try:
            data = request.get_json()

            cursor = con.cursor()

            insert_query = (
                "INSERT INTO [dbo].[scores] (team_a, score_a, team_b, score_b, entered_by, entered_date, entered_time, field)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)")

            data['entered_date'] = convert_date_format(data['entered_date'])

            cursor.execute(insert_query, (
                data['team_a'], data['score_a'], data['team_b'], data['score_b'], data['entered_by'],
                data['entered_date'], data['entered_time'], data['field']))

            con.commit()
            cursor.close()

            response = {"message": "Data inserted successfully"}
            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400


def get_score_by_id(con):
    try:
        cursor = con.cursor()
        query = 'SELECT * FROM [dbo].[scores] WHERE score_id = ?'
        value = request.args.get("score_id")
        cursor.execute(query, value)

        rows = cursor.fetchall()

        data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        if cursor.rowcount == 0:
            return jsonify({"error": "Score not found!"}), 404
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
