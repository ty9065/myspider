# -*- coding: UTF-8 -*-
"""
sqlite to csv for python2
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sqlite3
import csv, codecs
from sqlite_read import find_firefox_cookies


def save_to_csv(csv_filename, basedomain):
    """sqlite数据库写入csv文件
    """
    sqlite_filename = find_firefox_cookies()
    con = sqlite3.connect(sqlite_filename)
    c = con.cursor()
    # c.execute("SELECT * FROM moz_cookies WHERE baseDomain={};".format(basedomain))    # format用法：对应"'webscraping.com'"
    c.execute("SELECT * FROM moz_cookies WHERE baseDomain='%s';" % basedomain)          # '%s'  用法：对应'webscraping.com'
    with open(csv_filename, 'w') as file:
        file.write(codecs.BOM_UTF8)  # 防止乱码
        # for i in c:
        #     print(i)
        #     csv.writer(file).writerow(i)        # writerow():写入单行
        a = c.fetchall()
        # print(a)
        csv.writer(file).writerows(a)       # writerows():写入多行


if __name__ == '__main__':
    # save_to_csv('webscraping.csv', "'webscraping.com'")     # sql语句，使用format时需要再加上双引号""
    save_to_csv('webscraping.csv', 'webscraping.com')
