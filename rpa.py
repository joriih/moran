from flask import json, jsonify

def driq_rpa_select(app):
    sql = "select * from driq_request where rpa_check = 'N'"
    result = app.database.execute(sql).fetchall()
    rows = [dict(row) for row in result]
    return rows

def driq_rpa_select_multi(app):
    sql = "select * from driq_request where rpa_check='E'"
    result = app.database.execute(sql).fetchall()
    rows = [dict(row) for row in result]
    return rows


def driq_rpa_inup(request_update, real_insert, hybrid_insert, real_hybrid_result, app):
    if not True in [badchar in request_update or badchar in real_insert or badchar in hybrid_insert or badchar in real_hybrid_result for badchar in "\n'\""]:
        sql = "UPDATE driq_request SET rpa_check = %s, num = %s WHERE id = %s and date_ = %s and num = %s"
        request_update_list = request_update.split(",")
        app.database.execute(sql, request_update_list[1], request_update_list[2], request_update_list[3], request_update_list[4], request_update_list[5])
        
        sql2 = "INSERT INTO driq_result VALUES (%s, %s, %s, %s)"
        real_hybrid_result_list = real_hybrid_result.split(",")
        app.database.execute(sql2, real_hybrid_result_list[1], real_hybrid_result_list[2], real_hybrid_result_list[3], real_hybrid_result_list[4])
    
    if real_insert =="" and hybrid_insert != "":
        sql3 = "INSERT INTO driq_result_app_hybrid VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s)"
        h = hybrid_insert.split(",")
        app.database.execute(sql3, h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[8],h[9],h[10],h[11],h[12],h[13],h[14],h[15],h[16],h[17],h[18],h[19],h[20],h[21],h[22],h[23],h[24] )
    elif hybrid_insert =="" and real_insert != "":
        sql3 = "INSERT INTO driq_result_app_real VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s)"
        r = real_insert.split(",")
        app.database.execute(sql3, r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12],r[13],r[14],r[15],r[16],r[17],r[18],r[19],r[20],r[21],r[22],r[23],r[24],r[25])
    elif hybrid_insert == "" and real_insert == "":
        pass
    return jsonify("ghdlt")
