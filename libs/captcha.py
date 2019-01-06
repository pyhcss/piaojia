# coding=utf-8

import re
import time
import json
import random
import tornado.gen
from base_httpclient import Base_Httpclient


class Captcha(Base_Httpclient):
    """获取12306验证码"""
    def __init__(self,*args,**kwargs):
        super(Captcha,self).__init__(*args,**kwargs)

    def format_captcha(self,value):
        """
        格式化验证码文本
        value: "158" 用户输入的验证码代号
        return: "152,45,54,125" 服务器需要的验证码文本
        """
        text_list = []
        if "1" in value:                                    # 判断输入内容把值加入列表
            text_list.append(str(random.randint(30, 40)))
            text_list.append(str(random.randint(40, 50)))
        if "2" in value:
            text_list.append(str(random.randint(30, 40)))
            text_list.append(str(random.randint(110, 120)))
        if "3" in value:
            text_list.append(str(random.randint(107, 115)))
            text_list.append(str(random.randint(40, 50)))
        if "4" in value:
            text_list.append(str(random.randint(107, 115)))
            text_list.append(str(random.randint(110, 120)))
        if "5" in value:
            text_list.append(str(random.randint(180, 185)))
            text_list.append(str(random.randint(40, 50)))
        if "6" in value:
            text_list.append(str(random.randint(180, 185)))
            text_list.append(str(random.randint(110, 120)))
        if "7" in value:
            text_list.append(str(random.randint(248, 260)))
            text_list.append(str(random.randint(40, 50)))
        if "8" in value:
            text_list.append(str(random.randint(248, 260)))
            text_list.append(str(random.randint(110, 120)))
        return "%2C".join(text_list)                         # 拼接列表组成验证码文本

    @tornado.gen.coroutine
    def get_captcha(self):
        """
        获取12306验证码
        return: {"cookies":{},"image":"图片二进制数据"}
        """
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&"+str(time.time())+"&callback=jQuery1910471916584"+str(random.randint(0,999999)).zfill(6)+"_"+str(time.time())+"&_="+str(time.time())
        if self.cookies:
            self.headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies])
        request = self.request(url,headers=self.headers,request_timeout=3)    # 构建请求对象
        while True:
            try:
                resp = yield self.fetch(request)            # 发送请求拿到响应
                json_data = re.search(r".*?(\{.*\})\);",resp.body).group(1)
                callback = re.search(r"\/\*\*\/(.*?)\(.*\);",resp.body).group(1)
                data = json.loads(json_data)                    # 解析数据
            except Exception as e:
                continue                                    # 提取返回数据
            if data["result_code"] != "0":
                continue                                    # 拿到图片数据
            else:
                break
        try:
            if self.cookies:                                # 处理cookie
                self.cookies = self.format_cookies(resp.headers["Set-Cookie"],self.cookies)
            else:
                self.cookies = self.format_cookies(resp.headers["Set-Cookie"])
        except Exception as e:
            pass
        self.cookies["callback"] = callback                 # 返回cookie 返回base64数据
        raise tornado.gen.Return({"cookies":self.cookies,"data":data["image"]})

    @tornado.gen.coroutine
    def check_captcha(self,value):
        """
        校验验证码
        cookies 验证码id {"":""} 服务器设置的键值对
        value 验证码值 "" 用户输入的文本值
        """
        text = self.format_captcha(value)                   # 拿到格式化好的验证码
        url = "https://kyfw.12306.cn/passport/captcha/captcha-check?callback="+self.cookies["callback"]+"&answer="+text+"&rand=sjrand&login_site=E&_="+str(time.time())
        self.headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies if i != "callback"])
        self.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        self.headers["X-Requested-With"] = "XMLHttpRequest"
        request = self.request(url,headers=self.headers,request_timeout=5)
        try:
            resp = yield self.fetch(request)            # 发送请求拿到响应
            json_data = re.search(r".*?(\{.*\})\);", resp.body).group(1)
            data = json.loads(json_data)                        # 解析数据
        except Exception as e:
            raise tornado.gen.Return({"errcode":"4103","errmsg":"验证码校验失败","cookies":self.cookies})
        try:                                                # 处理cookie
            self.cookies = self.format_cookies(resp.headers["Set-Cookie"],self.cookies)
        except Exception as e:
            pass                                            # 提取数据
        if data["result_code"] != "4":
            print resp.body                                 # 返回校验失败
            raise tornado.gen.Return({"errcode":"4103","errmsg":"验证码校验失败","cookies":self.cookies})
        self.cookies["captcha_text"] = text
        # "7" 验证码已过期 "5" 验证码错误 "4" 验证码校验成功 "8" 信息为空     # 返回数据
        raise tornado.gen.Return({"errcode":"0","errmsg":"验证码校验成功","cookies":self.cookies})