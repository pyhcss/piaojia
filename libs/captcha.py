# coding=utf-8

import json
import random
import urllib
import tornado.gen
from base_httpclient import Base_Httpclient


class Captcha(Base_Httpclient):
    """获取12306验证码"""
    def __init__(self,*args,**kwargs):
        super(Captcha,self).__init__(*args,**kwargs)
        self.headers["Referer"] = "https://kyfw.12306.cn/otn/login/init"

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
        return ",".join(text_list)                          # 拼接列表组成验证码文本

    @tornado.gen.coroutine
    def get_captcha(self):
        """
        获取12306验证码
        return: {"cookies":{},"image":"图片二进制数据"}
        """
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&" + str(random.random())
        if self.cookies:
            self.headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies])
        self.headers["Accept"] = "image/webp,image/*,*/*;q=0.8"
        request = self.request(url,headers=self.headers)    # 构建请求对象
        while True:
            try:
                resp = yield self.fetch(request)            # 发送请求拿到响应
            except Exception as e:
                continue
            else:
                break
        image_data = resp.body                              # 拿到图片数据
        try:
            if self.cookies:
                self.cookies = self.format_cookies(resp.headers["Set-Cookie"],self.cookies)
            else:
                self.cookies = self.format_cookies(resp.headers["Set-Cookie"])
        except Exception as e:
            pass
        raise tornado.gen.Return({"cookies":self.cookies,"image":image_data})

    @tornado.gen.coroutine
    def check_captcha(self,value):
        """
        校验验证码
        cookies 验证码id {"":""} 服务器设置的键值对
        value 验证码值 "" 用户输入的文本值
        """
        text = self.format_captcha(value)
        url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        data = {                                            # 创建数据内容
            "answer":text,                                  # 验证码值
            "login_site":"E",                               # 固定值
            "rand":"sjrand"                                 # 固定值
        }
        self.headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies])
        self.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        self.headers["X-Requested-With"] = "XMLHttpRequest"
        request = self.request(url,method="POST",headers=self.headers,body=urllib.urlencode(data))
        while True:
            try:
                resp = yield self.fetch(request)            # 发送请求拿到响应
            except Exception as e:
                continue
            else:
                break
        try:
            self.cookies = self.format_cookies(resp.headers["Set-Cookie"],self.cookies)
        except Exception as e:
            pass
        print resp.body
        # "7" 验证码已过期 "5" 验证码错误 "4" 验证码校验成功      # 返回数据
        raise tornado.gen.Return({"errcode":json.loads(resp.body)["result_code"],"cookies":self.cookies})