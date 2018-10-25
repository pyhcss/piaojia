# coding=utf-8

import uuid
import json
from conf import SESSION_MAX_TIME


class Session(object):
    """自定义session类"""
    def __init__(self,requesthandler):
        self.requesthandler = requesthandler
        self.session_id = self.requesthandler.get_secure_cookie("session_id")
        if self.session_id == None:                     # 用户没有session_id
            self.session_id = uuid.uuid4().get_hex()    # 生成session_id
            self.data = {}                              # 初始化data为空
        else:                                           # 用户已有session_id
            try:                                        # 获取数据库数据
                data = self.requesthandler.redis.get("piaojia_session_%s" %self.session_id)
            except Exception as e:
                print e                                 # 出错默认数据为空
                self.data = {}
            else:
                if not data:                            # 数据过期的情况
                    self.data = {}
                else:                                   # 正常情况
                    self.data = json.loads(data)

    def save(self):
        try:
            self.requesthandler.redis.setex("piaojia_session_%s" %self.session_id,SESSION_MAX_TIME,json.dumps(self.data,ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            print e
            raise Exception("save session error")
        else:
            self.requesthandler.set_secure_cookie("session_id",self.session_id,expires_days=2)

    def clear(self):
        self.requesthandler.clear_cookie("session_id")
        try:
            self.requesthandler.redis.delete("piaojia_session_%s" %self.session_id)
        except Exception as e:
            pass


# if __name__ == "__main__":
    # session = Session(self)
    # session.data["key"] = value
    # session.save()
    # session.clear()