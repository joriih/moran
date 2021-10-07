from flask import json, jsonify
import time
import sqlite3
from openpyxl import Workbook
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from email.message import EmailMessage
import pymysql
from sqlalchemy import create_engine, text

def driq_request_history(hdr, req, app):
    id = req['username']
    sa_type = req['sa_type']
    num = req['num']
    service_type = req['service_type']
    region = req['region']


    if not True in [badchar in id or badchar in sa_type or badchar in num or badchar in service_type or badchar in region for badchar in "\n'\""]:
    
        now = time.localtime()
        now_time = "%02d/%02d %02d:%02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

        sql = "INSERT INTO driq_request (id, date_, request_type, num, service_type, region, rpa_check) " \
            "VALUES (%s,%s,%s,%s,%s,%s,'N')"

        app.database.execute(sql, id, now_time, sa_type, num, service_type, region)

        sql2 = "SELECT count(*) FROM `driq_request` WHERE date_ <= %s AND rpa_check = 'N' ORDER BY date_"
        rows = app.database.execute(sql2, now_time).fetchone()[0]

        # sql3 = "SELECT date_, num, service_type, region FROM driq_request WHERE id = %s AND rpa_check = 'Y' ORDER BY date_ LIMIT 10"
        # rows2 = app.database.execute(sql2, id).fetchall()
        return json.dumps(rows)


def driq_only_history(hdr, req, app):
    id = req['id']
  
    
    if not True in [badchar in id for badchar in "\n'\""]:
        sql2 = "SELECT date_, num, service_type, region FROM driq_request WHERE id = %s AND rpa_check = 'YY' ORDER BY date_ DESC"
        rows = app.database.execute(sql2, id).fetchall()
        result = [dict(row) for row in rows] 
        return json.dumps(result) 
            
    
        
def driq_all_history(app):
    sql = "SELECT id, date_, num, service_type, region FROM driq_request WHERE rpa_check = 'YY' or rpa_check = 'Y' ORDER BY date_ DESC"
    rows = app.database.execute(sql).fetchall()
    result = [dict(row) for row in rows] 
    return json.dumps(result) 

def driq_request_result(req, app):
    clicked_id = req['clicked_id']
    
    if not True in [badchar in clicked_id for badchar in "\n'\""]:
        date_ = clicked_id.split(",")[0]
        num = clicked_id.split(",")[1]

        # sql2 = "SELECT real_hybrid, date_, num FROM driq_result WHERE id = '{}' AND date_ = '{}' AND num = '{}'".format(id, date_, num)
        sql = "SELECT real_hybrid, date_, num FROM driq_result WHERE date_ = %s AND num = %s"
        rows = app.database.execute(sql, date_, num).fetchall()
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

def driq_toast(req, app):
    id = req['username']
        
    if not True in [badchar in id for badchar in "\n'\""]:
        sql = '''
            SELECT count(*) FROM driq_request
            WHERE rpa_check = 'Y' and id = %s 
            order by date_ desc
            '''
        
        rows = app.database.execute(sql, id).fetchone()[0]
        
        sql2 = '''
            UPDATE driq_request 
            SET rpa_check = 'YY' 
            WHERE id = %s and rpa_check='Y'
            '''
            
        app.database.execute(sql2, id)
        return json.dumps(rows)

def driq_upload_file(id, f, app):
    if not True in [badchar in id for badchar in "\n'\""]:
        f = f.split("\n")
        now = time.localtime()
        now_time = "%02d/%02d %02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
        for i in range(1, len(f)-1):
            sql = "INSERT INTO driq_request (id, date_, request_type, num, service_type, region, rpa_check) " \
                                    "VALUES (%s,%s,'SAID',%s,'인터넷',%s,'E')"
            app.database.execute(sql, id, now_time, f[i].split('\t')[13], f[i].split('\t')[8])

            sql2 = "INSERT INTO driq_multi_base values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            
            app.database.execute(sql2, id, now_time,f[i].split("\t")[0],f[i].split("\t")[1],f[i].split("\t")[2],f[i].split("\t")[3],f[i].split("\t")[4],f[i].split("\t")[5],
                                f[i].split("\t")[6],f[i].split("\t")[7],f[i].split("\t")[8],f[i].split("\t")[9],f[i].split("\t")[10],f[i].split("\t")[11],f[i].split("\t")[12],
                                f[i].split("\t")[13],f[i].split("\t")[14],f[i].split("\t")[15],f[i].split("\t")[16],f[i].split("\t")[17],f[i].split("\t")[18],f[i].split("\t")[19],
                                f[i].split("\t")[20],f[i].split("\t")[21],"")
        sql3 = "INSERT INTO excel (id, date_, cnt) VALUES (%s, %s, %s)"
        app.database.execute(sql3, id, now_time, len(f)-2)

def driq_progress(id, app):
    if not True in [badchar in id for badchar in "\n'\""]:
        sql = "SELECT cnt, date_ FROM excel WHERE id = %s order by date_ desc"
        rows = app.database.execute(sql, id).fetchone()

        all = rows[0]
        date_ = rows[1]

        sql2 = "SELECT count(*) FROM driq_request WHERE rpa_check = 'EY' and id = %s and date_ = %s order by date_ desc"
        rows2 = app.database.execute(sql2, id, date_).fetchone()
        now = rows2[0]
        percent = int(now) / int(all) * 100

        sql3 = "SELECT request_type, num, service_type, region, rpa_check, date_ FROM driq_request WHERE id = %s and date_ = %s order by date_ desc"
        
        result = app.database.execute(sql3, id, date_).fetchall()
        rows = [dict(row) for row in result]
        return jsonify(now, all, percent, rows)

def driq_progress_all(id, app):
    if not True in [badchar in id for badchar in "\n'\""]:
        # sql = "SELECT cnt, date_ FROM excel WHERE id = %s order by date_ desc"
        # rows = app.database.execute(sql, id).fetchone()

        # all = rows[0]
        # date_ = rows[1]

        # sql2 = "SELECT count(*) FROM driq_request WHERE rpa_check = 'EY' and id = %s and date_ = %s order by date_ desc"
        # rows2 = app.database.execute(sql2, id, date_).fetchone()
        # now = rows2[0]
        # percent = int(now) / int(all) * 100
        # percent = 100
        sql3 = "SELECT request_type, num, service_type, region, rpa_check, date_ FROM driq_request WHERE id = %s order by date_ desc"
        
        result = app.database.execute(sql3, id).fetchall()
        rows = [dict(row) for row in result]
        return jsonify(100, 100, 100, rows)

def driq_progress2(id, date_, app):
    
    if not True in [badchar in date_ for badchar in "\n'\""]:
        date_test = '%' + date_[0:5] + '%'
        # sql = "SELECT a.*, b.control, b.profile, b.oplev_link, b.real_hybrid FROM driq_multi_base a, (select id, date_, said, control, PROFILE, real_hybrid, optical_level AS oplev_link from driq_result_app_real UNION SELECT id, date_, said, control, PROFILE, " \
        #        "real_hybrid, link_speed FROM driq_result_app_hybrid) b WHERE a.id = b.id AND a.date_ = b.date_ AND a.said = b.said AND a.id = %s AND a.date_ = %s"
        sql = "SELECT b.*, a.상품명, a.다운로드속도, a.업로드속도 FROM driq_view b LEFT JOIN driq_q_check a ON b.said = a.said WHERE b.id = %s AND b.date_ like %s"
        rows = app.database.execute(sql, id, date_test).fetchall()
        wb = Workbook()
        ws = wb.active
        ws.append(('요청id', '요청일자', '일자','시설수용조직2레벨','','시설수용조직3레벨','','시설수용조직4레벨','','시설수용조직','','분석상품레벨3','분석상품레벨4', '가설오더유형',
                   '명령번호', '서비스계약','KT사업용구분', 'WM작업자팀','WM업체', 'WM작업자', '', '출동무출동여부', '매트릭', '가설건수', '판정', '제어서버', '프로파일', '광레벨/링크스피드', '타입'))
        for row in rows:
            ws.append(list(row))


        sql2 = "SELECT b.*, '', '', '', '', a.상품명, a.다운로드속도, a.업로드속도 FROM driq_view_2 b LEFT JOIN driq_q_check a ON a.said = b.said WHERE b.id = %s AND b.date_ like %s"
        rows = app.database.execute(sql2, id, date_test).fetchall()

        for row in rows:
            ws.append(list(row))

        sql3 = "SELECT b.*, '', '', '', '', a.상품명, a.다운로드속도, a.업로드속도 FROM driq_multi_base b LEFT JOIN driq_q_check a ON b.said = a.said WHERE b.ok_notok = '미조회' AND b.id = %s AND b.date_ like %s"
        rows = app.database.execute(sql3, id, date_test).fetchall()

        for row in rows:
            ws.append(list(row))

        wb.save(id + '.xlsx')
        return jsonify('comp')

def driq_progress2_2(id, date_, app):
    
    if not True in [badchar in date_ for badchar in "\n'\""]:
        # sql = "SELECT a.*, b.control, b.profile, b.oplev_link, b.real_hybrid FROM driq_multi_base a, (select id, date_, said, control, PROFILE, real_hybrid, optical_level AS oplev_link from driq_result_app_real UNION SELECT id, date_, said, control, PROFILE, " \
        #        "real_hybrid, link_speed FROM driq_result_app_hybrid) b WHERE a.id = b.id AND a.date_ = b.date_ AND a.said = b.said AND a.id = %s AND a.date_ = %s"
        sql = "SELECT b.*, a.상품명, a.다운로드속도, a.업로드속도 FROM driq_view b LEFT JOIN driq_q_check a ON b.said = a.said WHERE b.id = %s"
        rows = app.database.execute(sql, id).fetchall()
        wb = Workbook()
        ws = wb.active
        ws.append(('요청id', '요청일자', '일자','시설수용조직2레벨','','시설수용조직3레벨','','시설수용조직4레벨','','시설수용조직','','분석상품레벨3','분석상품레벨4', '가설오더유형',
                   '명령번호', '서비스계약','KT사업용구분', 'WM작업자팀','WM업체', 'WM작업자', '', '출동무출동여부', '매트릭', '가설건수', '판정', '제어서버', '프로파일', '광레벨/링크스피드', '타입'))
        for row in rows:
            ws.append(list(row))


        sql2 = "SELECT b.*, '', '', '', '', a.상품명, a.다운로드속도, a.업로드속도 FROM driq_view_2 b LEFT JOIN driq_q_check a ON a.said = b.said WHERE b.id = %s"
        rows = app.database.execute(sql2, id).fetchall()

        for row in rows:
            ws.append(list(row))

        sql3 = "SELECT b.*, '', '', '', '', a.상품명, a.다운로드속도, a.업로드속도 FROM driq_multi_base b LEFT JOIN driq_q_check a ON b.said = a.said WHERE b.ok_notok = '미조회' AND b.id = %s"
        rows = app.database.execute(sql3, id).fetchall()

        for row in rows:
            ws.append(list(row))

        wb.save(id + '.xlsx')
        return jsonify('comp')

def driq_customer_re_care(req, app):
    id = req['username']
    date_ = req['id'].split(",")[0]
    num = req['id'].split(",")[1]
    care = req['care']
    care_type = req['care_type']
    service_type = req['service_type']
    care_option = req['care_option']
    
    if not True in [badchar in id or badchar in date_ or badchar in num or badchar in care or badchar in care_type or badchar in service_type or badchar in care_option for badchar in "\n'\""]:
        care_result = care_type + "/" + service_type + "/" + care_option + "/" + care
        sql = "INSERT INTO care (id, date_, num, care) " \
            "VALUES (%s,%s,%s,%s)"
        app.database.execute(sql, id, date_, num, care_result)

        sql2 = "SELECT * FROM driq_request WHERE id = %s AND date_ = %s"
        rows = app.database.execute(sql2, id, date_).fetchall()

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=120)
        server.ehlo()
        server.login('giga.service.checker@gmail.com', 'nam1234!')

        sender = 'giga.service.checker@gmail.com'
        to = ['GiGA-Doctor@kt.com'] # 추후 변경 예정

        msg = MIMEBase('multipart', 'mixed')
        html = """\
        <html>
            <head></head>
            <bodY>
                <p> {} : <strong>{}</strong> 고객의 <strong>{}</strong> 케어 요청  </p>
                <p> 요청 사유 : <strong> {} </strong> 의 <strong> {} </strong> 문제 </p>
                <p> 특이 사항 : {} </p>
                <p> 회선 정보 </p>
                <ul> 
                    <li> 요청 시간 : {} </li>
                    <li> 번호 타입 : {} </li>
                    <li> 서비스 유형 : {} </li>
                    <li> 국사 : {} </li>
                </ul>
            </body>
        </html>
        """.format(rows[0][0],rows[0][3], care_result.split('/')[0], care_result.split('/')[1], care_result.split('/')[2], care_result.split('/')[3], rows[0][1], rows[0][2], rows[0][4], rows[0][5])
        cont = MIMEText(html, 'html', 'utf-8')
        msg['Subject'] = '[기가서비스체커] 고객 케어 요청'
        msg['From'] = sender
        msg['To'] = ','.join(to)
        msg.attach(cont)

        server.sendmail(sender, msg['To'], msg.as_string().encode("UTF"))
        server.quit()

        return jsonify(rows)  