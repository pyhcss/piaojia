# coding=utf-8

import json
from submitorder import SubmitOrder

class Relogin(SubmitOrder):
    """重新登录类"""
    def authUamtk(self):
        """校验uamtk"""
        url = "https://kyfw.12306.cn/otn/uamauthclient"     # 创建url
        data = "appid=otn"                                  # 参数
        request = self.request(url,data=data,headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request,timeout=5).read()# 发送请求获取响应
                data = json.loads(resp)                         # 解析json数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "authUamtk校验失败"
                    return {"errcode":"404","errmsg":"authUamtk校验失败"}
            if data["result_code"] == 0:                        # 返回执行结果
                return {"errcode":"0","errmsg":"authUamtk校验成功","uamtk":data["newapptk"]}
            else:
                print data
                return {"errcode": "404", "errmsg": "authUamtk校验失败"}

    def userLogin(self):
        """重新获取12306服务器session"""
        url = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"
        request = self.request(url,headers=self.headers)
        count = 0
        while True:
            try:
                resp = self.opener.open(request, timeout=5).read()  # 发送请求获取响应
                data = json.loads(resp)  # 解析json数据
            except Exception as e:
                count += 1
                if count <= 3:
                    continue
                else:
                    print "session获取失败"
                    return "session error"
            if data["result_code"] == 0:
                return "0"              # 返回执行结果
            else:
                print data
                return "session error"

    def main(self):
        print "启动重新登录"
        resp = self.authUamtk()
        if resp["errcode"] != "0":
            return "relogin error"
        resp = self.userLogin()
        if resp != "0":
            return "relogin error"
        resp = self.authUamtk()
        if resp["errcode"] != "0":
            return "relogin error"
        resp = self.check_uamtk(resp["uamtk"])
        if resp == "0":
            return resp
        return "relogin error"

