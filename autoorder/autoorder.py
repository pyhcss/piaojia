# coding=utf-8

import time
import json
import redis
import threading
from Queue import Queue
from send_email import sendemail
from orderthread import OrderThread
from automysql import AutoMySql

THREAD_SWITCH_DICT = {}                                 # 线程开关字典


class AutoOrder(object):
    """自动化下单主线程"""
    def __init__(self):
        """初始化函数"""
        global THREAD_SWITCH_DICT
        self.redis_cli = redis.StrictRedis()            # redis mysql数据库链接
        self.thread_switch_dict = THREAD_SWITCH_DICT    # 开关字典
        self.switch_lock = threading.Lock()             # 开关字典锁
        self.return_queue = Queue()                     # 创建queue队列对象
        self.automysql = AutoMySql()                    # 初始化自定义sql类


    def start_thread(self):
        """读取需要开启的线程 传递参数开启线程"""
        global THREAD_SWITCH_DICT
        while (self.redis_cli.llen("piaojia_new_order")!=0):# 从redis查询数据
            json_data = self.redis_cli.lpop("piaojia_new_order")
            data = json.loads(json_data)            # 解析数据
            self.switch_lock.acquire()              # 设定开关为打开状态
            self.thread_switch_dict[str(data["id"])] = True
            self.switch_lock.release()              # 开启多线程
            order_thread = OrderThread(self.thread_switch_dict,self.switch_lock,
                                       self.return_queue,data)
            order_thread.setDaemon(True)            # 设置线程为伴随线程
            order_thread.start()                    # 运行子线程
            self.automysql.autoExecute("update order_info set oi_status=1 where id=%s",data["id"])

    def end_thread(self):
        """读取需要结束的线程、把开关设为False"""
        while (self.redis_cli.llen("piaojia_end_order")!=0):# 读取需要结束的线程
            order_id = self.redis_cli.lpop("piaojia_end_order")
            self.switch_lock.acquire()              # 关闭订单开关
            self.thread_switch_dict[str(order_id)] = False
            self.switch_lock.release()

    def return_thread(self):
        """读取返回值队列,根据返回值处理相应操作,删除开关,删除返回值列表的值"""
        while (not self.return_queue.empty()): # 判断队列是否为空
            data_dict = self.return_queue.get()     # 获取队列数据
            if data_dict["data"]:                   # 更新订单状态
                self.automysql.autoExecute("update order_info set oi_status=2 where id=%s",data_dict["id"])
                                                    # 发送邮件提醒
                resp = sendemail(data_dict["data"]["email"],data_dict["data"]["from"]+"-"+data_dict["data"]["to"])
                print resp
            else:                                   # 更新结束状态
                self.automysql.autoExecute("update order_info set oi_status=4 where id=%s",data_dict["id"])
            self.switch_lock.acquire()              # 删除开关数据
            del self.thread_switch_dict[str(data_dict["id"])]
            self.switch_lock.release()

    def main(self):
        """控制函数"""
        try:                                            # 设定死循环不断读取
            while True:                                 # 订单 做出响应处理
                self.start_thread()
                self.end_thread()
                self.return_thread()
                time.sleep(1)
        except Exception as e:
            print e
        finally:
            self.automysql.autoExecute("update order_info set oi_status=4 where (oi_status=1 or oi_status=0)")


if __name__ == "__main__":
    auto_order = AutoOrder()
    auto_order.main()
