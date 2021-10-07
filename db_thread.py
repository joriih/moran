import sqlite3

import datetime
import threading
import re
import pandas as pd
from threading import Thread, currentThread
import time
import pymysql

class Trigger(threading.Thread):
    def __init__(self, row, conn):
        super().__init__()
        self.row = row
        self.conn = pymysql.connect(host='210.121.218.5', user='zabbix', passwd='zabbix', port=3306, db='test', charset='euckr')
        self.curs = self.conn.cursor()

    def run(self):

        now = datetime.datetime.now()

        # nowDatetime = now.strftime('%Y-%m-%d %H:%M')
        tomorrow = now - datetime.timedelta(minutes=30)

        # pastDatetime = tomorrow.strftime('%Y-%m-%d %H:%M')
        pastDatetime = '2021-09-15 10:14'
        nowDatetime = '2021-10-07 16:30'
        if self.row[1][6] == "in":
            first = int(self.row[1][7])
            second = self.row[1][4]
            third = int(self.row[1][7])*0.7
        elif self.row[1][6] == "out":
            first = int(self.row[1][8])
            second = self.row[1][4]
            third = int(self.row[1][8])*0.7

        sql = 'SELECT itemid, FROM_UNIXTIME(clock) AS clock, VALUE, (value / {} * 100) as per  \
            FROM ZABBIXDB.history_uint \
            WHERE itemid = {} AND FROM_UNIXTIME(clock) >= "{}" AND FROM_UNIXTIME(clock) <= "{}" AND value >= {}'.format(first, second, pastDatetime, nowDatetime, third)
        # print(sql)
        self.curs.execute(sql)
        rows = self.curs.fetchall()
        if rows == ():
            pass
        else :
            for row in rows:
                print(row)
                timestamp = time.mktime(row[1].timetuple())
                sql = "INSERT INTO ZABBIXDB.alarm_b2b_test values({}, {}, {}, {})".format(row[0], int(timestamp), row[2], row[3])
                self.curs.execute(sql)
                self.conn.commit()
                sql = "select * from ZABBIXDB.alarm_b2b_test where itemid = {}".format(row[0])
                self.curs.execute(sql)
                rows = self.curs.fetchall()
                print(rows)

        now = datetime.datetime.now()
        print("last를 위한", now)

        self.curs.close()
        self.conn.close()

# print("main thread start")
if __name__ == '__main__':
    now = datetime.datetime.now()
    print(now)
    conn = pymysql.connect(host='210.121.218.5', user='zabbix', passwd='zabbix', port=3306, db='test', charset='euckr')
    curs = conn.cursor()
    sql = 'SELECT * FROM ZABBIXDB.new_db WHERE ingre != "" AND engre != ""'
    curs.execute(sql)
    rows = curs.fetchall()
    df = pd.DataFrame(rows)[20:100]
    # conn.close()

    for row in df.iterrows():
        # t = Trigger(row, conn)                # sub thread 생성
        # t.start()                       # sub thread의 run 메서드를 호출

        pastDatetime = '2021-09-15 10:14'
        nowDatetime = '2021-10-07 16:30'
        if row[1][6] == "in":
            first = int(row[1][7])
            second = row[1][4]
            third = int(row[1][7]) * 0.7
        elif row[1][6] == "out":
            first = int(row[1][8])
            second = row[1][4]
            third = int(row[1][8]) * 0.7
        print(second)
        sql = 'SELECT itemid, FROM_UNIXTIME(clock) AS clock, VALUE, (value / {} * 100) as per  \
                    FROM ZABBIXDB.history_uint \
                    WHERE itemid = {} AND FROM_UNIXTIME(clock) >= "{}" AND FROM_UNIXTIME(clock) <= "{}" AND value >= {}'.format(
            first, second, pastDatetime, nowDatetime, third)
        # print(sql)
        curs.execute(sql)
        rows = curs.fetchall()
        if rows == ():
            pass
        else:
            for row in rows:
                print(row)
                timestamp = time.mktime(row[1].timetuple())
                sql = "INSERT INTO ZABBIXDB.alarm_b2b_test values({}, {}, {}, {})".format(row[0], int(timestamp),
                                                                                          row[2], row[3])
                curs.execute(sql)
                conn.commit()
                # sql = "select * from ZABBIXDB.alarm_b2b_test where itemid = {}".format(row[0])
                # curs.execute(sql)
                # rows = curs.fetchall()
                # print(rows)

                now = datetime.datetime.now()
                print(now)
        # print("last를 위한", now)

        # curs.close()
    conn.close()
