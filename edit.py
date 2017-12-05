# -*- coding: UTF-8 -*-
import urllib, urllib2
import pprint
from login_auto import login_cookies, parse_form
import mechanize


COUNTRY_URL = 'http://example.webscraping.com/places/default/edit/United-Kingdom-239'
LOGIN_URL = 'http://example.webscraping.com/places/default/user/login'
LOGIN_EMAIL = 'example@webscraping.com'
LOGIN_PASSWORD = 'example'


def edit():
    """每运行一次脚本，国家人口数量加1
    """
    opener = login_cookies()
    html = opener.open(COUNTRY_URL).read()
    data = parse_form(html)
    pprint.pprint(data)
    print 'Population before:', data['population']
    data['population'] = int(data['population']) + 1

    encode_data = urllib.urlencode(data)
    request = urllib2.Request(COUNTRY_URL, encode_data)
    response = opener.open(request)

    html = opener.open(COUNTRY_URL).read()
    data = parse_form(html)
    print 'Population after:', data['population']

def mechanize_edit():
    """使用 mechanize 增加国家人口数量
    """
    # 登录
    br = mechanize.Browser()

    br.open(LOGIN_URL)
    br.select_form(nr=0)
    print br.form
    br['email'] = LOGIN_EMAIL
    br['password'] = LOGIN_PASSWORD
    response = br.submit()

    # 修改
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population before:', br['population']
    br['population'] = str(int(br['population']) + 1)
    br.submit()

    # 查看
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population after:', br['population']


if __name__ == '__main__':
    # edit()
    mechanize_edit()
