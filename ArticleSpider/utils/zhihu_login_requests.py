#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/29 18:01
# @Author  : Mpetrel
# @Site    : 
# @File    : zhihu_login_requests.py
# @Software: PyCharm

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re
from zheye.zheye import zheye
import json
import time
import os

session = requests.Session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
try:
    session.cookies.load(ignore_discard = True)
except:
    print('cookie 未能加载')
agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) " \
        "Chrome/61.0.3163.100 Safari/537.36"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    "User-Agent": agent
}

def get_xsrf():
    response = session.get("https://www.zhihu.com", headers = header)
    #匹配xsrf的值
    #print(response.text)
    # xs = '<input type="hidden" name="_xsrf" value="0ca2ca09a35d2568361e82d546c6a046"/>'
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
    #match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        print(match_obj.group(1))
        return match_obj.group(1)
    else:
        return ""

#识别验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    img_url = 'https://www.zhihu.com/captcha.gif?r='+t+'&type=login&lang=cn'
    response = session.get(img_url, headers = header)
    if(response.status_code == 200):
        if not os.path.exists('../images/captcha/'):
            os.makedirs('../images/captcha/')
        f_captcha = open('../images/captcha/captcha.gif', 'wb')
        f_captcha.write(response.content)
        return zheye().Recognize(os.path.abspath('../images/captcha/captcha.gif'))
    return None



#知乎登录
def zhihu_login(account, password):
    # 判断登录类型
    if re.match("^1\d{10}", account):
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            #"captcha": zheye().Recognize(""),
            #"remember_me": "true",
            "phone_num": account,
            "password": password
        }
    else:
        post_url = "https://www.zhihu.com/login/email"
        post_data = {
            "_xsrf": get_xsrf(),
            #"captcha": zheye().Recognize(""),
            #"remember_me": "true",
            "email": account,
            "password": password
        }


    response_text = session.post(post_url, data=post_data, headers = header)
    # 查看是否登录成功,需要验证码从新识别
    if(json.loads(response_text.text))['r'] == 1:
        print('需要验证码，开始识别.....')
        post_data['captcha'] = {"img_size":[200,44],"input_points":get_captcha()}
        post_data['captcha_type'] = 'cn'
        print('验证码识别结果：%s' % (post_data['captcha']))
        response_text = session.post(post_url, data=post_data, headers=header)
        #print((json.loads(response_text.text))['msg'])
    print(response_text.text)
    session.cookies.save(ignore_discard = True, ignore_expires = True)


def is_login():
    url = 'https://www.zhihu.com/settings/profile'
    login_code = session.get(url, headers = header).status_code
    if login_code == 200:
        return True
    else:
        return False


print(is_login())

#zhihu_login("lovicey@foxmail.com", "Lovsmm520?")