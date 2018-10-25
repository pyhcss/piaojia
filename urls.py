# coding=utf-8

import os

from tornado.web import StaticFileHandler
from handlers.loginhandler import *

urls = [
    (r"^/api/token",CheckTokenHandler),                     # 验证内部口令
    (r"^/api/imagecode",ImageCodeHandler),                  # 获取图片验证码
    (r"^/api/login",LoginHandler),                          # 校验登录
    (r"^/api/homelogin",IndexLoginHandler),                 # 用户主页判断用户是否登录
    (r"^/(.*)",StaticFileHandler,{"path":os.path.join(os.path.dirname(__file__),"static/html"),
                                  "default_filename":"index.html"})
]