# -*- coding: UTF-8 -*-
import urllib
import urllib2
import cookielib
import pprint
from login_auto import parse_form

from io import BytesIO
import lxml.html
from PIL import Image

import pytesseract
import string


REGISTER_URL = 'http://example.webscraping.com/places/default/user/register'


def register(first_name, last_name, email, password):
    """自动注册
    """
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(REGISTER_URL).read()         # 下载注册页面
    form = parse_form(html)                         # 提取表单
    pprint.pprint(form)

    form['first_name'] = first_name                 # 添加账号
    form['last_name'] = last_name
    form['email'] = email
    form['password'] = password
    form['password_two'] = password

    img = get_captcha(html)                         # 提取验证码图像
    captcha = ocr(img)                              # 提取验证码文本
    form['recaptcha_response_field'] = captcha      # 添加验证码

    encoded_data = urllib.urlencode(form)           # 提交表单数据
    request = urllib2.Request(REGISTER_URL, encoded_data)
    response = opener.open(request)

    success = '/user/register' not in response.geturl()     # 检查响应URL，确认注册是否成功
    return success

def get_captcha(html):
    """提取验证码图像
    """
    tree = lxml.html.fromstring(html)
    img_data = tree.cssselect('div#recaptcha img')[0].get('src')
    img_data = img_data.partition(',')[-1]          # partition():根据指定的分隔符将字符串进行分割
    binary_img_data = img_data.decode('base64')     # 解码
    file_like = BytesIO(binary_img_data)            # 封装二进制数据
    img = Image.open(file_like)
    return img

def ocr(img):
    """提取验证码图像中的文本
    """
    img.save('captcha_original.png')
    gray = img.convert('L')
    gray.save('captcha_gray.png')
    bw = gray.point(lambda x: 0 if x < 1 else 255, '1')
    bw.save('captcha_thresholded.png')
    word = pytesseract.image_to_string(bw)
    ascii_word = ''.join(c for c in word if c in string.letters).lower()
    return ascii_word


if __name__ == '__main__':
    print register('Test Account', 'Test Account', 'example@webscraping.com', 'example')
