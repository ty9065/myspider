# -*- coding: UTF-8 -*-

# 备注：最新版的 Firefox 和 Chrome 通过 browsercookie 获取 cookies 失败
# 原因：
# ———— Firefox 将 sessionstore.js 压缩为 sessionstore.jsonlz4
# ———— Chrome 对 cookies 进行了加密
# 参考：https://bitbucket.org/richardpenman/browsercookie

import re
import urllib2
import browsercookie
import requests

URL = 'http://example.webscraping.com'

def download():
    get_title = lambda html: re.findall('<title>(.*?)</title>', html, flags=re.DOTALL)[0].strip()
    html = urllib2.urlopen(URL).read()
    print get_title(html)

def cookies_test1():
    get_title = lambda html: re.findall('<title>(.*?)</title>', html, flags=re.DOTALL)[0].strip()
    cj = browsercookie.firefox()
    # cj = browsercookie.chrome()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(URL).read()
    print get_title(html)

def cookies_test2():
    get_title = lambda html: re.findall('<title>(.*?)</title>', html, flags=re.DOTALL)[0].strip()
    cj = browsercookie.firefox()            # 获取 Firefox cookies
    # cj = browsercookie.chrome()           # 获取 Chrome cookies
    r = requests.get(URL, cookies=cj)
    print get_title(r.content)

def cookies_test3():
    get_title = lambda html: re.findall('<title>(.*?)</title>', html, flags=re.DOTALL)[0].strip()
    cj = browsercookie.load()               # 获取 all available browser cookies
    r = requests.get(URL, cookies=cj)
    print get_title(r.content)

if __name__ == '__main__':
    download()
    cookies_test1()                         # 使用 urllib2
    cookies_test2()                         # 使用 requests
    cookies_test3()                         # 使用 requests
