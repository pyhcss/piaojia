# coding=utf-8

import tornado.gen
from conf import GLOBAL_TOKEN


def check_token(fun):
    """token检查装饰器"""
    @tornado.gen.coroutine
    def warpper(self,*args,**kwargs):
        token = self.get_secure_cookie("token")
        if (not token) or (token != GLOBAL_TOKEN):
            raise tornado.gen.Return(self.write({"errcode":"4105","errmsg":"身份验证不通过"}))
        yield fun(self,*args,**kwargs)
    return warpper