# coding=utf-8

import re
import tornado.gen
from libs.session import Session
from basehandler import BaseHandler
from libs.check_login import CheckLogin
from libs.query_info import QueryTrain,QueryPerson


class SelectTrainHandler(BaseHandler):
    """查询列车数据"""
    @tornado.gen.coroutine
    def get(self):
        """查询列车数据"""
        session_data = self.get_current_user()          # 判断是否本站登录
        if not session_data:                            # 返回未登录信息
            raise tornado.gen.Return(self.write({"errcode": "4101", "errmsg": "False"}))
        date = self.get_argument("date","")             # 接收客户端数据
        from_station = self.get_argument("from","")
        to_station = self.get_argument("to","")         # 判断数据正确性
        if not all((date,from_station,to_station,re.match(r"^\d{4}-\d{2}-\d{2}$",date))):
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "参数错误"}))
        try:                                            # 从数据库读取车站代号
            from_dict = self.db.get("select ts_name_code from train_station where ts_name=%s",from_station.replace(" ","").replace(u"站","").replace(u"市",""))
            to_dict = self.db.get("select ts_name_code from train_station where ts_name=%s",to_station.replace(" ","").replace(u"站","").replace(u"市",""))
        except Exception as e:
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "出发地或目的地错误"}))
        if not all((from_dict,to_dict)):                # 获取不到返回错误信息
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "出发地或目的地错误"}))
        query_train = QueryTrain(date,from_dict["ts_name_code"],to_dict["ts_name_code"])
        resp = yield query_train.get_submit_data()      # 发送请求并格式化数据
        raise tornado.gen.Return(self.write(resp))      # 返回格式化完成的数据


class SelectPersonHandler(BaseHandler):
    """常用联系人信息"""
    @tornado.gen.coroutine
    def check_login(self):
        """检查是否远程登录"""
        session_data = self.get_current_user()          # 调用session
        if not session_data:                            # 返回未登录信息
            raise tornado.gen.Return({"errcode": "4101", "errmsg": "False"})
        cookies = session_data["cookies"]               # 拿到缓存的cookie
        check_login = CheckLogin(cookies)
        resp = yield check_login.check_remote_login()   # 发送请求
        if not resp:                                    # 确认远程端是否登录
            raise tornado.gen.Return({"errcode": "4101", "errmsg": "False"})
        raise tornado.gen.Return({"errcode":"0","errmsg":"True","session_data":session_data})

    @tornado.gen.coroutine
    def get(self):
        """查询常用联系人信息"""
        resp = yield self.check_login()                 # 查询远程端是否登录
        if resp["errcode"] != "0":
            raise tornado.gen.Return(self.write(resp))  # 没登录返回错误信息
        user_id = resp["session_data"]["user_id"]       # 根据用户id查询数据库
        persons = self.db.query("select pi_name from person_info where pi_user=%s",user_id)
        if persons:                                     # 如果有数据 直接格式化并返回数据
            persons = [{"name":i["pi_name"]} for i in persons]
            raise tornado.gen.Return(self.write({"errcode":"0","errmsg":"常用联系人获取成功","persons":persons}))
        cookies = resp["session_data"]["cookies"]       # 如果没有数据 取出cookie
        query_person = QueryPerson(cookies)
        resp = yield query_person.get_persons()         # 调用接口查询数据
        if resp["errcode"] == "0":                      # 返回值正确时直接插入数据库
            for i in resp["data"]:                      # 返回正确信息
                self.db.execute("insert into person_info(pi_user,pi_name,pi_sex,pi_born_date,pi_idcard,"
                                "pi_type,pi_mobile,pi_email,pi_address) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                user_id,i["passenger_name"],"1" if i["sex_code"]=="M" else "0",i["born_date"],
                                i["passenger_id_no"],i["passenger_type"],i["mobile_no"],i["email"],i["address"])
            raise tornado.gen.Return(self.write({"errcode":"0","errmsg":"常用联系人获取成功","persons":[{"name":i["passenger_name"]} for i in resp["data"]]}))
        else:                                           # 返回错误信息
            raise tornado.gen.Return(self.write({"errcode":"4101","errmsg":"第三方系统错误"}))

    @tornado.gen.coroutine
    def post(self):
        """更新常用联系人信息"""
        resp = yield self.check_login()                 # 查询是否登录
        if resp["errcode"] != "0":
            raise tornado.gen.Return(self.write(resp))  # 返回错误信息
        user_id = resp["session_data"]["user_id"]       # 从session拿到用户id和cookie
        cookies = resp["session_data"]["cookies"]
        query_person = QueryPerson(cookies)
        resp = yield query_person.get_persons()         # 调用接口查询数据
        if resp["errcode"] == "0":                      # 从数据库获取已有常用联系人的信息
            person_list = self.db.query("select pi_name from person_info where pi_user=%s",user_id)
            sql_persons = [i["pi_name"] for i in person_list]         # 生成名字列表
            resp_persons = [i["passenger_name"] for i in resp["data"]]# 从返回值数据中生成名字列表
            persons_name = [i for i in resp_persons if i not in sql_persons]# 求数据库没有的名字
            if not persons_name:                        # 如果差集为空 直接返回数据
                raise tornado.gen.Return(self.write({"errcode":"0","errmsg":"常用联系人更新成功","persons":[{"name":i} for i in resp_persons]}))
            for i in resp["data"]:                      # 否则更新数据库中没有的数据
                if i["passenger_name"] in persons_name: # 组合数据返回
                    self.db.execute("insert into person_info(pi_user,pi_name,pi_sex,pi_born_date,pi_idcard,"
                                    "pi_type,pi_mobile,pi_email,pi_address) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                    user_id,i["passenger_name"],"1" if i["sex_code"]=="M" else "0",i["born_date"],
                                    i["passenger_id_no"],i["passenger_type"],i["mobile_no"],i["email"],i["address"])
            raise tornado.gen.Return(self.write({"errcode":"0","errmsg":"常用联系人更新成功","persons":[{"name":i} for i in list(set(sql_persons+resp_persons))]}))
        else:                                           # 返回错误信息
            raise tornado.gen.Return(self.write({"errcode":"4101","errmsg":"第三方系统错误"}))
