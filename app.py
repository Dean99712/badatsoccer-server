# from datetime import datetime
#
# import pyodbc
# from flask import Flask, request, jsonify
# from flask_cors import CORS
#
# from auth import get_google_sheet, get_data_from_sheet
# from config import Config as cnf
#
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
#
#
# def connection():
#     con = pyodbc.connect(
#         f'DRIVER={cnf.Driver};SERVER={cnf.Server}, {cnf.Port};DATABASE={cnf.Database};Uid={cnf.Uid};Pwd={cnf.Pwd};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"Trusted_Connection=yes;" "Auto_Commit=true;"')
#     return con
#
#
# def convert_date_format(iso_str):
#     date_obj = datetime.strptime(iso_str, "%Y-%m-%d")
#     formatted_date = date_obj.strftime("%Y-%m-%d")
#     return formatted_date
#
#
# @app.route('/')
# def home():
#     return "Welcome to the Bad at Soccer API!"
#
#
# @app.route('/insert_sheet_data')
# def insert_data_from_sheet():
#     try:
#         con = connection()
#         cursor = con.cursor()
#
#         sheet_id = "1TnsWwX_n2nXTDvZAGVQ_tnrKKk8oZZoYggy8fSF8b9Q"
#
#         sheet = get_google_sheet(sheet_id)
#
#         data = get_data_from_sheet(sheet)
#         for i, row in data.iterrows():
#             columns = ', '.join(row.keys())
#             placeholders = ', '.join('?' for _ in row)
#             values = tuple(row)
#
#             insert_query = f"INSERT INTO team_selection ({columns}) VALUES ({placeholders})"
#             cursor.execute(insert_query, values)
#
#         cursor.commit()
#         cursor.close()
#
#         return "Data inserted successfully!", 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_all_fields')
# def get_all_fields():
#     try:
#         con = connection()
#         cursor = con.cursor()
#         query = 'SELECT DISTINCT field FROM [dbo].[games]'
#         cursor.execute(query)
#
#         rows = cursor.fetchall()
#
#         result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#
#         con.close()
#
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_field')
# def get_fields():
#     try:
#         con = connection()
#         cursor = con.cursor()
#         query = 'SELECT DISTINCT team_1, team_2, team_3 FROM [dbo].[games] WHERE field = ?'
#         value = request.args.get("field")
#         cursor.execute(query, value)
#         rows = cursor.fetchall()
#
#         result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_team_by_field')
# def get_team_by_field():
#     try:
#         con = connection()
#
#         cursor = con.cursor()
#         query = 'SELECT DISTINCT team_1, team_2, team_3 from [dbo].[games] WHERE field = ?'
#         value = request.args.get("field")
#         cursor.execute(query, value)
#
#         rows = cursor.fetchall()
#
#         result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/add_score', methods=['POST'])
# def add_score():
#     if request.method == 'POST':
#
#         try:
#             con = connection()
#
#             data = request.get_json()
#
#             cursor = con.cursor()
#
#             insert_query = (
#                 "INSERT INTO [dbo].[scores] (team_a, score_a, team_b, score_b, entered_by, entered_date, entered_time, field)"
#                 " VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
#
#             data['entered_date'] = convert_date_format(data['entered_date'])
#
#             cursor.execute(insert_query, (
#                 data['team_a'], data['score_a'], data['team_b'], data['score_b'], data['entered_by'],
#                 data['entered_date'], data['entered_time'], data['field']))
#
#             con.commit()
#             cursor.close()
#
#             response = {"message": "Data inserted successfully"}
#             return jsonify(response), 200
#
#         except Exception as e:
#             return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_scores')
# def get_scores():
#     try:
#         con = connection()
#
#         cursor = con.cursor()
#         cursor.execute(f'SELECT * FROM [dbo].[scores] ORDER BY entered_time DESC')
#
#         rows = cursor.fetchall()
#
#         data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         return jsonify(data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_score_by_id')
# def get_score_by_id():
#     try:
#         con = connection()
#
#         cursor = con.cursor()
#         query = 'SELECT * FROM [dbo].[scores] WHERE score_id = ?'
#         value = request.args.get("score_id")
#         cursor.execute(query, value)
#
#         rows = cursor.fetchall()
#
#         data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         if cursor.rowcount == 0:
#             return jsonify({"error": "Score not found!"}), 404
#         return jsonify(data), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_scores_by_field_name_and_date')
# def get_scores_by_field_name():
#     try:
#         con = connection()
#         cursor = con.cursor()
#         query = 'SELECT * FROM [dbo].[scores] WHERE field = ? AND entered_date = ? ORDER BY entered_time DESC'
#         field = request.args.get("field")
#         entered_date = request.args.get("entered_date")
#         cursor.execute(query, (field, entered_date))
#
#         rows = cursor.fetchall()
#
#         result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_scores_by_date')
# def get_scores_by_date():
#     try:
#         con = connection()
#
#         cursor = con.cursor()
#         query = 'SELECT * FROM [dbo].[scores] WHERE entered_date = ? ORDER BY entered_time DESC'
#         value = request.args.get("entered_date")
#         cursor.execute(query, value)
#
#         rows = cursor.fetchall()
#
#         result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/delete_score', methods=['DELETE'])
# def delete_score():
#     score_id = request.args.get("score_id")
#
#     score_id = int(score_id)
#     try:
#         con = connection()
#
#         cursor = con.cursor()
#         query = 'DELETE FROM [dbo].[scores] WHERE score_id = ?'
#         cursor.execute(query, score_id)
#
#         con.commit()
#
#         message = "The score has been deleted successfully!"
#         if cursor.rowcount == 0:
#             return jsonify({"error": "Score not found!"}), 404
#         con.close()
#         return jsonify(message), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/update_score', methods=['PATCH'])
# def update_score():
#     try:
#         con = connection()
#
#         score_id = request.args.get('score_id')
#
#         data = request.get_json()
#
#         score_id = int(score_id)
#
#         update_columns = []
#         params = []
#
#         if 'score_a' in data:
#             update_columns.append('score_a = ?')
#             params.append(data['score_a'])
#         if 'score_b' in data:
#             update_columns.append('score_b = ?')
#             params.append(data['score_b'])
#         if 'entered_date' in data:
#             update_columns.append('entered_date = ?')
#             params.append(data['entered_date'])
#         if 'entered_time' in data:
#             update_columns.append('entered_time = ?')
#             params.append(data['entered_time'])
#
#         if not update_columns:
#             return jsonify({'error': 'No valid fields provided'}), 400
#
#         sql_query = f"""
#             UPDATE [dbo].[scores]
#             SET {', '.join(update_columns)}
#             WHERE score_id = ?
#         """
#         params.append(score_id)
#         cursor = con.cursor()
#         cursor.execute(sql_query, *params)
#         con.commit()
#
#         con.close()
#         if cursor.rowcount == 0:
#             return jsonify({'error': 'Score not found'}), 404
#         return jsonify({'message': 'Score updated successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
#
# @app.route('/add_game', methods=['POST'])
# def add_game():
#     if request.method == 'POST':
#         try:
#             con = connection()
#
#             data = request.get_json()
#
#             cursor = con.cursor()
#
#             insert_query = (
#                 "INSERT INTO [dbo].[games] (date, field, team_1, team_2, team_3)"
#                 " VALUES (?, ?, ?, ?, ?)")
#
#             cursor.execute(insert_query, (data['date'], data['field'], data['team_1'], data['team_2'], data['team_3']))
#
#             con.commit()
#             cursor.close()
#
#             response = {"message": "Data inserted successfully"}
#             return jsonify(response), 200
#
#         except Exception as e:
#             return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_games_dates')
# def get_games_dates():
#     try:
#         con = connection()
#         cursor = con.cursor()
#         query = ('SELECT * FROM '
#                  '(SELECT DISTINCT date FROM [dbo].[games])'
#                  ' AS subquery'
#                  ' ORDER BY date;')
#
#         cursor.execute(query)
#
#         rows = cursor.fetchall()
#
#         result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/get_games_statistics_by_team_and_date')
# def get_games_statistics_by_team_and_date():
#     try:
#         con = connection()
#         cursor = con.cursor()
#         query = ('SELECT '
#                  'Q1.team_1,'
#                  ' Q1.team_2,'
#                  ' Q1.team_3,'
#                  'CASE '
#                  'WHEN '
#                  'Q1.team_1 = Q2.team_a THEN Q2.score_a '
#                  'WHEN Q1.team_1 = Q2.team_b THEN Q2.score_b '
#                  'ELSE NULL '
#                  'END AS team_1_score,'
#                  'CASE WHEN Q1.team_2 = Q2.team_a THEN Q2.score_a'
#                  ' WHEN Q1.team_2 = Q2.team_b THEN Q2.score_b'
#                  ' ELSE NULL END AS team_2_score,'
#                  ' CASE '
#                  'WHEN '
#                  'Q1.team_3 = Q2.team_a THEN Q2.score_a'
#                  ' WHEN Q1.team_3 = Q2.team_b THEN Q2.score_b'
#                  ' ELSE NULL '
#                  ' END AS team_3_score '
#                  'FROM [dbo].[games] AS Q1'
#                  ' JOIN [dbo].[scores] AS Q2 ON Q1.field = Q2.field AND Q2.entered_date = Q1.date '
#                  'WHERE Q1.date = ? AND Q2.field = ?')
#
#         entered_date = request.args.get("entered_date")
#         field = request.args.get("field")
#
#         cursor.execute(query, (entered_date, field))
#
#         rows = cursor.fetchall()
#
#         result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
#         con.close()
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
#
# @app.route('/read_sheet')
# def index():
#     spreadsheet_id = '18XJbsh2uWjwSd2JfPV9HcWgzJBL3jLyJi09l4jthkeA'
#     sheets = service.spreadsheets()
#     result = sheets.get(spreadsheetId=spreadsheet_id).execute()
#     cell_date = result.get("sheets")
#
#     for row in cell_date:
#         for column in row:
#             print(column)
#         print(row)
#     return jsonify(cell_date)
#
#
# @app.route('/create_user', methods=['POST'])
# def create_user():
#     if request.method == 'POST':
#         try:
#             con = connection()
#
#             data = request.get_json()
#
#             cursor = con.cursor()
#             insert_query = "INSERT INTO [dbo].[user] (user_id, email, name, password) VALUES (?, ?, ?, ?)"
#             cursor.execute(insert_query, (
#                 data['user_id'], data['email'], data['name'], data['password']))
#
#             con.commit()
#             cursor.close()
#
#             response = {"message": "Data inserted successfully"}
#             return jsonify(response), 200
#
#         except Exception as e:
#             return jsonify({"error": str(e)}), 400
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hellow_world():
    return "Hello World!"


if __name__ == '__main__':
    app.run(debug=True)
   