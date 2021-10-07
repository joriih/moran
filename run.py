# -*-coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, redirect, url_for, jsonify, app, send_file
from flask.helpers import url_for
from flask_cors import CORS
from sqlalchemy import create_engine
from werkzeug.utils import redirect
from werkzeug.wrappers import response
import time
import json

from driq import *
from rpa import *
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = '1a2b3c4d5e'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_pyfile('config.py')
database = create_engine(app.config['DB_URL'], encoding = 'utf-8')
app.database = database

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/request_history")
def request_history():
    return render_template('request_history.html')
@app.route("/up")
def up():
    return render_template('up.html')
@app.route("/bye")
def bye():
    return render_template('bye.html')
@app.route("/register_page")
def register_page():
    return render_template('register_page.html')
@app.route("/login_page")
def login_page():
    return render_template('login_page.html')
@app.route("/history")
def history():
    return render_template('history.html')
@app.route("/request_said", methods = ['POST'])
def request_said():
    if request.method == 'POST':
        req = request.get_json()
        sa_type = req['sa_type']
        num = req['said']
        service_type = req['service_type']
        region = req['region']
        now = time.localtime()
        now_time = "%02d/%02d %02d:%02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        sql = "INSERT INTO driq_request (id, date_, request_type, num, service_type, region, rpa_check) " \
              "VALUES (%s,%s,%s,%s,%s,%s,'N')"
        app.database.execute(sql, id, now_time, sa_type, num, service_type, region)
        sql2 = "SELECT count(*) FROM `driq_request` WHERE date_ <= %s AND rpa_check = 'N' ORDER BY date_"
        rows = app.database.execute(sql2, now_time).fetchone()[0]
        return json.dumps(rows)

@app.route("/request_bye", methods = ['POST'])
def request_bye():
    if request.method == 'POST':
        now = time.localtime()
        now_time = "%02d/%02d %02d:%02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        req = request.get_json()
        sa_type = req['sa_type']
        num = req['said']
        service_type = req['service_type']
        items = req['items']
        other = req['other']

        care_type = "해지징후"
        
        if len(items) == 3:
            option = "속도+품질"
        else :
            if items[0] == "quality":
                option = "품질"
            else :
                option = "속도"

        html = """\
        <html>
            <head></head>
            <bodY>
                <h6> <strong>{}</strong> 고객의 <strong>{}</strong> 케어 요청  </h6>
                <p> 요청 사유 : <strong> {} </strong> 의 <strong> {} </strong> 문제 </p>
                <p> 특이 사항 : {} </p>
                <p> 회선 정보 </p>
                <ul> 
                    <li> 요청 시간 : {} </li>
                    <li> 번호 타입 : {} </li>
                    <li> 서비스 유형 : {} </li>
                </ul>
            </body>
        </html>
        """.format(num, care_type, service_type, option, other, now_time, sa_type, service_type)
        
        print(html)
        # server = smtplib.SMTP('smtp.gmail.com', 587, timeout=120)
        # server.ehlo()
        # server.login('giga.service.checker@gmail.com', 'nam1234!')

        # sender = 'giga.service.checker@gmail.com'
        # to = ['heeyeon.jo@kt.com'] # 추후 변경 예정
        # msg = MIMEBase('multipart', 'mixed')
        # cont = MIMEText(html, 'html', 'utf-8')
        # msg['Subject'] = '[기가서비스체커] 고객 케어 요청'
        # msg['From'] = sender
        # msg['To'] = ','.join(to)
        # msg.attach(cont)

        # server.sendmail(sender, msg['To'], msg.as_string().encode("UTF"))
        # server.quit()

        return "complete"

@app.route("/request_up", methods = ['POST'])
def request_up():
    if request.method == 'POST':
        now = time.localtime()
        now_time = "%02d/%02d %02d:%02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        req = request.get_json()
        sa_type = req['sa_type']
        num = req['said']
        service_type = req['service_type']
        items = req['items']
        other = req['other']

        care_type = "업셀링"
        
        if len(items) == 3:
            option = "속도+품질"
        else :
            if items[0] == "quality":
                option = "품질"
            else :
                option = "속도"

        html = """\
        <html>
            <head></head>
            <bodY>
                <h6> <strong>{}</strong> 고객의 <strong>{}</strong> 케어 요청  </h6>
                <p> 요청 사유 : <strong> {} </strong> 의 <strong> {} </strong> 문제 </p>
                <p> 특이 사항 : {} </p>
                <p> 회선 정보 </p>
                <ul> 
                    <li> 요청 시간 : {} </li>
                    <li> 번호 타입 : {} </li>
                    <li> 서비스 유형 : {} </li>
                </ul>
            </body>
        </html>
        """.format(num, care_type, service_type, option, other, now_time, sa_type, service_type)
        print(html)
                # server = smtplib.SMTP('smtp.gmail.com', 587, timeout=120)
        # server.ehlo()
        # server.login('giga.service.checker@gmail.com', 'nam1234!')

        # sender = 'giga.service.checker@gmail.com'
        # to = ['heeyeon.jo@kt.com'] # 추후 변경 예정
        # msg = MIMEBase('multipart', 'mixed')
        # cont = MIMEText(html, 'html', 'utf-8')
        # msg['Subject'] = '[기가서비스체커] 고객 케어 요청'
        # msg['From'] = sender
        # msg['To'] = ','.join(to)
        # msg.attach(cont)

        # server.sendmail(sender, msg['To'], msg.as_string().encode("UTF"))
        # server.quit()

        return "complete"

# 개인이 요청한 이력보기
@app.route('/only_history', methods=['POST'])
def only_history():
    sql2 = "SELECT date_, num, service_type, region FROM driq_request WHERE rpa_check = 'YY' ORDER BY date_ DESC"
    rows = app.database.execute(sql2).fetchall()
    result = [dict(row) for row in rows] 
    print(result)
    return json.dumps(result)

# 요청이력에서 결과 확인 시 modal 창 출력
@app.route('/request_result', methods=['POST'])
def request_result():
    
    req = request.get_json()
    clicked_id = req['clicked_id']
    
    if not True in [badchar in clicked_id for badchar in "\n'\""]:
        date_ = clicked_id.split(",")[0]
        num = clicked_id.split(",")[1]

        # sql2 = "SELECT real_hybrid, date_, num FROM driq_result WHERE id = '{}' AND date_ = '{}' AND num = '{}'".format(id, date_, num)
        sql = "SELECT real_hybrid, date_, num FROM driq_result WHERE date_ = %s AND num = %s"
        rows = app.database.execute(sql, date_, num).fetchall()
        print(rows)
        if rows[0][0] == "Real":
            # sql3 = "SELECT * FROM driq_result_app_real WHERE id = '{}' AND date_ = '{}' AND num = '{}'".format(id, date_, num)
            sql2 = "SELECT * FROM driq_result_app_real WHERE date_ = %s AND num = %s"
            rows2 = app.database.execute(sql2, date_, num).fetchall()

            trestdb_sql = "SELECT * FROM trest WHERE num Like \'%s%%\'" %(num[:8])
            trestdb_rows = app.database.execute(text(trestdb_sql)).fetchall()
            
            if trestdb_rows == []:
                trestdb_rows = ["nothing"]
            result = rows2
            result1 = trestdb_rows

        elif rows[0][0] == "Hybrid":
            # sql3 = "SELECT * FROM driq_result_app_hybrid WHERE id = '{}' AND date_ = '{}' AND num = '{}'".format(id, date_,num)
            sql2 = "SELECT * FROM driq_result_app_hybrid WHERE date_ = %s AND num = %s"
            rows2 = app.database.execute(sql2, date_, num).fetchall()

            trestdb_sql = "SELECT * FROM trest WHERE num Like \'%s%%\'" %(num[:8])
            trestdb_rows = app.database.execute(text(trestdb_sql)).fetchall()
            if trestdb_rows == [] :
                trestdb_rows = ["nothing"]
            
            result = rows2
            result1 = trestdb_rows

        elif rows[0][0] == "no":
            rows2 = ["nothing"]
            trestdb_sql = "SELECT * FROM trest WHERE num Like \'%s%%\'" %(num[:8])
            trestdb_rows = app.database.execute(text(trestdb_sql)).fetchall()
            if trestdb_rows == [] :
                trestdb_rows = ["nothing"]
            result = rows2
            result1 = trestdb_rows
        else :
            result = ["nothing"]
            result1 = ["nothing"]

        if result[0] == "nothing" and result1[0] == "nothing":
            return jsonify(result[0], result1[0])
        elif result[0] == "nothing":
            rows2 = [dict(row) for row in result1]
            return jsonify(result, rows2)
        elif result1[0] == "nothing":
            rows = [dict(row) for row in result]
            return jsonify(rows, result1)
        else:
            rows = [dict(row) for row in result]
            rows2 = [dict(row) for row in result1]
            return jsonify(rows, rows2)


# 알람용 함수
@app.route('/toast', methods=['POST'])
def toast():
    result = driq_toast(request.get_json(), app)
    return result

# rpa 관련 페이지
@app.route('/rpa_sql', methods=['GET', 'POST'])
def rpa_sql():
    return render_template('rpa_sql.html') 

# rpa 페이지에서 진단 요청 목록 확인
@app.route('/rpa_select', methods=['GET', 'POST'])
def rpa_select():
    result = driq_rpa_select(app)
    return render_template('rpa_select.html', rows=result)

# rpa 처리 후 sql 쿼리 실행
@app.route('/rpa_inup', methods=['POST'])
def rpa_inup():
    request_update = request.form['request_update']
    real_insert = request.form['real_insert']
    hybrid_insert = request.form['hybrid_insert']
    real_hybrid_result = request.form['real_hybrid_result']

    if not True in [badchar in request_update or badchar in real_insert or badchar in hybrid_insert or badchar in real_hybrid_result for badchar in "\n'\""]:
        sql = "UPDATE driq_request SET rpa_check = %s, num = %s WHERE id = %s and date_ = %s and num = %s"
        request_update_list = request_update.split(",")
        app.database.execute(sql, request_update_list[1], request_update_list[2], request_update_list[3], request_update_list[4], request_update_list[5])
        print(sql %(request_update_list[1], request_update_list[2], request_update_list[3], request_update_list[4], request_update_list[5]))
        sql2 = "INSERT INTO driq_result VALUES (%s, %s, %s, %s)"
        real_hybrid_result_list = real_hybrid_result.split(",")
        app.database.execute(sql2, real_hybrid_result_list[1], real_hybrid_result_list[2], real_hybrid_result_list[3], real_hybrid_result_list[4])
        print(sql2 %(real_hybrid_result_list[1], real_hybrid_result_list[2], real_hybrid_result_list[3], real_hybrid_result_list[4]))
    if real_insert =="" and hybrid_insert != "":
        sql3 = "INSERT INTO driq_result_app_hybrid VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s)"
        h = hybrid_insert.split(",")
        app.database.execute(sql3, h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[8],h[9],h[10],h[11],h[12],h[13],h[14],h[15],h[16],h[17],h[18],h[19],h[20],h[21],h[22],h[23],h[24] )
        
        print(sql3 %(h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[8],h[9],h[10],h[11],h[12],h[13],h[14],h[15],h[16],h[17],h[18],h[19],h[20],h[21],h[22],h[23],h[24]))
    elif hybrid_insert =="" and real_insert != "":
        sql3 = "INSERT INTO driq_result_app_real VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s)"
        r = real_insert.split(",")
        app.database.execute(sql3, r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12],r[13],r[14],r[15],r[16],r[17],r[18],r[19],r[20],r[21],r[22],r[23],r[24],r[25])
        
        print(sql3%( r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12],r[13],r[14],r[15],r[16],r[17],r[18],r[19],r[20],r[21],r[22],r[23],r[24],r[25]))
    elif hybrid_insert == "" and real_insert == "":
        pass
    return jsonify("ghdlt")


# Flask 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
    # app.run(host='0.0.0.0',port=8000,debug=True)