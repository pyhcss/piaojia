# coding=utf-8

import random
import tornado.httpclient


class Base_Httpclient(object):
    """基础请求客户端类"""
    def __init__(self,cookies=None):
        """初始化"""
        user_agent = [
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
        self.headers = {                                        # 创建报头信息
            "User-Agent": random.choice(user_agent),
            "Host":"kyfw.12306.cn",
            "Origin":"https://kyfw.12306.cn",
            "Accept-Language":"zh-CN,zh;q=0.8",
            "Connection":"keep-alive",
        }
        http_client = tornado.httpclient.AsyncHTTPClient()      # 创建客户端对象
        self.fetch = http_client.fetch                          # 创建发送请求对象
        self.request = tornado.httpclient.HTTPRequest           # 创建请求对象
        self.cookies = cookies if cookies else {}

    def format_cookies(self, set_cookie, cookie_dict=None):
        """
        处理cookies 格式化成字典
        set_cookie:服务器返回的set-cookie 类字典对象
        cookie_dict:{} 原cookie字典
        return cookie_dict:{} 增加后的cookie字典
        """
        cookie_dict = cookie_dict if cookie_dict else {}        # 遍历服务器设置的cookie 追加到字典
        for y in [x[0].split("=") for x in [i.split(";") for i in set_cookie.split(",")]]:
            cookie_dict[y[0]] = y[1]
        return cookie_dict                                      # 返回追加后的字典对象
