# coding=utf-8


import json
import tornado.gen
from basehandler import BaseHandler
from libs.decorate import check_islogin


class OrderInfoHandler(BaseHandler):
    """订单类"""
    @check_islogin
    def post(self):
        """接收客户端数据、存入数据库并执行订单"""
        try:
            from_station = self.json_args["from"]       # 从客户端接受参数
            to_station = self.json_args["to"]
            date = self.json_args["date"]
            trains = self.json_args["trains"]
            seats = self.json_args["seats"]
            persons = self.json_args["persons"]
            email = self.json_args["email"]
        except Exception as e:                          # 参数异常
            raise tornado.gen.Return(self.write({"errcode":"4103","errmsg":"参数错误"}))
        if not all((from_station,to_station,date,trains,seats,persons,email)):
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "参数错误"}))
        try:                                            # 从数据库读取车站代号
            from_dict = self.db.get("select ts_name_code from train_station where ts_name=%s",from_station.replace(" ","").replace(u"站","").replace(u"市",""))
            to_dict = self.db.get("select ts_name_code from train_station where ts_name=%s",to_station.replace(" ","").replace(u"站","").replace(u"市",""))
        except Exception as e:                          # 数据库异常
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "出发地或目的地错误"}))
        if not all((from_dict,to_dict)):                # 获取不到返回错误信息
            raise tornado.gen.Return(self.write({"errcode": "4103", "errmsg": "出发地或目的地错误"}))
        from_code = from_dict["ts_name_code"];to_code = to_dict["ts_name_code"]
        session_data = self.get_current_user()          # 调用session
        user_id = session_data["user_id"]               # 获取用户id和cookie数据
        cookies = session_data["cookies"]               # 插入订单信息
        order_id = self.db.execute("insert into order_info(oi_user,oi_from,oi_from_code,oi_to,oi_to_code,"
                        "oi_date,oi_trains,oi_seats,oi_persons,oi_email) values(%s,%s,%s,%s,%s,"
                        "%s,%s,%s,%s,%s)",user_id,from_station,from_code,to_station,to_code,date,
                        trains,seats,persons,email)     # 组合后台系统所需信息
        order = {"id":order_id,"user_id":user_id,"from":from_station,"from_code":from_code,"to":to_station,"to_code":to_code,"date":date,"trains":trains,"seats":seats,"persons":persons,"email":email,"cookies":cookies}
        order_info = json.dumps(order,ensure_ascii=False).encode("utf-8")
        self.redis.lpush("piaojia_new_order",order_info)# 发送到后台
        raise tornado.gen.Return(self.write({"errcode":"0","errmsg":"订单提交成功"}))

    def get(self):
        """查询订单信息"""
        session_data = self.get_current_user()
        if not session_data:                            # 没有session数据代表未登录
            return self.write({"errcode": "4101", "errmsg": "False"})
        user_id = session_data["user_id"]               # 获取用户id 查询数据库
        orders = self.db.query("select id as order_id,oi_from,oi_to,oi_date,oi_trains as order_trains,"
                               "oi_seats as order_seats,oi_persons as order_persons,oi_email as order_email,"
                               "oi_status as order_status,oi_comment,oi_ctime from order_info where "
                               "oi_user=%s order by id desc",user_id)
        if orders:                                      # 查到订单数据后
            for i in orders:                            # 组合数据并返回
                i["order_address"] = i["oi_from"]+"-"+i["oi_to"]
                i["order_date"] = i["oi_date"].strftime('%Y-%m-%d')
                i["order_comment"] = i["oi_comment"] if i["oi_comment"] else ""
                i["order_cdate"] = i["oi_ctime"].strftime('%Y-%m-%d %H:%M:%S')
                del i["oi_from"];del i["oi_to"];del i["oi_date"];del i["oi_comment"];del i["oi_ctime"]
        return self.write({"errcode":"0","errmsg":"订单获取成功","orders":orders})


class UpdateOrderHandler(BaseHandler):
    """取消订单及评价"""
    def post(self):
        """评价"""
        session_data = self.get_current_user()
        if not session_data:                            # 判断用户是否登录
            return self.write({"errcode": "4101", "errmsg": "False"})
        try:                                            # 获取用户数据
            order_id = self.json_args["order_id"]
            comment = self.json_args["comment"]
            user_id = session_data["user_id"]
        except Exception as e:
            return self.write({"errcode":"4103","errmsg":"参数错误"})
        if not all((order_id,comment,user_id)):
            return self.write({"errcode": "4103", "errmsg": "参数错误"})
        try:                                            # 更新用户评价
            self.db.execute("update order_info set oi_status=3,oi_comment=%s "
                            "where id=%s and oi_user=%s",comment,order_id,user_id)
        except Exception as e:
            return self.write({"errcode":"4001","errmsg":"系统错误"})
        return self.write({"errcode":"0","errmsg":"评价成功"})

    def get(self):
        """取消订单"""
        session_data = self.get_current_user()
        if not session_data:                            # 判断登录情况
            return self.write({"errcode": "4101", "errmsg": "False"})
        try:                                            # 获取用户数据
            order_id = self.get_argument("order_id","")
            user_id = session_data["user_id"]
        except Exception as e:
            return self.write({"errcode": "4103", "errmsg": "参数错误"})
        if not all((order_id,user_id)):
            return self.write({"errcode": "4103", "errmsg": "参数错误"})
        try:                                            # 查询订单数据
            order = self.db.get("select id from order_info where id=%s and oi_user=%s",order_id,user_id)
        except Exception as e:
            return self.write({"errcode": "4001", "errmsg": "系统错误"})
        if not order:                                   # 返回错误信息
            return self.write({"errcode": "4105", "errmsg": "用户身份错误"})
        self.redis.lpush("piaojia_end_order",order["id"])# 后台发送数据停止线程
        return self.write({"errcode":"0","errmsg":"取消成功"})