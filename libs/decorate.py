# coding=utf-8

import tornado.gen
from conf import GLOBAL_TOKEN
from libs.check_login import CheckLogin

def check_token(fun):
    """token检查装饰器"""
    @tornado.gen.coroutine
    def warpper(self,*args,**kwargs):
        token = self.get_secure_cookie("token")
        if (not token) or (token != GLOBAL_TOKEN):
            raise tornado.gen.Return(self.write({"errcode":"4105","errmsg":"身份验证不通过"}))
        yield fun(self,*args,**kwargs)
    return warpper


def check_islogin(fun):
    """检查登录装饰器"""
    @tornado.gen.coroutine
    def warpper(self,*args,**kwargs):
        session_data = self.get_current_user()              # 调用session
        if not session_data:                                # 返回未登录信息
            raise tornado.gen.Return(self.write({"errcode": "4101", "errmsg": "False"}))
        cookies = session_data["cookies"]                   # 拿到缓存的cookie
        check_login = CheckLogin(cookies)
        resp = yield check_login.check_remote_login()       # 发送请求
        if not resp:                                        # 确认远程端是否登录
            raise tornado.gen.Return(self.write({"errcode": "4101", "errmsg": "False"}))
        yield fun(self,*args,**kwargs)
    return warpper