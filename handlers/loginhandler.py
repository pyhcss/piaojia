# coding=utf-8

import json
import tornado.web
import tornado.gen

from libs.session import Session
from libs.captcha import Captcha
from basehandler import BaseHandler
from libs.decorate import check_token
from libs.check_login import CheckLogin
from conf import GLOBAL_WORD,GLOBAL_TOKEN


class CheckTokenHandler(BaseHandler):
    """校验用户身份设置全局token"""
    def get(self):
        """验证及设置token"""
        token = self.get_argument("token","")           # 获取客户端口令
        token_key = self.get_secure_cookie("token")     # 获取客户端token值
        if (not token) and (not token_key):             # 如果都没有返回错误信息
            return self.write({"errcode":"4103","errmsg":"口令错误"})
        elif token == GLOBAL_WORD:                      # 如果其中某个正确返回正确信息
            self.set_secure_cookie("token", GLOBAL_TOKEN, expires_days=3)
            return self.write({"errcode": "0", "errmsg": "验证成功"})
        elif token_key == GLOBAL_TOKEN:
            return self.write({"errcode": "0", "errmsg": "验证成功"})
        else:                                           # 返回错误信息
            return self.write({"errcode": "4103", "errmsg": "口令错误"})


class ImageCodeHandler(BaseHandler):
    """获取12306验证码图片"""
    @tornado.gen.coroutine
    def get(self):
        """获取验证码"""
        captcha = Captcha()                             # 创建生成验证码对象
        dict_data = yield captcha.get_captcha()         # 获取验证码返回值
                                                        # 设置cookie 验证码校验值
        self.set_secure_cookie("captcha_id",json.dumps(dict_data["cookies"],ensure_ascii=False).encode("utf-8"))
        self.write(dict_data["image"])                  # 返回图片数据


class LoginHandler(BaseHandler):
    """执行登录"""
    @check_token
    @tornado.gen.coroutine
    def post(self):
        """校验登录"""
        try:                                            # 获取用户传递参数
            user_number = self.json_args["mobile"]      # 账号
            user_pwd = self.json_args["password"]       # 密码
            captcha_text = self.json_args["imagecode"]  # 验证码文本
            captcha_id = self.get_secure_cookie("captcha_id")# 获取cookie中远程cookie值
        except Exception as e:                          # 出现异常或参数错误返回
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "参数错误"}))
        if not captcha_id:
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "参数错误"}))
        captcha = Captcha()                             # 创建验证码对象
                                                        # 发送请求检验验证码值
        dict_data = yield captcha.check_captcha(json.loads(captcha_id),captcha_text)
        if dict_data["errcode"] == "7":                 # 验证码过期
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "验证码已过期"}))
        elif dict_data["errcode"] == "5":               # 验证码错误
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "验证码错误"}))
        elif dict_data["errcode"] == "4":               # 验证码正确
            check_login = CheckLogin()                  # 发送请求验证账号密码
            resp = yield check_login.get_uamtk(user_number,user_pwd,dict_data["cookies"])
            if resp["errcode"] == "0":                  # 账号密码正确
                                                        # 发送请求获取用户名
                resp = yield check_login.get_user_name(resp["cookies"])
                if resp["errcode"] == "0":              # 用户名获取成功 查询数据库
                    user = self.db.get("select id from user_info where ui_account=%s",user_number)
                    if user == None:                    # 如果无数据则插入
                        user_id = self.db.execute("insert into user_info(ui_name,ui_account,ui_pwd) values(%s,%s,%s)",resp["username"],user_number,user_pwd)
                    else:                               # 否则更新数据
                        self.db.execute("update user_info set ui_pwd=%s,ui_login=ui_login+1 where ui_account=%s",user_pwd,user_number)
                        user_id = user["id"]
                    session = Session(self)             # 创建session对象
                    session.data["user_name"] = resp["username"]
                    session.data["user_account"] = user_number
                    session.data["user_id"] = user_id
                    session.data["cookies"] = resp["cookies"]
                    session.save()                      # 写入数据并设置cookie
                    self.clear_cookie("captcha-id")     # 删除验证码验证数据 返回登录成功
                    raise tornado.gen.Return(self.write({"errcode": "0", "errmsg": "登录成功"}))
                else:
                    raise tornado.gen.Return(self.write({"errcode": "4106", "errmsg": "用户名或者密码错误"}))
            else:                                       # 账号密码错误
                raise tornado.gen.Return(self.write({"errcode": "4106", "errmsg": "用户名或密码错误"}))
        else:                                           # 验证码检验未知情况
            raise tornado.gen.Return(self.write({"errcode": "4301", "errmsg": "第三方错误,请及时联系管理员"}))


class IndexLoginHandler(BaseHandler):
    """用户主页判断用户是否登录"""
    def get(self):
        session_data = self.get_current_user()
        if session_data:
            return self.write({"errcode":"0","errmsg":"True","user_name":session_data["user_name"],"user_account":session_data["user_account"]})
        else:
            return self.write({"errcode":"4101","errmsg":"False"})