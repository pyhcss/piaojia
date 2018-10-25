# coding=utf-8

import json
import random
import urllib
import tornado.gen
import tornado.httpclient


class CheckLogin(object):
    """验证登录类"""
    def __init__(self):
        """初始化"""
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
            'android/4.7.0 (android 7.0; ; MI+5s)',
        ]

    @tornado.gen.coroutine
    def get_uamtk(self,user,pwd,cookies):
        """
        发送账号密码请求
        user: "" "账号"
        pwd： "" "密码"
        cookies:{"":""} "cookie字典"
        return: {"状态码":"","说明":"","cookies"：{}}
        """
        url = "https://kyfw.12306.cn/passport/web/login"
        data = {                                            # 创建数据内容
            "username":user,                                # 账户名
            "password":pwd,                                 # 密码
            "appid": "otn"                                  # 固定值
        }                                                   # 设置自定义报头
        headers = {"User-Agent":random.choice(self.user_agent)}
        headers["Cookie"] = ";".join([i+"="+cookies[i] for i in cookies])
        request = tornado.httpclient.HTTPRequest(url,method="POST",headers=headers,body=urllib.urlencode(data))
        http_client = tornado.httpclient.AsyncHTTPClient()  # 创建客户端对象
        resp = yield http_client.fetch(request)             # 发送请求 获取json数据
        data = json.loads(resp.body)                        # 解析json数据
        if data["result_code"] == 0:                        # 如果返回值为0校验成功
            cookies["uamtk"] = data["uamtk"]
            del cookies["_passport_ct"]
            raise tornado.gen.Return({"errcode":"0","errmsg":"账号密码校验成功","cookies":cookies})
        else:                                               # 否则校验失败
            raise tornado.gen.Return({"errcode":"4103","errmsg":"账号密码校验失败"})

    @tornado.gen.coroutine
    def get_user_name(self,cookies):
        """
        获取newapptk 获取用户名
        cookies:{} 上次发送请求后的cookies字典
        return: {"状态码":"","说明":"","用户名":"","cookies":{}}
        """
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        data = {"appid":"otn"}                              # 自定义请求内容
        headers = {"User-Agent": random.choice(self.user_agent)}
        headers["Cookie"] = ";".join([i + "=" + cookies[i] for i in cookies])
        request = tornado.httpclient.HTTPRequest(url, method="POST", headers=headers, body=urllib.urlencode(data))
        http_client = tornado.httpclient.AsyncHTTPClient()  # 请求客户端对象
        resp = yield http_client.fetch(request)             # 发送请求 获取json数据
        data = json.loads(resp.body)                        # 解析json数据
        if data["result_code"] == 0:                        # 如果返回值为0则成功
            newapptk = data["newapptk"]                     # 服务器生成值
        else:                                               # 否则校验失败
            raise tornado.gen.Return({"errcode": "4103", "errmsg": "newapptk获取失败"})
        url = "https://kyfw.12306.cn/otn/uamauthclient"
        data = {"tk":newapptk}                              # 上一步获取到的值
        request = tornado.httpclient.HTTPRequest(url, method="POST", headers=headers, body=urllib.urlencode(data))
        resp = yield http_client.fetch(request)             # 发送请求 获取json数据
        data = json.loads(resp.body)                        # 解析json数据
        if data["result_code"] == 0:                        # 如果返回值为0则成功
            for y in [x[0].split("=") for x in [i.split(";") for i in resp.headers["Set-Cookie"].split(",")]]:
                cookies[y[0]] = y[1]                        # 将服务器设置的cookie添加到cookie字典
            user_name = data["username"]                    # 拿到用户名
        else:                                               # 否则校验失败
            print "用户名获取失败"
            raise tornado.gen.Return({"errcode": "4103", "errmsg": "newapptk获取失败"})
        # 获取html文本 模拟行为 可省略
        url = "https://kyfw.12306.cn/otn/index/initMy12306"
        headers["Cookie"] = ";".join([i + "=" + cookies[i] for i in cookies])
        request = tornado.httpclient.HTTPRequest(url, method="GET", headers=headers)
        yield http_client.fetch(request)                    # 仅发送请求就行
        # 返回登录成功的返回值
        raise tornado.gen.Return({"errcode":"0","errmsg":"用户名获取成功","cookies":cookies,"username":user_name})