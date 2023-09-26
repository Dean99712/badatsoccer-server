import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config as cnf
import googleapiclient.discovery
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

con = pyodbc.connect(
    f'DRIVER={cnf.Driver};SERVER={cnf.Server}, {cnf.Port};DATABASE={cnf.Database};Uid={cnf.Uid};Pwd={cnf.Pwd};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"Trusted_Connection=yes;" "Auto_Commit=true;"')

SERVICE_ACCOUNT_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/get_all_fields')
def get_all_fields():
    try:
        cursor = con.cursor()
        query = 'SELECT DISTINCT field FROM [dbo].[team_selection]'
        cursor.execute(query)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_field')
def get_fields():
    try:
        cursor = con.cursor()
        query = 'SELECT DISTINCT team, field FROM [dbo].[team_selection] WHERE field = ?'
        value = request.args.get("field")
        cursor.execute(query, value)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_team_by_field')
def get_team_by_field():
    try:
        cursor = con.cursor()
        query = 'SELECT DISTINCT team  FROM [dbo].[team_selection] WHERE field = ?'
        value = request.args.get("field")
        cursor.execute(query, value)

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/add_score', methods=['POST'])
def add_score():
    if request.method == 'POST':

        try:

            data = request.get_json()

            cursor = con.cursor()
            insert_query = "INSERT INTO [dbo].[scores] (team_a, score_a, team_b, score_b, entered_by, entered_time, field) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert_query, (
                data['team_a'], data['score_a'], data['team_b'], data['score_b'], data['entered_by'],
                data['entered_time'], data['field']))

            con.commit()
            cursor.close()

            response = {"message": "Data inserted successfully"}
            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400


@app.route('/get_scores')
def get_scores():
    try:
        cursor = con.cursor()
        cursor.execute(f'SELECT * FROM [dbo].[scores]')

        rows = cursor.fetchall()

        data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/read_sheet')
def index():
    spreadsheet_id = '18XJbsh2uWjwSd2JfPV9HcWgzJBL3jLyJi09l4jthkeA'
    sheets = service.spreadsheets()
    result = sheets.get(spreadsheetId=spreadsheet_id).execute()
    cell_date = result.get("sheets")

    for row in cell_date:
        for column in row:
            print(column)
        print(row)
    return jsonify(cell_date)


@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        try:

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
