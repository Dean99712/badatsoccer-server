import os

import bcrypt
import pandas as pd
import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import UserMixin
from werkzeug.utils import secure_filename

import azure_services
import google_services as gos
import logger as log
from google_services import get_google_sheet, get_data_from_sheet
from services import scores_service as scs, game_service as gs, teams_service as ts, fields_service as fs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

CORS(app,
     resources={r"/*": {"origins": ["http://localhost:3000", "https://witty-mud-09afa6410.3.azurestaticapps.net",
                                    'https://www.bad-at-soccer.in', 'https://bad-at-soccer.in',
                                    'https://python-flask-webapp-t.azurewebsites.net']}})

CONTAINER_NAME = 'player-photo'


class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password


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


@app.route('/insert_team_selection_sheet_data')
def insert_team_selection_sheet_data():
    try:
        con = connection()  # Get the database connection
        cursor = con.cursor()

        sheet_id = "1BL1KkNbhp4cn8WrFByKYUId0Xm10eMqncMdtAMLqkgA"
        sheet = get_google_sheet(sheet_id)
        sheet_data = get_data_from_sheet(sheet, 'A', 'L')

        # Fetch unique combinations of date and player_name from sheet data
        unique_pairs = sheet_data[['date', 'player_name']].drop_duplicates()

        # Build the WHERE condition with multiple OR conditions
        or_conditions = ' OR '.join(['(date = ? AND player_name = ?)' for _ in range(len(unique_pairs))])
        check_query = f"SELECT date, player_name FROM team_selection WHERE {or_conditions}"
        cursor.execute(check_query, tuple(unique_pairs.values.flatten()))
        existing_pairs = {(row[0], row[1]) for row in cursor.fetchall()}

        results = []

        # Loop through sheet data rows
        for i, row in sheet_data.iterrows():
            # Skip rows with empty values (except date and player_name)
            if row.drop(['date', 'player_name']).apply(lambda x: pd.isna(x) or x == '').any():
                results.append({"row": i + 2, "status": "skipped",
                                "message": "Row contains empty values except for date and player_name"})
                continue

            date_field = row['date']
            player_name_field = row['player_name']

            if (date_field, player_name_field) in existing_pairs:
                # Update existing record
                try:
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
                # Insert new record
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

        # Commit the transaction
        con.commit()
        cursor.close()
        log.logger.info('Sheet data processed successfully!')

        return jsonify({"message": "Sheet processed successfully", "results": results}), 200

    except Exception as e:
        # Rollback the transaction in case of an error
        con.rollback()
        log.logger.error(e)
        return jsonify({"error": str(e)}), 400


@app.route('/insert_players_sheet_data')
def insert_players_sheet_data():
    try:
        con = connection()
        cursor = con.cursor()

        sheet_id = "11j5LnCerz_RhTYrVZoksFBLHyFVFq23TyItJt70x2MY"
        sheet = get_google_sheet(sheet_id)
        sheet_data = get_data_from_sheet(sheet, 'A', 'N')

        results = []

        for i, row in sheet_data.iterrows():
            try:
                # Handle password logic
                password = row.get('password', '')
                if not password:
                    password = f"{row['player_name'][0]}{row['phone_number']}"
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                row['password'] = hashed_password

                player_name = row['player_name']
                cursor.execute("SELECT * FROM players WHERE player_name = ?", player_name)
                existing_player = cursor.fetchone()

                if existing_player:
                    # Update existing player
                    set_clause = ', '.join([f"{col} = ?" for col in row.keys() if col not in ['player_name']])
                    values = tuple(row[col] for col in row.keys() if col not in ['player_name']) + (player_name,)
                    update_query = f"UPDATE players SET {set_clause} WHERE player_name = ?"
                    cursor.execute(update_query, values)
                    results.append({"row": i + 2, "status": "updated", "message": "Player updated successfully"})
                else:
                    # Insert new player
                    columns = ', '.join(row.keys())
                    placeholders = ', '.join('?' * len(row))
                    values = tuple(row)
                    insert_query = f"INSERT INTO players ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_query, values)
                    results.append({"row": i + 2, "status": "success", "message": "Player inserted successfully"})

                con.commit()
            except Exception as insert_error:
                results.append({"row": i + 2, "status": "failed", "message": f"Insertion error: {insert_error}"})
                log.logger.error(f"Insertion error for row {i + 2}: {insert_error}")

        cursor.close()
        con.close()
        log.logger.info('Sheet data processed successfully!')

        return jsonify({"message": "Sheet processed successfully", "results": results}), 200

    except Exception as e:
        log.logger.error(e)
        return jsonify({"error": str(e)}), 400


@app.route('/search_players_by_name')
def search_players_by_name():
    try:
        cursor = connection().cursor()
        search_text = request.args.get('query')
        query = "SELECT * FROM team_selection WHERE date = ? AND player_name LIKE '%{}%'".format(search_text)
        params = (request.args.get('date'))
        cursor.execute(query, params)
        rows = cursor.fetchall()
        data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_images_from_azure')
def get_images_from_azure():
    blob_list = []
    container_client = azure_services.connect_to_azure_storage('player-photo')
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


@app.route('/get_team')
def get_team():
    return ts.get_team(connection())


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


@app.route('/update_players_images')
def update_players_images():
    gos.transfer_files('1VhVxbMnRgsP44sQGSrIETabD4eBhkfLV', container_name=CONTAINER_NAME)
    log.logger.info('Players images updated successfully!'), 200
    return jsonify('Players images updated successfully!'), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['gmail']
    password = data['password']

    con = connection()
    if con is None:
        return jsonify({"message": "Connection to database failed"}), 500

    cursor = con.cursor()
    cursor.execute("SELECT id, gmail, password, type, player_name FROM players WHERE gmail = ?", email)
    user = cursor.fetchone()
    cursor.close()
    con.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        user_data = {
            'id': user.id,
            'gmail': user.gmail,
            'password': user.password,
            'roles': [user.type],
            "player_name": user.player_name
        }

        return jsonify({'data': user_data, 'status_code': 200, 'message': 'Player retrieved successfully !'}), 200
    else:
        return jsonify({"message": "Invalid credentials!"}), 401


if __name__ == '__main__':
    # Production mode
    # app.run()

    # Development mode
    app.run(debug=True)
