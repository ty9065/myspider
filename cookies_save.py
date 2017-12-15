# -*- coding: UTF-8 -*-
"""
该方法兼容 python2 和 python3
"""
try:
    from cookielib import CookieJar, MozillaCookieJar, LWPCookieJar             # python2 包名
    from urllib2 import build_opener, HTTPCookieProcessor
except ImportError:
    from http.cookiejar import CookieJar, MozillaCookieJar, LWPCookieJar        # python3 包名
    from urllib.request import build_opener, HTTPCookieProcessor


def cookies(url):
    """保存cookies到变量
    """
    #声明一个CookieJar对象实例来保存cookie
    cookie = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie))
    #此处的open方法同urllib2的urlopen方法，也可以传入request
    response = opener.open(url)
    for item in cookie:
        print('Name = '+item.name)
        print('Value = '+item.value)

def save_cookies_Moz(url):
    """保存cookies到文件 —— MozillaCookieJar格式
    """
    # 设置保存cookie的文件，同级目录下的cookie.txt
    filename = 'cookies_Moz.txt'
    # 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookie = MozillaCookieJar(filename)
    opener = build_opener(HTTPCookieProcessor(cookie))
    # 创建一个请求，原理同urllib2的urlopen
    response = opener.open(url)
    # 保存cookie到文件
    cookie.save(ignore_discard=True, ignore_expires=True)       # 这里必须将参数置为True，否则写入文件失败

def save_cookies_LWP(url):
    """保存cookies到文件 —— LWPCookieJar格式
    """
    # 设置保存cookie的文件，同级目录下的cookie.txt
    filename = 'cookies_LWP.txt'
    # 声明一个LWPCookieJar对象实例来保存cookie，之后写入文件
    cookie = LWPCookieJar(filename)
    opener = build_opener(HTTPCookieProcessor(cookie))
    # 创建一个请求，原理同urllib2的urlopen
    response = opener.open(url)
    # 保存cookie到文件
    cookie.save(ignore_discard=True, ignore_expires=True)       # 这里必须将参数置为True，否则写入文件失败


if __name__ == '__main__':
    url = 'http://example.webscraping.com'
    cookies(url)
    save_cookies_Moz(url)
    save_cookies_LWP(url)
