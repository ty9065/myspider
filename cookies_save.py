# -*- coding: UTF-8 -*-
import cookielib
import urllib2

def cookies():
    """保存cookies到变量
    """
    #声明一个CookieJar对象实例来保存cookie
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    #此处的open方法同urllib2的urlopen方法，也可以传入request
    response = opener.open('http://example.webscraping.com')
    for item in cookie:
        print ('Name = '+item.name)
        print ('Value = '+item.value)

def save_cookies_Moz():
    """保存cookies到文件 —— MozillaCookieJar格式
    """
    # 设置保存cookie的文件，同级目录下的cookie.txt
    filename = 'cookies_Moz.txt'
    # 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookie = cookielib.MozillaCookieJar(filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    # 创建一个请求，原理同urllib2的urlopen
    response = opener.open("http://example.webscraping.com")
    # 保存cookie到文件
    cookie.save(ignore_discard=True, ignore_expires=True)       # 这里必须将参数置为True，否则写入文件失败

def save_cookies_LWP():
    """保存cookies到文件 —— LWPCookieJar格式
    """
    # 设置保存cookie的文件，同级目录下的cookie.txt
    filename = 'cookies_LWP.txt'
    # 声明一个LWPCookieJar对象实例来保存cookie，之后写入文件
    cookie = cookielib.LWPCookieJar(filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    # 创建一个请求，原理同urllib2的urlopen
    response = opener.open("http://example.webscraping.com")
    # 保存cookie到文件
    cookie.save(ignore_discard=True, ignore_expires=True)       # 这里必须将参数置为True，否则写入文件失败


if __name__ == '__main__':
    cookies()
    save_cookies_Moz()
    save_cookies_LWP()
