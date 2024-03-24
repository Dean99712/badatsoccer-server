import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS

import game_service as gs
import logger as log
import scores_service as scs
from auth import get_google_sheet, get_data_from_sheet
from config import Config as cnf

app = Flask(__name__)
app.logger.addHandler(log.logger)
CORS(app,
     resources={r"/*": {"origins": ["http://localhost:3000", "https://witty-mud-09afa6410.3.azurestaticapps.net"]}})


def connection():
    con = pyodbc.connect(
        f'DRIVER={cnf.Driver};SERVER={cnf.Server}, {cnf.Port};DATABASE={cnf.Database};Uid={cnf.Uid};Pwd={cnf.Pwd};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"Trusted_Connection=yes;" "Auto_Commit=true;"')
    return con


@app.route('/')
def home():
    message = 'Welcome to the Bad at Soccer API!'
    log.log_message(request, message)
    log.logger.info('Welcome to the Bad at Soccer API!')
    return message


@app.route('/sheet_log')
def logs():
    with open(log.location, 'r') as log_file:
        log_contents = log_file.read()
    print(log_contents)
    return jsonify(log_contents)


@app.route('/insert_sheet_data')
def insert_data_from_sheet():
    try:
        con = connection()
        cursor = con.cursor()

        sheet_id = "1TnsWwX_n2nXTDvZAGVQ_tnrKKk8oZZoYggy8fSF8b9Q"

        sheet = get_google_sheet(sheet_id)

        data = get_data_from_sheet(sheet)

        for i, row in data.iterrows():
            columns = ', '.join(row.keys())
            placeholders = ', '.join('?' for _ in row)
            values = tuple(row)

            insert_query = f"INSERT INTO team_selection ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, values)

        cursor.commit()
        cursor.close()

        log.logger.info("Sheet loaded successfully!")
        return "Sheet loaded successfully!", 200

    except Exception as e:
        log.logger.error(e)
        return jsonify({"error": str(e)}), 400


@app.route('/get_all_fields')
def get_all_fields():
    try:
        con = connection()
        cursor = con.cursor()
        query = 'SELECT DISTINCT field FROM [dbo].[games]'
        cursor.execute(query)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

        con.close()
        log.logger.info('Fields retrieved successfully!')
        log.log_message(request, 200)
        return jsonify(result), 200

    except Exception as e:
        log.logger.error(e)
        log.log_message(request, 400)
        return jsonify({"error": str(e)}), 400


@app.route('/get_field')
def get_fields():
    try:
        con = connection()
        cursor = con.cursor()
        query = 'SELECT DISTINCT team_1, team_2, team_3 FROM [dbo].[games] WHERE field = ?'
        value = request.args.get("field")
        cursor.execute(query, value)
        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        log.logger.info('Field retrieved successfully!')
        return jsonify(result), 200

    except Exception as e:
        log.logger.error(e)
        return jsonify({"error": str(e)}), 400


@app.route('/get_team_by_field')
def get_team_by_field():
    try:
        con = connection()

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


@app.route('/add_score', methods=['POST'])
def add_score():
    return scs.add_score(connection())


@app.route('/get_scores')
def get_scores():
    return scs.get_scores(connection())


@app.route('/get_score_by_id')
def get_score_by_id():
    return scs.get_score_by_id(connection())


@app.route('/get_scores_by_field_name_and_date')
def get_scores_by_field_name():
    try:
        con = connection()
        cursor = con.cursor()
        query = 'SELECT * FROM [dbo].[scores] WHERE field = ? AND entered_date = ? ORDER BY entered_time DESC'
        field = request.args.get("field")
        entered_date = request.args.get("entered_date")
        cursor.execute(query, (field, entered_date))

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_scores_by_date')
def get_scores_by_date():
    try:
        con = connection()

        cursor = con.cursor()
        query = 'SELECT * FROM [dbo].[scores] WHERE entered_date = ? ORDER BY entered_time DESC'
        value = request.args.get("entered_date")
        cursor.execute(query, value)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/delete_score', methods=['DELETE'])
def delete_score():
    score_id = request.args.get("score_id")

    score_id = int(score_id)
    try:
        con = connection()

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


@app.route('/update_score', methods=['PATCH'])
def update_score():
    try:
        con = connection()

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


@app.route('/add_game', methods=['POST'])
def add_game():
    if request.method == 'POST':
        try:
            con = connection()

            data = request.get_json()

            cursor = con.cursor()

            insert_query = (
                "INSERT INTO [dbo].[games] (date, field, team_1, team_2, team_3)"
                " VALUES (?, ?, ?, ?, ?)")

            cursor.execute(insert_query, (data['date'], data['field'], data['team_1'], data['team_2'], data['team_3']))

            con.commit()
            cursor.close()

            response = {"message": "Data inserted successfully"}
            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400


@app.route('/get_games_dates')
def get_games_dates():
    try:
        con = connection()
        cursor = con.cursor()
        query = ('SELECT * FROM '
                 '(SELECT DISTINCT date FROM [dbo].[games])'
                 ' AS subquery'
                 ' ORDER BY date;')

        cursor.execute(query)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_games_statistics_by_team_and_date')
def get_games_statistics_by_team_and_date():
    return gs.get_games_statistics_by_team_and_date(connection())


# @app.route('/read_sheet')
# def index():
#     try:
#         spreadsheet_id = '18XJbsh2uWjwSd2JfPV9HcWgzJBL3jLyJi09l4jthkeA'
#         sheets = service.spreadsheets()
#         result = sheets.get(spreadsheetId=spreadsheet_id).execute()
#         cell_date = result.get("sheets")
#
#         for row in cell_date:
#             for column in row:
#                 print(column)
#             print(row)
#         return jsonify(cell_date)
#     except Exception as e:
#         log.logger.error(e)
#         return jsonify({"error": str(e)}), 400


@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        try:
            con = connection()

            data = request.get_json()

            cursor = con.cursor()
            insert_query = "INSERT INTO [dbo].[user] (user_id, email, name, password) VALUES (?, ?, ?, ?)"
            cursor.execute(insert_query, (
                data['user_id'], data['email'], data['name'], data['password']))

            con.commit()
            cursor.close()

            response = {"message": "Data inserted successfully"}

            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
