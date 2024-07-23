# from flask import jsonify
# from flask import request
#
#
# def validate_user(con):
#     try:
#         cursor = con.cursor()
#         query = 'SELECT * FROM users WHERE email = ? AND password = ?'
#         email = request.args.get("email")
#         password = request.args.get("password")
#         cursor.execute(query, (email, password))
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
