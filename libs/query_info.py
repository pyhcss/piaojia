# coding=utf-8

# import re
import json
import time
import urllib
import tornado.gen
from base_httpclient import Base_Httpclient


class QueryTrain(Base_Httpclient):
    """查询车次信息"""
    def __init__(self,date,from_code,to_code,*args,**kwargs):
        """
        初始化信息 格式化数据
        date:"2018-10-10"               出发时间 格式化数据
        from_station:"BJD"              出发站代号
        to_station:"TJN"                目的站代号
        """
        super(QueryTrain,self).__init__(*args,**kwargs)
        self.data = [                                       # 格式化查询信息
            {"leftTicketDTO.train_date": date},             # 出发日期
            {"leftTicketDTO.from_station": from_code},      # 出发站代号
            {"leftTicketDTO.to_station": to_code},          # 到达站代号
            {"purpose_codes": "ADULT"}                      # 固定值
        ]

    @tornado.gen.coroutine
    def select_trains(self):
        """
        发送请求获取所有余票信息
        return: {"errcode":"0","errmsg":"","data":"{"map",{},"result":["列车详情1","列车详情2"]}
        """
        url = "https://kyfw.12306.cn/otn/leftTicket/query?" # 构造url
        data_list = [urllib.urlencode(i) for i in self.data]# 遍历数据组成参数列表
        url += "&".join(data_list)                          # 拼接url
        request = self.request(url,headers=self.headers)    # 构建请求对象
        while True:
            try:
                resp = yield self.fetch(request)            # 发送请求 获取返回值
            except Exception as e:
                continue
            else:
                try:                                        # 服务器可能返回错误页面
                    data_dict = json.loads(resp.body)       # 解析json对象
                except Exception as e:
                    raise tornado.gen.Return({"errcode":"4301","errmsg":"第三方错误，请稍后重试"})
                if data_dict["httpstatus"] == 200:          # 正常状态返回码
                    raise tornado.gen.Return({"errcode":"0","errmsg":"列车信息获取成功","data":data_dict["data"]})# 返回数据
                else:                                       # 出错后重新执行
                    continue

    @tornado.gen.coroutine
    def get_submit_data(self):
        """
        执行查询数据并格式化成提交页需要的数据
        return:{"errcode":"","errmsg":"","trains":[{},{}]}
        """
        resp_data = yield self.select_trains()              # 获取获取到的信息
        if resp_data["errcode"] == "0":                     # 如果响应正确
            data = resp_data["data"]                        # 组合数据 格式化响应数据
            data_map = data["map"]
            new_data = []
            for i in data["result"]:
                info_list = i.split("|")
                info = {}
                info["id"] = info_list[3]
                info["address"] = data_map[info_list[6]]+"-"+data_map[info_list[7]]
                info["time"] = info_list[8]+"-"+info_list[9]
                new_data.append(info)                       # 返回查询信息
            raise tornado.gen.Return({"errcode":"0","errmsg":"格式化数据成功","trains":new_data})
        else:                                               # 直接返回查询响应
            raise tornado.gen.Return(resp_data)


class QueryPerson(Base_Httpclient):
    """获取12306常用联系人信息"""
    @tornado.gen.coroutine
    def get_persons(self):
        """获取常用联系人信息"""
        url = "https://kyfw.12306.cn/otn/passengers/query"
        data = "pageIndex=1&pageSize=20"
        self.headers["Cookie"] = ";".join([i + "=" + self.cookies[i] for i in self.cookies])
        request = self.request(url, method="POST", headers=self.headers, body=data)
        a = 1
        while a <= 3:
            try:
                resp = yield self.fetch(request)            # 发送请求 获取返回值
            except Exception as e:
                a += 1
                continue
            try:
                resp_dict = json.loads(resp.body)           # 解析json数据
            except Exception as e:
                a += 1
                if a == 2:
                    time.sleep(1)
                else:
                    time.sleep(2)
                continue
            if resp_dict["httpstatus"] != 200:
                a += 1
                if a == 2:
                    time.sleep(1)
                else:
                    time.sleep(2)
                continue
            data_list = resp_dict["data"]["datas"]          # 拿到常用联系人列表
            raise tornado.gen.Return({"errcode": "0", "errmsg": "常用联系人获取成功", "data": data_list})
        raise tornado.gen.Return({"errcode": "4301", "errmsg": "第三方系统错误"})
