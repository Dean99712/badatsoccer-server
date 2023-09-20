import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config as cnf
import googleapiclient.discovery
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)

con = pyodbc.connect(
    f'DRIVER={cnf.Driver};SERVER={cnf.Server}, {cnf.Port};DATABASE={cnf.Database};Uid={cnf.Uid};Pwd={cnf.Pwd};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')

SERVICE_ACCOUNT_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/get_scores')
def get_scores():
    cursor = con.cursor()
    cursor.execute(f'SELECT * FROM [dbo].[scores]')

    rows = cursor.fetchall()

    data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

    return jsonify(data)


@app.route('/get')
def connection():
    cursor = con.cursor()
    cursor.execute(f'SELECT * FROM [dbo].[user]')

    rows = cursor.fetchall()

    data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

    return jsonify(data)


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
