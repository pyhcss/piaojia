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
        self.thread_switch_dict = THREAD_SWITCH_DICT        # 开关字典
        self.switch_lock = switch_lock                      # 字典锁
        self.return_queue = return_queue                    # 返回值队列
        self.data = data                                    # 数据
        self.cookie = cookielib.CookieJar()                 # 构建cookiejar对象 用来保存cookie对象
        for i in self.data["cookies"]:                      # 添加自定义cookie
                self.cookie.set_cookie(self.make_cookie(i,self.data["cookies"][i]))
        cookie_handler = urllib2.HTTPCookieProcessor(self.cookie)# 构建自定义cookie处理器对象 用来处理cookie
        self.opener = urllib2.build_opener(cookie_handler)  # 构建opener
        self.setDaemon(True)                                # 主停子停

    def run(self):
        """订单线程执行函数"""
        print "订单"+str(self.data["id"])+"开始执行"          # 打印开始执行
        submit_order = SubmitOrder(self.opener)             # 生成提交订单对象
        resp = submit_order.check_uamtk(self.data["cookies"]["tk"])  # uamtk检测
        if resp != "0":                                     # 登录过期返回
            self.return_queue.put({"id": self.data["id"], "data": False})
            print "订单" + str(self.data["id"]) + "结束执行1-登录过期"
            return
        print "uamtk检测成功"
        while True:
            try:
                self.switch_lock.acquire()                  # 开关上锁
                if not self.thread_switch_dict[str(self.data["id"])]:# 查询开关数据 是否取消
                    self.switch_lock.release()              # 开关解锁
                    self.return_queue.put({"id": self.data["id"],"data":False})
                    print "订单" + str(self.data["id"]) + "结束执行2-开关关闭"
                    return                                  # 直接return
                self.switch_lock.release()                  # 解锁开关
                now_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                if now_time > self.data["date"]:            # 判断时间是否过期
                    self.return_queue.put({"id": self.data["id"], "data": False})
                    print "订单" + str(self.data["id"]) + "结束执行3-时间过期"
                    return
                                                            # 创建查票类对象
                get_train = GetTrain(self.data["date"],self.data["from_code"],self.data["to_code"],self.opener)
                resp = get_train.query_all_trains()         # 调用查票接口
                if resp["errcode"] == "0":                  # 拿到车票信息 格式化数据
                    resp_data = get_train.get_submit_data(self.data["trains"].split(","),self.data["seats"].split(","),
                                                           len(self.data["persons"].split(",")),resp["data"])
                    if resp_data["errcode"] != "0":
                        time.sleep(2)
                        continue
                    else:                                   # 保存符合情况的车票及座位信息
                        train_data = resp_data["data"]
                        seat = resp_data["seat"]
                else:
                    time.sleep(2)
                    continue                                # 判断时间是否超限
                now_time = time.strftime('%H:%M', time.localtime(time.time()))
                if now_time <= "06:00" or now_time >= "22:45":# 不在时间范围时重新查票
                    time.sleep(30)
                    continue
                                                            # 创建提交订单的对象
                resp = submit_order.checklogin()            # 检查是否登录
                if resp != "0":                             # 登录过期返回
                    self.return_queue.put({"id": self.data["id"], "data": False})
                    print "订单" + str(self.data["id"]) + "结束执行4-登录过期"
                    return
                                                            # 获取预定页面
                resp = submit_order.destine(train_data[0],self.data["date"],self.data["from"],self.data["to"])
                if resp != "0":
                    time.sleep(2)
                    continue
                token_key = submit_order.get_token()        # 获取全局token及key
                if not token_key:
                    time.sleep(2)
                    continue
                                                            # 获取常用联系人信息
                person_list = submit_order.get_persons(self.data["persons"].split(","))
                if not person_list:
                    time.sleep(2)
                    continue
                                                            # 乘车人信息预提交
                resp = submit_order.order_person_submit(seat,person_list,token_key)
                if resp["errcode"] != "0":
                    time.sleep(2)
                    continue
                person_info = resp["data"]
                                                            # 订票车次提交
                resp = submit_order.order_train_submit(self.data["date"],train_data,person_info,token_key)
                if resp != "0":
                    time.sleep(2)
                    continue
                                                            # 最终提交预定信息
                resp = submit_order.order_submit(person_info,token_key,train_data)
                if resp != "0":
                    time.sleep(2)
                    continue
                                                            # 查询预定情况
                resp = submit_order.query_submit(token_key)
                if resp != "0":
                    time.sleep(2)
                    continue
                                                            # 预定成功 添加数据到返回值队列
                print "订单" + str(self.data["id"]) + "结束执行5-已抢到"
                self.return_queue.put({"id": self.data["id"], "data": self.data})
                return                                      # 结束函数
            except Exception as e:
                continue

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


