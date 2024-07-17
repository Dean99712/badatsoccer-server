import os

import pandas as pd
import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import azure_services
import logger as log
from google_services import get_google_sheet, get_data_from_sheet
from services import scores_service as scs, game_service as gs, teams_service as ts, fields_service as fs

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

        unique_pairs = sheet_data[['date', 'player_name']].drop_duplicates()

        or_conditions = ' OR '.join(['(date = ? AND player_name = ?)' for _ in range(len(unique_pairs))])
        check_query = f"SELECT date, player_name FROM team_selection WHERE {or_conditions}"
        cursor.execute(check_query, tuple(unique_pairs.values.flatten()))
        existing_pairs = {(row[0], row[1]) for row in cursor.fetchall()}

        results = []

        for i, row in sheet_data.iterrows():
            # Check for empty values in all columns except 'date' and 'player_name'
            if row.drop(['date', 'player_name']).apply(lambda x: pd.isna(x) or x == '').any():
                results.append({"row": i + 2, "status": "skipped",
                                "message": "Row contains empty values except for date and player_name"})
                continue

            date_field = row['date']
            player_name_field = row['player_name']

            if (date_field, player_name_field) in existing_pairs:
                try:
                    # Construct the SET clause for the update statement
                    set_clause = ', '.join([f"{col} = ?" for col in row.keys() if col not in ['date', 'player_name']])
                    values = tuple(row[col] for col in row.keys() if col not in ['date', 'player_name']) + (
                    date_field, player_name_field)
                    update_query = f"UPDATE team_selection SET {set_clause} WHERE date = ? AND player_name = ?"
                    cursor.execute(update_query, values)
                    results.append({"row": i + 2, "status": "updated", "message": "Row updated successfully"})
                except Exception as update_error:
                    results.append({"row": i + 2, "status": "failed", "message": f"Update error: {update_error}"})
                    log.logger.error(f"Update error for row {i + 2}: {update_error}")
            else:
                try:
                    columns = ', '.join(row.keys())
                    placeholders = ', '.join('?' * len(row))
                    values = tuple(row)
                    insert_query = f"INSERT INTO team_selection ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_query, values)
                    results.append({"row": i + 2, "status": "success", "message": "Row inserted successfully"})
                except Exception as insert_error:
                    results.append({"row": i + 2, "status": "failed", "message": f"Insertion error: {insert_error}"})
                    log.logger.error(f"Insertion error for row {i + 2}: {insert_error}")

        cursor.commit()
        cursor.close()
        log.logger.info('Sheet data processed successfully!')

        return jsonify({"message": "Sheet processed successfully", "results": results}), 200

    except Exception as e:
        log.logger.error(e)
        return jsonify({"error": str(e)}), 400


# @app.route('/insert_sheet_data')
# def insert_data_from_sheet():
#     try:
#         con = connection()
#         cursor = con.cursor()
#
#         sheet_id = "1BL1KkNbhp4cn8WrFByKYUId0Xm10eMqncMdtAMLqkgA"
#         sheet = get_google_sheet(sheet_id)
#         sheet_data = get_data_from_sheet(sheet)
#
#         # Extract all unique dates from the sheet
#         unique_dates = sheet_data['date'].unique()
#
#         # Check if any of these dates exist in the database
#         placeholders = ', '.join('?' * len(unique_dates))
#         check_query = f"SELECT date FROM team_selection WHERE date IN ({placeholders})"
#         cursor.execute(check_query, tuple(unique_dates))
#         existing_dates = {row[0] for row in cursor.fetchall()}
#
#         results = []
#
#         for i, row in sheet_data.iterrows():
#             # Check for empty values in all columns except 'date'
#             if row.drop('date').apply(lambda x: pd.isna(x) or x == '').any():
#                 results.append({"row": i+2, "status": "skipped", "message": "Row contains empty values except for date"})
#                 continue
#
#             date_field = row['date']
#
#             if date_field in existing_dates:
#                 try:
#                     # Construct the SET clause for the update statement
#                     set_clause = ', '.join([f"{col} = ?" for col in row.keys() if col != 'date'])
#                     values = tuple(row[col] for col in row.keys() if col != 'date') + (date_field,)
#                     update_query = f"UPDATE team_selection SET {set_clause} WHERE date = ?"
#                     cursor.execute(update_query, values)
#                     results.append({"row": i+2, "status": "updated", "message": "Row updated successfully"})
#                 except Exception as update_error:
#                     results.append({"row": i+2, "status": "failed", "message": f"Update error: {update_error}"})
#                     log.logger.error(f"Update error for row {i+2}: {update_error}")
#             else:
#                 try:
#                     columns = ', '.join(row.keys())
#                     placeholders = ', '.join('?' * len(row))
#                     values = tuple(row)
#                     insert_query = f"INSERT INTO team_selection ({columns}) VALUES ({placeholders})"
#                     cursor.execute(insert_query, values)
#                     results.append({"row": i+2, "status": "success", "message": "Row inserted successfully"})
#                 except Exception as insert_error:
#                     results.append({"row": i+2, "status": "failed", "message": f"Insertion error: {insert_error}"})
#                     log.logger.error(f"Insertion error for row {i+2}: {insert_error}")
#
#         cursor.commit()
#         cursor.close()
#         log.logger.info('Sheet data processed successfully!')
#
#         return jsonify({"message": "Sheet processed successfully", "results": results}), 200
#
#     except Exception as e:
#         log.logger.error(e)
#         return jsonify({"error": str(e)}), 400

# @app.route('/insert_sheet_data')
# def insert_data_from_sheet():
#     try:
#         con = connection()
#         cursor = con.cursor()
#
#         sheet_id = "1BL1KkNbhp4cn8WrFByKYUId0Xm10eMqncMdtAMLqkgA"
#         sheet = get_google_sheet(sheet_id)
#         sheet_data = get_data_from_sheet(sheet)
#
#         # Extract all unique dates from the sheet
#         unique_dates = sheet_data['date'].unique()
#
#         # Check if any of these dates exist in the database
#         placeholders = ', '.join('?' * len(unique_dates))
#         check_query = f"SELECT COUNT(1) FROM team_selection WHERE date IN ({placeholders})"
#         cursor.execute(check_query, tuple(unique_dates))
#         count = cursor.fetchone()[0]
#
#         if count > 0:
#             print(placeholders)
#             # return jsonify({"message": "Data already exists"}), 200
#
#         # If no existing records found, proceed to insert data
#         results = []
#
#         for i, row in sheet_data.iterrows():
#             # Check for empty values in all columns except 'date'
#             if row.drop('date').apply(lambda x: pd.isna(x) or x == '').any():
#                 continue
#
#             try:
#                 columns = ', '.join(row.keys())
#                 placeholders = ', '.join('?' * len(row))
#                 values = tuple(row)
#                 insert_query = f"INSERT INTO team_selection ({columns}) VALUES ({placeholders})"
#                 cursor.execute(insert_query, values)
#             except Exception as insert_error:
#                 log.logger.error(f"Insertion error for row {i + 2}: {insert_error}")
#
#         cursor.commit()
#         cursor.close()
#         log.logger.info('Sheet data processed successfully!')
#
#         return jsonify({"message": "Sheet processed successfully", "results": results}), 200
#
#     except Exception as e:
#         log.logger.error(e)
#         return jsonify({"error": str(e)}), 400


@app.route('/search_players_by_name')
def search_players_by_name():
    try:
        cursor = connection().cursor()
        search_text = request.args.get('query')
        query = "SELECT * FROM team_selection WHERE date = ? AND player_name LIKE '%{}%'".format(search_text)
        params = (request.args.get('date'),)
        cursor.execute(query, params)
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


@app.route('/get_all_players')
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
