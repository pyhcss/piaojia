# coding=utf-8

import re
import json
import random
import urllib
import tornado.web
import tornado.gen
import tornado.httpclient


class Captcha(object):
    """获取12306验证码"""
    def __init__(self):
        self.user_agent = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
            'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10',
            'Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13',
            'Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+',
            'Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0',
            'Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)',
        ]

    @tornado.gen.coroutine
    def get_captcha(self):
        """获取12306验证码"""
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&"
        url += str(random.random())                         # 添加自定义随机数
        request = tornado.httpclient.HTTPRequest(url,headers={"User-Agent":random.choice(self.user_agent)})# 构建请求对象
        http_client = tornado.httpclient.AsyncHTTPClient()  # 创建客户端对象
        resp = yield http_client.fetch(request)             # 发送请求拿到响应
                                                            # 拿到set-Cookie中的_passport_ct字段值
        cookies = {}
        for y in [ x[0].split("=") for x in [i.split(";") for i in resp.headers["Set-Cookie"].split(",")]]:
            cookies[y[0]] = y[1]
        image_data = resp.body                              # 拿到图片数据
                                                            # 返回结果
        raise tornado.gen.Return({"cookies":cookies,"image":image_data})

    @tornado.gen.coroutine
    def check_captcha(self,cookies,value):
        """
        校验验证码
        cookies 验证码id {"":""} 服务器设置的键值对
        value 验证码值 "" 用户输入的文本值
        """
        text_list = []
        if "1" in value:                                    # 判断输入内容把值加入列表
            text_list.append(str(random.randint(30,40)))
            text_list.append(str(random.randint(40,50)))
        if "2" in value:
            text_list.append(str(random.randint(30,40)))
            text_list.append(str(random.randint(110,120)))
        if "3" in value:
            text_list.append(str(random.randint(107,115)))
            text_list.append(str(random.randint(40,50)))
        if "4" in value:
            text_list.append(str(random.randint(107, 115)))
            text_list.append(str(random.randint(110, 120)))
        if "5" in value:
            text_list.append(str(random.randint(180,185)))
            text_list.append(str(random.randint(40, 50)))
        if "6" in value:
            text_list.append(str(random.randint(180,185)))
            text_list.append(str(random.randint(110,120)))
        if "7" in value:
            text_list.append(str(random.randint(248,260)))
            text_list.append(str(random.randint(40, 50)))
        if "8" in value:
            text_list.append(str(random.randint(248,260)))
            text_list.append(str(random.randint(110,120)))
        value = ",".join(text_list)                         # 拼接列表组成验证码文本
        url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        data = {                                            # 创建数据内容
            "answer":value,                                 # 验证码值
            "login_site":"E",                               # 固定值
            "rand":"sjrand"                                 # 固定值
        }
        headers = {"User-Agent":random.choice(self.user_agent)}# 构建请求对象
        headers["Cookie"] = ";".join([i + "=" + cookies[i] for i in cookies])
        request = tornado.httpclient.HTTPRequest(url,method="POST",headers=headers,body=urllib.urlencode(data))
        http_client = tornado.httpclient.AsyncHTTPClient()  # 创建客户端对象
        resp = yield http_client.fetch(request)             # 发送请求拿到响应
                                                            # 获取所有cookie值组成字典
        try:
            for y in [x[0].split("=") for x in [i.split(";") for i in resp.headers["Set-Cookie"].split(",")]]:
                cookies[y[0]] = y[1]
        except Exception as e:
            pass
        # "7" 验证码已过期 "5" 验证码错误 "4" 验证码校验成功      # 返回数据
        print resp.body
        raise tornado.gen.Return({"errcode":json.loads(resp.body)["result_code"],"cookies":cookies})
