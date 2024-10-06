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


def get_scores_by_field_and_date(con):
    try:
        cursor = con.cursor()
        count = request.args.get("count")
        field = request.args.get("field")
        entered_date = request.args.get("entered_date")
        query = f'SELECT TOP({count}) * FROM [dbo].[scores] WHERE field = ? AND entered_date = ? ORDER BY entered_time DESC'

        cursor.execute(query, (field, entered_date))

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def add_score(con, log):
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
            log.log_message(request, 200)
            return jsonify(response), 200

        except Exception as e:
            log.log_message(request, 400)
            return jsonify({"error": str(e)}), 400


def update_score(con):
    try:
        score_id = request.args.get('score_id')

        data = request.get_json()

        score_id = int(score_id)

        update_columns = []
        params = []

        if 'score_a' in data:
            update_columns.append('score_a = ?')
            params.append(data['score_a'])
        if 'score_b' in data:
            update_columns.append('score_b = ?')
            params.append(data['score_b'])
        if 'entered_date' in data:
            update_columns.append('entered_date = ?')
            params.append(data['entered_date'])
        if 'entered_time' in data:
            update_columns.append('entered_time = ?')
            params.append(data['entered_time'])

        if not update_columns:
            return jsonify({'error': 'No valid fields provided'}), 400

        sql_query = f"""
            UPDATE [dbo].[scores]
            SET {', '.join(update_columns)}
            WHERE score_id = ?
        """
        params.append(score_id)
        cursor = con.cursor()
        cursor.execute(sql_query, *params)
        con.commit()

        con.close()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Score not found'}), 404
        return jsonify({'message': 'Score updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def delete_score(con):
    score_id = request.args.get("score_id")

    score_id = int(score_id)
    try:

        cursor = con.cursor()
        query = 'DELETE FROM [dbo].[scores] WHERE score_id = ?'
        cursor.execute(query, score_id)

        con.commit()

        message = "The score has been deleted successfully!"
        if cursor.rowcount == 0:
            return jsonify({"error": "Score not found!"}), 404
        con.close()

        return jsonify(message), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

