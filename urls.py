# coding=utf-8

import os

from tornado.web import StaticFileHandler
from handlers.loginhandler import *
from handlers.selecthandler import *
from handlers.orderhandler import *

urls = [
    (r"^/api/token",CheckTokenHandler),                     # 验证内部口令
    (r"^/api/imagecode",ImageCodeHandler),                  # 获取图片验证码
    (r"^/api/login",LoginHandler),                          # 校验登录
    (r"^/api/homelogin",IndexLoginHandler),                 # 用户主页判断用户是否登录
    (r"^/api/trainsinfo",SelectTrainHandler),               # 查询提交订单页的数据
    (r"^/api/personsinfo",SelectPersonHandler),             # 查询常用联系人信息
    (r"^/api/updatepersons",SelectPersonHandler),           # 更新常用联系人信息
    (r"^/api/submitorder",OrderInfoHandler),                # 提交订单
    (r"^/api/myorder",OrderInfoHandler),                    # 查询订单
    (r"^/api/commentorder",UpdateOrderHandler),             # 评价订单
    (r"^/api/cancelorder",UpdateOrderHandler),              # 取消订单
    (r"^/(.*)",StaticFileHandler,{"path":os.path.join(os.path.dirname(__file__),"static/html"),
                                  "default_filename":"index.html"})
]