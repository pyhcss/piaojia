# coding=utf-8

import time
import urllib2
import threading
import cookielib
from querytrains import GetTrain
from submitorder import SubmitOrder


class OrderThread(threading.Thread):
    """订单线程"""
    def __init__(self,THREAD_SWITCH_DICT,switch_lock,return_queue,data,*args,**kwargs):
        super(OrderThread,self).__init__(*args,**kwargs)
        self.thread_switch_dict = THREAD_SWITCH_DICT
        self.switch_lock = switch_lock
        self.return_queue = return_queue
        self.data = data
        self.cookie = cookielib.CookieJar()                 # 构建cookiejar对象 用来保存cookie对象
        for i in self.data["cookies"]:
            self.cookie.set_cookie(self.make_cookie(i,self.data["cookies"][i]))
        cookie_handler = urllib2.HTTPCookieProcessor(self.cookie)# 构建自定义cookie处理器对象 用来处理cookie
        self.opener = urllib2.build_opener(cookie_handler)  # 构建opener

    def run(self):
        """订单线程执行函数"""
        print "订单"+str(self.data["id"])+"开始执行"
        while True:
            self.switch_lock.acquire()                      # 开关上锁
            if not self.thread_switch_dict[str(self.data["id"])]:# 查询开关数据 是否取消
                self.switch_lock.release()                  # 开关解锁
                self.return_queue.put({"id": self.data["id"],"data":False})
                print "订单" + str(self.data["id"]) + "结束执行1-开关关闭"
                return                                      # 直接return
            self.switch_lock.release()                      # 解锁开关
            now_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            if now_time > self.data["date"]:
                self.return_queue.put({"id": self.data["id"], "data": False})
                print "订单" + str(self.data["id"]) + "结束执行2-时间过期"
                return
            # 调用查票接口    返回符合情况的车票 保存车票信息
            get_train = GetTrain(self.data["date"],self.data["from_code"],self.data["to_code"],self.opener)
            resp = get_train.query_all_trains()
            if resp["errcode"] == "0":
                resp_data = get_train.get_submit_data(self.data["trains"].split(","),self.data["seats"].split(","),
                                                       len(self.data["persons"].split(",")),resp["data"])
                if resp_data["errcode"] != "0":
                    continue
                else:
                    train_data = resp_data["data"]
                    seat = resp_data["seat"]
            else:
                continue
            now_time = time.strftime('%H:%M', time.localtime(time.time()))
            if now_time <= "06:00" or now_time >= "22:45":
                continue
            # 检查是否登录    未登录则抢票失败    未登录返回return
            submit_order = SubmitOrder(self.opener)
            resp = submit_order.checklogin()
            if resp != "0":
                self.return_queue.put({"id": self.data["id"], "data": False})
                print "订单" + str(self.data["id"]) + "结束执行3-登录过期"
                return
            # 跳转预定
            resp = submit_order.destine(train_data[0],self.data["date"],self.data["from"],self.data["to"])
            if resp != "0":
                continue
            # 获取全局token及key
            token_key = submit_order.get_token()
            if not token_key:
                continue
            # 获取常用联系人信息
            person_list = submit_order.get_persons(self.data["persons"].split(","))
            if not person_list:
                continue
            # 乘车人信息预提交
            resp = submit_order.order_person_submit(seat,person_list,token_key)
            if resp["errcode"] != "0":
                continue
            person_info = resp["data"]
            # 订票车次提交
            resp = submit_order.order_train_submit(self.data["date"],train_data,person_info,token_key)
            if resp != "0":
                continue
            # 最终提交预定信息
            resp = submit_order.order_submit(person_info,token_key,train_data)
            if resp != "0":
                continue
            # 查询预定情况
            resp = submit_order.query_submit(token_key)
            if resp != "0":
                continue
            # 预定成功 添加数据到返回值队列
            print "订单" + str(self.data["id"]) + "结束执行4-已抢到"
            self.return_queue.put({"id": self.data["id"], "data": self.data})
            # 结束函数
            return

    def make_cookie(self,name,value):
        return cookielib.Cookie(
            version=None,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain="",
            domain_specified=False,
            domain_initial_dot=False,
            path="/",
            path_specified=False,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest=None,
        )


