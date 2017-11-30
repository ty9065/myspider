# -*- coding: UTF-8 -*-
import urllib, urllib2
import lxml.html
import pprint
import cookielib
import csv
from sqlite_read import sqlite_read
from sqlite_to_cvs import save_to_csv


LOGIN_URL = 'http://example.webscraping.com/places/default/user/login'
LOGIN_EMAIL = 'example@webscraping.com'
LOGIN_PASSWORD = 'example'


def login_cookies():
    """自动登录
    """
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    html = opener.open(LOGIN_URL).read()
    data = parse_form(html)
    pprint.pprint(data)

    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = opener.open(request)
    # print response.info()             # 获取http服务器返回的响应头信息
    print response.geturl()             # 登录成功，跳转至主页

def login_firefox():
    """手工登录，再复用cookie
    """
    cj = load_cookies()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    url = 'http://example.webscraping.com'
    html = opener.open(url).read()
    tree = lxml.html.fromstring(html)
    welcome = tree.cssselect('ul#navbar li a')[0].text_content()
    print welcome                       # 登录成功，解析出问候语

def make_cookie(name, value):
    """ 生成 cookie
        参考：https://docs.python.org/2/library/cookielib.html
    """
    return cookielib.Cookie(
                             version=0,
                             name=name,
                             value=value,
                             port=None,
                             port_specified=False,
                             domain="example.webscraping.com",
                             domain_specified=True,
                             domain_initial_dot=False,
                             path="/",
                             path_specified=True,
                             secure=False,
                             expires=None,
                             discard=False,
                             comment=None,
                             comment_url=None,
                             rest=None
        )

def load_cookies():
    """ 加载 cookie
    """
    cj = cookielib.CookieJar()
    save_to_csv('export_data.csv')          # 将cookies.sqlite写入csv文件
    cookies = csv.reader(open("export_data.csv", "rb"))     # 获取 cookies
    fields = sqlite_read()                                  # 获取 表列名
    for cookie in cookies:
        aa = dict(zip(fields, cookie))      # 两个列表组成字典
        # pprint.pprint(aa)
        c = make_cookie(aa['name'], aa['value'])
        cj.set_cookie(c)                    # 循环设置多个cookie，cookie不会覆盖
    for index, cookie in enumerate(cj):     # 显示cookies
        print '[', index, ']', cookie
    return cj

def parse_form(html):
    """解析出form中所有的input
    ———为了提交隐藏的_formkey
    """
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data


if __name__ == '__main__':
    # login_cookies()
    login_firefox()
