# -*-coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, redirect, url_for, jsonify, app, send_file
from flask.helpers import url_for
from flask_cors import CORS
from sqlalchemy import create_engine
from werkzeug.utils import redirect
from werkzeug.wrappers import response
from ldap import *
from employee import *
import pymysql
import sqlite3
import pandas as pd
from ldap import *
from driq import *
from rpa import *
import datetime
import flask
from datetime import timedelta
from ai import *

pd.options.display.float_format = '{:.0f}'.format
app = Flask(__name__)

app.secret_key = '1a2b3c4d5e'



@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


@app.route("/", methods = ['GET'])
def index():
    if 'loggedin' in session:
        return render_template('ai_index.html', username = session['username'])
    
    # return redirect(url_for("login"))
    return redirect("https://gsc.appdu.kt.co.kr/login")


@app.after_request
def add_header(response):
    response.headers['Server'] = '*'
    
    if 'Allow' in response.headers:
        response.headers['Allow'] = '*'

    return response


@app.errorhandler(400)
def bad_request(error):
    return render_template('404.html'), 400



@app.errorhandler(403)
def forbidden(error):
    return render_template('404.html'), 403
    
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
    
    
@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('404.html'), 405
    
    
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('404.html'), 500


# 로그인 페이지 출력
@app.route('/login', methods = ['GET'])
def login():
    session.pop('username',None)
    session.pop('loggedin', None)
    return render_template(
        'login.html'
    )

# 로그아웃 버튼 클릭 시
@app.route('/logout',methods=['GET'])
def logout():
    session.pop('username',None)
    session.pop('loggedin', None)
    return redirect('/')

# captchaKey, image return
@app.route('/captcha', methods = ['GET'])
def captcha():
    if request.method == 'GET':

        response = getcaptcha()
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# captcha 로그인 시도 및 토큰 발행
@app.route('/signin2', methods = ['POST'])
def signin2():
    if request.method == 'POST':

        response = signinwithcaptcha(request.get_json())
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# LDAP 로그인 시도
@app.route('/signin', methods = ['POST'])
def signin():
    if request.method == 'POST':
        # json.dumps(dict): dict('') -> json("")
        # json.loads(json): json("") -> dict('')
        
        # request.get_json(): dict object
        response = signinwithotp(request.get_json())
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# OTP 확인 및 토큰 발행
@app.route('/verify', methods = ['POST'])
def verify():
    if request.method == 'POST':
        response = verifywithotp(request.get_json())
        if (response['returnCode']) == "OK":
            session['loggedin'] = True
            session['username'] = response['username']
            redirect(url_for("index"))
        else:
            redirect(url_for("login"))
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# 로그아웃
@app.route('/signout', methods = ['POST'])
def signout():
    if request.method == 'POST':
        response = dosignout(request.headers, app)
        return response
    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# 토큰 연장
@app.route('/generateNewToken', methods = ['POST'])
def genNewToken():
    if request.method == 'POST':
        
        response = generateNewToken()
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# 토큰 연장
@app.route('/generateNewToken2', methods = ['POST'])
def genNewToken2():
    if request.method == 'POST':
        
        response = generateNewToken2(request)
        return response


# CRUD - Read
@app.route('/employee/getEmployees', methods = ['GET', 'POST'])
def getEmployees():
    if request.method in ['GET', 'POST']:
        
        response = userlist(request.headers, app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# CRUD - Create
@app.route('/employee/addNewEmployee', methods = ['POST'])
def addNewEmployee():
    if request.method == 'POST':
        
        response = add_user(request.headers, request.get_json(), app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# CRUD - Update
@app.route('/employee/updateEmployeeInfo', methods = ['POST'])
def updateEmployeeInfo():
    if request.method == 'POST':
        
        response = update_user(request.headers, request.get_json(), app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405


# CRUD - Delete
@app.route('/employee/deleteEmployee', methods = ['POST'])
def deleteEmployee():
    if request.method == 'POST':
        
        response = delete_user(request.headers, request.get_json(), app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405

# AppDu health_check 함수 절대 지우지 말것 
# health_check
@app.route('/health_check', methods = ['GET'])
def health_check():
    if request.method == 'GET':

        return json.dumps({'returnCode': 'OK'})

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}), 405

# 진단 요청
@app.route('/request_history', methods=['POST'])
def request_history():
    result = driq_request_history(request.headers, request.get_json(), app)
    return result

# 개인이 요청한 이력보기
@app.route('/only_history', methods=['POST'])
def only_history():
    result = driq_only_history(request.headers, request.get_json(), app)
    return result

# 헬프 데스크에서 볼 수 있는 모든 이력
@app.route('/all_history', methods=['POST'])
def all_history():
    result = driq_all_history(app)
    return result

# 요청이력에서 결과 확인 시 modal 창 출력
@app.route('/request_result', methods=['POST'])
def request_result():
    result = driq_request_result(request.get_json(), app)
    print(result)
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

# 다량회선 처리를 위한 진단 요청 목록 확인
@app.route('/rpa_select_multi', methods=['GET', 'POST'])
def rpa_select_multi():
    result = driq_rpa_select_multi(app)
    return render_template('rpa_select_multi.html', rows=result)  #


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

# 알람용 함수
@app.route('/toast', methods=['POST'])
def toast():
    result = driq_toast(request.get_json(), app)
    return result

# 텍스트 database에 업로드
@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if 'loggedin' in session:
        if request.method == 'POST':
            id = session['username']
            f = request.form['memo']
            driq_upload_file(id, f, app)
            return render_template('confirm.html')
        else:
            return render_template('confirm.html')
    return redirect(url_for('login'))

# 텍스트 database에 업로드
@app.route('/uploader2', methods=['GET', 'POST'])
def upload_file2():
    if 'loggedin' in session:
        if request.method == 'POST':
            id = session['username']
            return render_template('confirm2.html')
        else:
            return render_template('confirm2.html')
    return redirect(url_for('login'))

# 다량회선 진행상황 확인
@app.route('/uploader/progress', methods = ['GET', 'POST'])
def progress():
    id = session['username']
    result = driq_progress(id, app)
    return result

# 다량회선 진행상황 확인
@app.route('/uploader2/progress_all', methods = ['GET', 'POST'])
def progress_all():
    id = session['username']
    result = driq_progress_all(id, app)
    return result

@app.route('/downloadtest', methods=['GET', 'POST'])
def progress3():
    id = session['username']
    return send_file(id + '.xlsx',as_attachment=True)    

@app.route('/uploader/excel_download', methods = ['GET', 'POST'])
def progress2():
    id = session['username']
    date_ = request.form['date_']
    result = driq_progress2(id, date_, app)
    return result

@app.route('/uploader2/excel_download', methods = ['GET', 'POST'])
def progress2_2():
    id = session['username']
    date_ = request.form['date_']
    result = driq_progress2_2(id, date_, app)
    return result

# 업셀링/해지징후 버튼 클릭 시 메일 전송
@app.route('/customer_re_care', methods=['POST'])
def customer_re_care():
    result = driq_customer_re_care(request.get_json(), app)
    return result

@app.route('/customer_hy_care', methods=['POST'])
def customer_hy_care():
    result = driq_customer_re_care(request.get_json(), app)
    return result

@app.route('/customer_no_care', methods=['POST'])
def customer_no_care():
    result = driq_customer_re_care(request.get_json(), app)
    return result

@app.route('/rpa_select_test')
def rpa_select_test():
    return render_template('rpa_sql_copy.html')

@app.route('/excel_upload_test', methods=['GET', 'POST'])
def excel_upload_test():
    raw_data = request.files['file']
    print(raw_data)
    test = pd.read_excel(raw_data)
    print(test)
    return "test"

@app.route('/ai_request', methods = ['POST'])
def ai_request():
    
    req = request.get_json()
    select_voc_1 = req['select_voc_1']
    select_voc_2 = req['select_voc_2']
    select_voc_3 = req['select_voc_3']
    select_voc_fac = req['select_voc_fac']
    # select_voc_cau = req['select_voc_cau']
    # select_pa_model = req['select_pa_model']
    # select_pa_make = req['select_pa_make']
    # select_pa_home_model = req['select_pa_home_model']
    # select_pa_home_make = req['select_pa_home_make']
    data = [select_voc_1, select_voc_2, select_voc_3, select_voc_fac] #, select_voc_cau, select_pa_model, select_pa_make, select_pa_home_model, select_pa_home_make]
    result = ai(select_voc_1, select_voc_2, select_voc_3, select_voc_fac) #, select_voc_cau, select_pa_model, select_pa_make, select_pa_home_model, select_pa_home_make)
    
    return jsonify(result)

# Flask 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0',port=8000,debug=True)

