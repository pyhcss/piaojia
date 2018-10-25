# coding=utf-8

import os

# app配置
settings = {
    "debug":True,
    "xsrf_cookies":True,
    "static_path":os.path.join(os.path.dirname(__file__),"static"),
    "cookie_secret":"2icZdSTxQdOkm1dnTv8oJrxlV/ZQQk1nnw+2Zp3+rkE=",
}

# mysql配置
db_conf = {
    "host":"127.0.0.1",
    "database":"piaojia",
    "user":"root",
    "password":"******",
    "time_zone":"+8:00",
}

# redis配置
redis_conf = {
    "host":"127.0.0.1",
    "port":6379,
}

GLOBAL_WORD = u"******"                  # 口令
                                            # token
GLOBAL_TOKEN = "******"
SESSION_MAX_TIME = 60*60*24*3               # session有效期
