# -*- coding: UTF-8 -*-
"""
该方法兼容 python2 和 python3
"""
import urllib
import lxml.html
import pprint
import csv
from sqlite_read import sqlite_read

try:
    from cookielib import CookieJar, MozillaCookieJar, LWPCookieJar, Cookie         # python2 包名
    from urllib2 import build_opener, HTTPCookieProcessor, Request
    from sqlite_to_csv_2 import save_to_csv
except ImportError:
    from http.cookiejar import CookieJar, MozillaCookieJar, LWPCookieJar, Cookie    # python3 包名
    from urllib.request import build_opener, HTTPCookieProcessor, Request
    from sqlite_to_csv_3 import save_to_csv


LOGIN_URL = 'http://example.webscraping.com/places/default/user/login'
LOGIN_EMAIL = 'example@webscraping.com'
LOGIN_PASSWORD = 'example'


def login_cookies():
    """自动登录
    """
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))

    html = opener.open(LOGIN_URL).read()
    data = parse_form(html)
    # pprint.pprint(data)

    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    encoded_data = urllib.urlencode(data)
    request = Request(LOGIN_URL, encoded_data)
    response = opener.open(request)
    # print(response.info())             # 获取http服务器返回的响应头信息
    print(response.geturl())             # 登录成功，跳转至主页
    return opener

def login_firefox(url, csv_filename, basedomain):
    """手工登录，再复用cookie
    """
    cj = load_cookies(csv_filename, basedomain)
    opener = build_opener(HTTPCookieProcessor(cj))

    html = opener.open(url).read()
    tree = lxml.html.fromstring(html)
    welcome = tree.cssselect('ul#navbar li a')[0].text_content()
    print(welcome)                       # 登录成功，解析出问候语

def make_cookie(name, value):
    """ 生成 cookie
        参考：https://docs.python.org/2/library/cookielib.html
    """
    return Cookie(
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

def load_cookies(csv_filename, basedomain):
    """ 加载 cookie：cookies.sqlite -> cookies.csv -> make_cookie()     仅适用于firefox
    """
    cj = CookieJar()
    save_to_csv(csv_filename, basedomain)                   # 将cookies.sqlite写入csv文件
    cookies = csv.reader(open(csv_filename, 'r'))           # 获取 cookies
    fields = sqlite_read()                                  # 获取 表列名
    for cookie in cookies:
        aa = dict(zip(fields, cookie))      # 两个列表组成字典
        # pprint.pprint(aa)
        c = make_cookie(aa['name'], aa['value'])
        cj.set_cookie(c)                    # 循环设置多个cookie，cookie不会覆盖
    for index, cookie in enumerate(cj):     # 显示cookies
        print('[', index, ']', cookie)
    return cj

def load_cookies2():
    """ 加载 cookie：变量 -> make_cookie()
    """
    cj = CookieJar()
    cookie1 = ['session_data_places', '"8bd6acbc1de59b1dfceb2099ae7c2b3a:JeRQM1TZ9lwn_7e9KS2LcAGQjUai1Y5TbtUsr1D-qUj_rleZ8zKEu9iUVL0V-r9_icFERBwtpsJE7eusjbh7G_M3Jlem9ojkSkOpjNBuv4qvPFUmtBtgECSfJr2aHDQPibmo1jZKgrVvjuMCYgbJeGoCVqsU8Ru3UIpHnGwrCubtNEvfFQB0dEickfTDUSlprWpH4Oq8YOmAimJ00nI3AJUqub5DfY0kZLVL6KFl7L-xn79HwEhzzE_dVbYi7lD_6ZUi-Q5ob6197UL8dp1zJnD6OQ37iriLG6uZ4wAliRgUt8xIb9ebg60o6viRmat2tkC9fJwbb2ghEoGResxA8-1p6h-Z26nFH_QPG00J7N27UA7B3tB1aIlgufn48Ng6b-2EAp37j01WR5z5S0QposiYl4aWLOGVZIhlLOgfRW2v3yv00aooW2jXhSjMGEeQ8TNyzWRQUPiNYEXqV-Hu52ZFB7y9jGqFRGgL0fQqzP7zb3c0out8omE54eNOUS9QoYK46GUt7Mgiql-jisc4sJPEdttuRTx2wsbJn8DJfV-_Y7A6Lwi8j9cRyqAYwtALD9sCeT7QM3D6yacgBhf9CMCmNTRIK-ZH34a85ZlcFgBUiUY778f268C3tqCxlozD-XMNgpRk7VC9UU5a0COjNZPwo_zgI759dx1IognjndUSrl9YU-WX02sY4PNYoR0AXIIV-cqfpBkQq6uM_UBhSEdNxCdlAk8rqZBoPRFuh98DpExdW3xuScE_BkeVB1WtT7VW_82rEoqxrYP5BLoISK4wck_D8fvQf6AjjzJLPtRKVZCpLrbl0Rq8IhWjlfrinAx6rlCGyIN5bEgKrnoxxqFI4DNg2eg84iVh4wTwqr72Gwe-OA9q6xLTgEIr2gfCrb3WqsMFQR8FWSjqCy_YyyBQzsBNGd_S5lZ8iruzzlR_5OkeHkTFX8qkfgJTNsXWwL-s9U3dCJITWqi35qRky7XJ4-a_qY5WnPtjh9nP1G7p9SLSrXzeJ7Pch4bi2T_xddzmo5nZGx8MxO-dmKY1rHG5SdGQNveHQQOYuod6YwWJTa_YcxObJ72itblRIFNB"']
    cookie2 = ['session_id_places', 'True']
    cookies = [cookie1, cookie2]            # 将cookies存入列表
    fields = ['name', 'value']
    for cookie in cookies:
        aa = dict(zip(fields, cookie))      # 两个列表组成字典
        # pprint.pprint(aa)
        c = make_cookie(aa['name'], aa['value'])
        cj.set_cookie(c)                    # 循环设置多个cookie，cookie不会覆盖
    for index, cookie in enumerate(cj):     # 显示cookies
        print('[', index, ']', cookie)
    return cj

def load_cookies3():
    """ 加载 cookie：cookies.txt -> load()  —— MozillaCookieJar格式
    """
    save_to_txt()
    cj = MozillaCookieJar()
    cj.load('localCookiesMoz.txt', ignore_discard=True, ignore_expires=True)    # 这里必须将参数置为True，否则登录失败
    for index, cookie in enumerate(cj):     # 显示cookies
        print('[', index, ']', cookie)
    return cj

def load_cookies4():
    """ 加载 cookie：cookies.txt -> load()  —— LWPCookieJar格式
    """
    cj = LWPCookieJar()
    cj.load('localCookiesLWP.txt', ignore_discard=True, ignore_expires=True)    # 这里必须将参数置为True，否则登录失败
    for index, cookie in enumerate(cj):     # 显示cookies
        print('[', index, ']', cookie)
    return cj

def save_to_txt():
    """ 保存 cookie：生成cookies.txt —— MozillaCookieJar格式
    """
    cookie1 = [
        'example.webscraping.com',  # domain
        'FALSE',                    # 此参数置为TRUE时报错
        '/',                        # path
        'FALSE',                    #
        '',                         # 这里有2个tab间隔，所以加个空字符串''
        'session_data_places',      # name
        '"92e018c966ae4109802cadd0b986a284:RLmLLCJN93TMcPAH7pcwMAsdrkIzxZagLPZbaq0nyOdtFkf2-Pp0cbwTHapQa789Mid9q_luNEdm-51oUYSxAwYPSwiV1K3a28oCCO5jJQb53Esx_QC5s7y8xyoVqXmQ-_5Wophaxu3KWSSyTuWK5Yvp-oI2CaeXLB5SeI-Tblv15fZUVUrBv3aZ8awztlnGli2y5s5n-qolz5IgEBfYJ6RP9Lk6LTXIYnSPc7Ye2O6-W_c68Spyu40TEbQpzwcrogwFrDakG-9GmVgc6_S1bBVHYAeqe9JPNbhySEPTN7RQfHnPXpJTx5rWnBIOUd6ttl37VnRPoIB-Dy9joP6_HFdEpS9W0siquJoxFYBbeu-3CcVseNYpvNTmnvvEMetgMnis0gOnsEJy0br5PaxHyHrq-OuuSK3HU2wYKOtlmc2ffStrYTDBmwDK62IGV0Mvid8DqiqoZAHIbE58PNjaUVl_HyNFiUfZ0i1UWQ3R9asjY86C00MmrgZYi6t1vCpXJW5wQSNserRNMsq4mYw2px9zx0o9h1LdryoPXALA0bJYuDoN9n-kMKqgRvPeOKyjFV1Iqn_JEuh81tfB4qfVvTw_yH8gtq3M3kk95zFrAciv0AqTmK-KRJlCsYib2QyfQO678ecO2NHpxgdLC19NFEDD8wUOmuAXrcyTG5aV_kWNQzXr3dfE9HDoLAVXcR-le6VirTRnfpvsPWs0RcYro23z4ggUOYbz_VPaHJoKO2XvJL3R6y85ZG8o7oh-AdBZJMkxwbUMRXj83SWPzrBu0CK8u5h6G2ko6aMud3c1TE7okULJ-nbCAG5oI_RWAxY7Myzg3N_AH1Q5hn2KsK0WNmPQvRirl7ZllnnsV46J4blyO4Qk0BIs3nl9QtwnCufb9WyBqDXgJ-O-I97ZlL2ot3nXGe9MbzIy0s1L30B8FVWdoeX-kD8Y1epZG6d4Y-o8"'
    ]
    cookie2 = [
        'example.webscraping.com',  # domain
        'FALSE',
        '/',
        'FALSE',
        '',
        'session_id_places',        # name
        'True'                      # value
    ]
    cookies = [cookie1, cookie2]
    with open('localCookiesMoz.txt','wb') as file_obj:
        file_obj.write('# Netscape HTTP Cookie File\n\n')                   # 此句必须写入文件，否则报错
        for cookie in cookies:
            cookie = '\t'.join(cookie)
            file_obj.write(cookie)
            file_obj.write('\n')

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
    url = 'http://example.webscraping.com'
    csv_filename = 'webscraping.csv'
    basedomain = 'webscraping.com'
    # login_cookies()
    login_firefox(url, csv_filename, basedomain)
