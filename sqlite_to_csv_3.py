# -*- coding: UTF-8 -*-
"""
sqlite to csv for python3
"""
import sqlite3
import csv
from sqlite_read import find_firefox_cookies

import pandas.io.sql as sql
import pandas


def save_to_csv(csv_filename, basedomain):
    """sqlite数据库写入csv文件
    """
    sqlite_filename = find_firefox_cookies()
    con = sqlite3.connect(sqlite_filename)
    c = con.cursor()
    # c.execute("SELECT * FROM moz_cookies WHERE baseDomain={};".format(basedomain))    # format用法：对应"'webscraping.com'"
    c.execute("SELECT * FROM moz_cookies WHERE baseDomain='%s';" % basedomain)          # '%s'  用法：对应'webscraping.com'
    with open(csv_filename, 'w', encoding='gbk') as file:  # encoding='gbk': 防止中文乱码
        # for i in c:
        #     print(i)
        #     csv.writer(file).writerow(i)        # writerow():写入单行
        a = c.fetchall()
        # print(a)
        csv.writer(file).writerows(a)           # writerows():写入多行

def save_to_csv_pandas(csv_filename, basedomain):
    """pandas读取sqlite到DataFrame，再写入csv文件
    """
    sqlite_filename = find_firefox_cookies()
    con = sqlite3.connect(sqlite_filename)
    # table = sql.read_sql_query("SELECT * FROM moz_cookies WHERE baseDomain='%s';" % basedomain, con)
    table = pandas.read_sql("SELECT * FROM moz_cookies WHERE baseDomain='%s';" % basedomain, con)
    table.to_csv(csv_filename)


if __name__ == '__main__':
    # save_to_csv('webscraping.csv', "'webscraping.com'")     # sql语句，使用format时需要再加上双引号""
    save_to_csv('webscraping.csv', 'webscraping.com')
