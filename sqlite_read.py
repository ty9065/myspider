# -*- coding: UTF-8 -*-
import sqlite3
import pprint
import os, glob

def sqlite_read():
    """python读取sqlite数据库文件
    """
    sqlite_filename = find_firefox_cookies()
    mydb = sqlite3.connect(sqlite_filename)     # 链接数据库
    cur = mydb.cursor()                         # 创建游标cursor来执行SQL语句

    # 获取表名
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    Tables = cur.fetchall()                     # Tables 为元组列表
    # print Tables

    tbl_name = Tables[0][0]                     # 获取第一个表名

    # 获取表的列名
    cur.execute("SELECT * FROM {};".format(tbl_name))
    col_name_list = [tuple[0] for tuple in cur.description]
    # pprint.pprint(col_name_list)

    # 获取表结构的所有信息
    cur.execute("PRAGMA table_info({});".format(tbl_name))
    table_info = cur.fetchall()
    # pprint.pprint(table_info)

    return col_name_list

def find_firefox_cookies():
    paths = [
        '~/Library/Application Support/Firefox/Profiles/*.default'
    ]
    for path in paths:
        filename = os.path.join(path, 'cookies.sqlite')     # glob模块：返回指定路径中所有匹配的文件
        matches = glob.glob(os.path.expanduser(filename))   # expanduser把path中包含的"~"和"~user"转换成用户目录
        if matches:
            print matches[0]
            return matches[0]


if __name__ == '__main__':
    sqlite_read()

