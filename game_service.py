from flask import jsonify, request


def get_games_statistics_by_team_and_date(con):
    try:
        cursor = con.cursor()
        query = ('SELECT '
                 'Q1.team_1,'
                 ' Q1.team_2,'
                 ' Q1.team_3,'
                 'CASE '
                 'WHEN '
                 'Q1.team_1 = Q2.team_a THEN Q2.score_a '
                 'WHEN Q1.team_1 = Q2.team_b THEN Q2.score_b '
                 'ELSE NULL '
                 'END AS team_1_score,'
                 'CASE WHEN Q1.team_2 = Q2.team_a THEN Q2.score_a'
                 ' WHEN Q1.team_2 = Q2.team_b THEN Q2.score_b'
                 ' ELSE NULL END AS team_2_score,'
                 ' CASE '
                 'WHEN '
                 'Q1.team_3 = Q2.team_a THEN Q2.score_a'
                 ' WHEN Q1.team_3 = Q2.team_b THEN Q2.score_b'
                 ' ELSE NULL '
                 ' END AS team_3_score '
                 'FROM [dbo].[games] AS Q1'
                 ' JOIN [dbo].[scores] AS Q2 ON Q1.field = Q2.field AND Q2.entered_date = Q1.date '
                 'WHERE Q1.date = ? AND Q2.field = ?')

        entered_date = request.args.get("entered_date")
        field = request.args.get("field")

        cursor.execute(query, (entered_date, field))

        rows = cursor.fetchall()

        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        con.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
