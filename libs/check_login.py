# coding=utf-8

import time
import json
import urllib
import tornado.gen
from base_httpclient import Base_Httpclient


class CheckLogin(Base_Httpclient):
    """验证登录类"""
    @tornado.gen.coroutine
    def get_uamtk(self,user,pwd):
        """
        发送账号密码请求
        user: "" "账号"
        pwd： "" "密码"
        return: {"状态码":"","说明":"","cookies"：{}}
        """
        url = "https://kyfw.12306.cn/passport/web/login"
        data = {                                                # 创建数据内容
            "username":user,                                    # 账户名
            "password":pwd,                                     # 密码
            "appid": "otn"                                      # 固定值
        }                                                       # 设置自定义报头
        headers = self.headers
        headers["Cookie"] = ";".join([i+"="+self.cookies[i] for i in self.cookies])
        request = self.request(url,method="POST",headers=headers,body=urllib.urlencode(data))
        while True:
            try:
                resp = yield self.fetch(request)                # 发送请求 获取json数据
            except Exception as e:
                continue
            else:
                break
        data = json.loads(resp.body)                            # 解析json数据
        if data["result_code"] == 0:                            # 如果返回值为0校验成功
            self.cookies["uamtk"] = data["uamtk"]
            del self.cookies["_passport_ct"]
            raise tornado.gen.Return({"errcode":"0","errmsg":"账号密码校验成功","cookies":self.cookies})
        else:                                                   # 否则校验失败
            print "账号密码校验失败"
            print resp.body
            raise tornado.gen.Return({"errcode":"4103","errmsg":"账号密码校验失败"})

    @tornado.gen.coroutine
    def get_user_name(self):
        """
        获取newapptk 获取用户名
        return: {"状态码":"","说明":"","用户名":"","cookies":{}}
        """
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        data = {"appid":"otn"}                                  # 自定义请求内容
        headers = self.headers
        headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies])
        request = self.request(url, method="POST", headers=headers, body=urllib.urlencode(data))
        while True:
            try:
                resp = yield self.fetch(request)                # 发送请求 获取json数据
            except Exception as e:
                continue
            else:
                break
        data = json.loads(resp.body)                            # 解析json数据
        if data["result_code"] == 0:                            # 如果返回值为0则成功
            newapptk = data["newapptk"]                         # 服务器生成值
        else:                                                   # 否则校验失败
            print "newapptk获取失败"
            raise tornado.gen.Return({"errcode": "4103", "errmsg": "newapptk获取失败"})
        url = "https://kyfw.12306.cn/otn/uamauthclient"
        data = {"tk":newapptk}                                  # 上一步获取到的值
        request = self.request(url, method="POST", headers=headers, body=urllib.urlencode(data))
        while True:
            try:
                resp = yield self.fetch(request)                # 发送请求 获取json数据
            except Exception as e:
                continue
            else:
                break
        data = json.loads(resp.body)                            # 解析json数据
        if data["result_code"] == 0:                            # 如果返回值为0则成功
            self.cookies = self.format_cookies(resp.headers["Set-Cookie"],self.cookies)
            user_name = data["username"]                        # 拿到用户名
        else:                                                   # 否则校验失败
            print "用户名获取失败"
            raise tornado.gen.Return({"errcode": "4103", "errmsg": "newapptk获取失败"})
        # 获取html文本 模拟行为 可省略
        url = "https://kyfw.12306.cn/otn/index/initMy12306"
        headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies])
        request = self.request(url, method="GET", headers=headers)
        try:
            yield self.fetch(request)                           # 仅发送请求就行
        except Exception as e:
            pass
        # 返回登录成功的返回值
        raise tornado.gen.Return({"errcode":"0","errmsg":"用户名获取成功","cookies":self.cookies,"username":user_name})

    @tornado.gen.coroutine
    def check_remote_login(self):
        """
        判断远程12306端是否登录
        return True or False
        """
        url = "https://kyfw.12306.cn/otn/login/checkUser"       # 创建url
        data = "_json_att="                                     # 创建请求头信息
        self.headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies])
        request = self.request(url,method="POST",headers=self.headers,body=data)
        a = 1
        while a <= 3:
            try:
                resp = yield self.fetch(request)                # 发送请求 获取返回值
            except Exception as e:
                a += 1
                continue
            data = json.loads(resp.body)                        # 解析数据
            if not data["data"]["flag"]:                        # 判断是否登陆成功
                print resp.body
                time.sleep(1)
                a += 1
                continue
            else:
                raise tornado.gen.Return(True)
        print "预定验证登录失败"
        raise tornado.gen.Return(False)
