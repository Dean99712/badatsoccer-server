import pyodbc
from flask import Flask, render_template, request, jsonify
from config import Config as cnf

app = Flask(__name__)

con = pyodbc.connect(
    f'DRIVER={cnf.Driver};SERVER={cnf.Server}, {cnf.Port};DATABASE={cnf.Database};Uid={cnf.Uid};Pwd={cnf.Pwd};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")


@app.route('/get')
def connection():
    cursor = con.cursor()
    cursor.execute(f'SELECT * FROM "user"')

    dataset = cursor.fetchall()
    print(dataset)

    return "Connection to database successful"


@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        try:

            data = request.get_json()

            cursor = con.cursor()
            insert_query = "INSERT INTO [user] (user_id, email, name, password) VALUES (?, ?, ?, ?)"
            cursor.execute(insert_query, (
                data['user_id'], data['email'], data['name'], data['password']))

            con.commit()
            cursor.close()

            response = {"message": "Data inserted successfully"}
            return jsonify(response), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run()
