# -*-coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, redirect, url_for, jsonify, app, send_file
import time
app = Flask(__name__)


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
        req = request.get_json()
        sa_type = req['sa_type']
        num = req['said']
        service_type = req['service_type']
        items = req['items']
        other = req['other']
        print(items)
        return "complete"

@app.route("/request_up", methods = ['POST'])
def request_up():
    if request.method == 'POST':
        req = request.get_json()
        sa_type = req['sa_type']
        num = req['said']
        service_type = req['service_type']
        items = req['items']
        other = req['other']
        print(items)
        return "complete"
# Flask 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)
    # app.run(host='0.0.0.0',port=8000,debug=True)