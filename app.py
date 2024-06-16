import os

import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import azure_services
import logger as log
from google_services import get_google_sheet, get_data_from_sheet
from service import scores_service as scs, game_service as gs, teams_service as ts, fields_service as fs

app = Flask(__name__)

CORS(app,
     resources={r"/*": {"origins": ["http://localhost:3000", "https://witty-mud-09afa6410.3.azurestaticapps.net",
                                    'https://www.bad-at-soccer.in', 'https://bad-at-soccer.in',
                                    'https://python-flask-webapp-t.azurewebsites.net']}})


def connection():
    connection_string = os.environ.get('SQLCONNSTR_AZURE_SQL')
    if connection_string is not None:
        connection_string = str(connection_string)
    else:
        message = '"SQLCONNSTR_AZURE_SQL not found in environment variables"'
        log.logger.error(message)
        return message
    con = pyodbc.connect(connection_string)
    return con


@app.route('/')
def home():
    message = 'Welcome to the Bad at Soccer API!'
    # gos.transfer_files('1sMREp7bbwho-oijNBonRI8r1BEp0lOwI', 'players-photos')
    return jsonify(message)


@app.route('/log')
def logs():
    with open(f'{log.LOGS_DIR}/{log.LOG_NAME}', 'r') as log_file:
        log_contents = log_file.read()
    return jsonify({"log_data": log_contents, "log_name": log.LOG_NAME})


@app.route('/logs/clear', methods=['POST'])
def clear_log():
    try:
        with open(os.path.join(f'{log.LOGS_DIR}', secure_filename(log.LOG_NAME)), 'w'):
            pass
        log.log_message(request, 200)
        log.logger.info('Log file cleared')
        return jsonify({"success": True, "message": "Log file cleared"})
    except Exception as e:
        log.logger.error(e)
        log.log_message(request, 500)
        return jsonify({"error": str(e)}), 500


@app.route('/insert_sheet_data')
def insert_data_from_sheet():
    try:
        con = connection()
        cursor = con.cursor()

        sheet_id = "1BL1KkNbhp4cn8WrFByKYUId0Xm10eMqncMdtAMLqkgA"

        sheet = get_google_sheet(sheet_id)

        sheet_data = get_data_from_sheet(sheet)

        for i, row in sheet_data.iterrows():
            if not all(row):
                continue

            columns = ', '.join(row.keys())
            placeholders = ', '.join('?' * len(row))
            values = tuple(row)
            insert_query = f"INSERT INTO team_selection ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, values)

        cursor.commit()
        cursor.close()
        log.logger.info('Sheet data inserted successfully!')
        return "Sheet loaded successfully!", 200

    except Exception as e:
        log.logger.error(e)
        return jsonify({"error": str(e)}), 400


@app.route('/search_players_by_name')
def search_players_by_name():
    try:
        cursor = connection().cursor()
        search_text = request.args.get('query')
        query = "SELECT DISTINCT player_name FROM team_selection WHERE player_name LIKE '%{}%'".format(search_text)
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_images_from_azure')
def get_images_from_azure():
    blob_list = []
    container_client = azure_services.connect_to_azure_storage()
    blob_items = container_client.list_blobs()
    for blob in blob_items:
        blob_item = container_client.get_blob_client(blob=blob.name)
        blob_list.append({'player_url': blob_item.url, 'player_name': blob.name})
    return jsonify(blob_list), 200


@app.route('/get_all_fields')
def get_all_fields():
    return fs.get_all_fields(connection())


@app.route('/get_field')
def get_field():
    return fs.get_field_by_date_and_team(connection())


@app.route('/get_teams_by_field_and_date')
def get_teams_by_field_and_date():
    return ts.get_teams_by_field_and_date(connection())


@app.route('/get_all_player')
def get_all_players():
    return ts.get_all_players(connection())


@app.route('/get_team_by_player_name')
def get_team_by_player_name():
    return ts.get_team_by_player_name(connection())


@app.route('/add_score', methods=['POST'])
def add_score():
    return scs.add_score(connection(), log)


@app.route('/get_scores')
def get_scores():
    return scs.get_scores(connection())


@app.route('/get_score_by_id')
def get_score_by_id():
    return scs.get_score_by_id(connection())


@app.route('/get_scores_by_field_and_date')
def get_scores_by_field_and_date():
    return scs.get_scores_by_field_and_date(connection())


@app.route('/delete_score', methods=['DELETE'])
def delete_score():
    return scs.delete_score(connection())


@app.route('/update_score', methods=['PATCH'])
def update_score():
    return scs.update_score(connection())


@app.route('/get_games_dates')
def get_games_dates():
    return gs.get_games_dates(connection())


@app.route('/get_games_statistics_by_team_and_date')
def get_games_statistics_by_team_and_date():
    return gs.get_games_statistics_by_team_and_date(connection())


# Add a new route to create a user

# @app.route('/create_user', methods=['POST'])
# def create_user():
#     if request.method == 'POST':
#         try:
#             con = connection()
#
#             data = request.get_json()
#
#             cursor = con.cursor()
#             insert_query = "INSERT INTO user (user_id, email, name, password) VALUES (?, ?, ?, ?)"
#             cursor.execute(insert_query, (
#                 data['user_id'], data['email'], data['name'], data['password']))
#
#             con.commit()
#             cursor.close()
#
#             response = {"message": "Data inserted successfully"}
#
#             return jsonify(response), 200
#
#         except Exception as e:
#             return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    # Production mode
    # app.run()

    # Development mode
    app.run(debug=True)