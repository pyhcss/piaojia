# coding=utf-8

import time
import json
import redis
import pymysql
import threading
from Queue import Queue
from send_email import sendemail
from orderthread import OrderThread

THREAD_SWITCH_DICT = {}                                 # 线程开关字典


class AutoOrder(object):
    """自动化下单主线程"""
    def __init__(self):
        """初始化函数"""
        global THREAD_SWITCH_DICT,THREAD_RETURN_DICT
        self.redis_cli = redis.StrictRedis()            # redis mysql数据库链接
        self.db_cli = pymysql.Connection(host="127.0.0.1", user="root",
                                         password="",database="piaojia",
                                         port=3306,charset='utf8')
        self.cursor = self.db_cli.cursor()              # mysql游标
        self.thread_switch_dict = THREAD_SWITCH_DICT    # 开关字典
        self.switch_lock = threading.Lock()             # 开关字典锁
        self.return_queue = Queue()                     # 创建queue队列对象

    def start_thread(self):
        """读取需要开启的线程 传递参数开启线程"""
        global THREAD_SWITCH_DICT
        while True:                                     # 设定死循环
            start_count = self.redis_cli.llen("piaojia_new_order")
            if start_count != 0:                        # 从redis查询数据
                json_data = self.redis_cli.lpop("piaojia_new_order")
                data = json.loads(json_data)            # 解析数据
                self.switch_lock.acquire()              # 设定开关为打开状态
                self.thread_switch_dict[str(data["id"])] = True
                self.switch_lock.release()              # 开启多线程
                order_thread = OrderThread(self.thread_switch_dict,self.switch_lock,
                                           self.return_queue,data)
                order_thread.start()                    # 运行多线程
                self.cursor.execute("update order_info set oi_status=1 where id=%s",data["id"])
                self.db_cli.commit()                    # 更新订单状态为抢票中
            else:
                break

    def end_thread(self):
        """读取需要结束的线程、把开关设为False"""
        while True:                                     # 设定死循环
            end_count = self.redis_cli.llen("piaojia_end_order")
            if end_count != 0:                          # 读取需要结束的线程
                order_id = self.redis_cli.lpop("piaojia_end_order")
                self.switch_lock.acquire()              # 关闭订单开关
                self.thread_switch_dict[str(order_id)] = False
                self.switch_lock.release()
            else:
                break

    def return_thread(self):
        """读取返回值队列,根据返回值处理相应操作,删除开关,删除返回值列表的值"""
        while True:                                     # 设定死循环
            if not self.return_queue.empty():           # 判断队列是否为空
                data_dict = self.return_queue.get()     # 获取队列数据
                if data_dict["data"]:                   # 更新订单状态
                    self.cursor.execute("update order_info set oi_status=2 where id=%s",data_dict["id"])
                    self.db_cli.commit()                # 发送邮件提醒
                    resp = sendemail(data_dict["data"]["email"],data_dict["data"]["from"]+"-"+data_dict["data"]["to"])
                    print resp
                else:                                   # 更新结束状态
                    self.cursor.execute("update order_info set oi_status=4 where id=%s",data_dict["id"])
                    self.db_cli.commit()
                self.switch_lock.acquire()              # 删除开关数据
                del self.thread_switch_dict[str(data_dict["id"])]
                self.switch_lock.release()
            else:
                break

    def main(self):
        """控制函数"""
        try:                                            # 设定死循环不断读取
            global THREAD_SWITCH_DICT                   # 需要执行或者结束的
            while True:                                 # 订单 做出响应处理
                self.start_thread()
                self.end_thread()
                self.return_thread()
                time.sleep(3)
        except Exception as e:
            print e
        finally:
            self.cursor.close()
            self.db_cli.close()


if __name__ == "__main__":
    auto_order = AutoOrder()
    auto_order.main()
