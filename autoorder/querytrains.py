# coding=utf-8

import json
import urllib
from baserequest import BaseRequest


class GetTrain(BaseRequest):
    """继承基础类"""
    def __init__(self, date, from_code, to_code, *args, **kwargs):
        """
        初始化信息 格式化数据
        date:"2018-10-10"               出发时间 格式化数据
        from_station:"BJD"              出发站代号
        to_station:"TJN"                目的站代号
        """
        super(GetTrain, self).__init__(*args, **kwargs)
        self.data = [                                           # 格式化查询信息
            {"leftTicketDTO.train_date": date},                 # 出发日期
            {"leftTicketDTO.from_station": from_code},          # 出发站代号
            {"leftTicketDTO.to_station": to_code},              # 到达站代号
            {"purpose_codes": "ADULT"}                          # 固定值
        ]

    def query_all_trains(self):
        """发送请求获取所有的余票信息"""
        url = "https://kyfw.12306.cn/otn/leftTicket/queryZ?"     # 构造url
        data_list = [urllib.urlencode(i) for i in self.data]    # 遍历数据组成参数列表
        url += "&".join(data_list)                              # 拼接url
        request = self.request(url, headers=self.headers)       # 构建请求对象
        count = 0
        while True:
            try:
                resp = self.opener.open(request).read()         # 发送请求 获取返回值
                data_dict = json.loads(resp)                    # 解析json对象
            except Exception as e:
                count += 1
                if count <=3:
                    continue
                else:
                    return {"errcode":"404","errmsg":"列车信息获取失败"}
            if data_dict["httpstatus"] == 200:                  # 正常状态返回码
                return {"errcode": "0", "errmsg": "列车信息获取成功", "data": data_dict["data"]}  # 返回数据
            else:                                               # 出错后重新执行
                print data_dict
                continue

    def get_submit_data(self,trains_code,seattypes,person_count,data):
        """
        查询某趟列车的所有信息
        trains_code:["k138",]:   列车简称不区分大小写
        seattype:  ["硬座",]        坐席类型列表
        data:    {"result":["列车详情1","列车详情2"]}
        return:  ["列车参数1","列车参数2","列车参数3"...] 详情在 接口分析.txt
        """
        seat_type_list = []                                     # 初始化需要提取的座位类型列表
        for i in seattypes:                                     # 遍历提交信息 转换为列表下标
            if i == u"特等座":
                seat_type_list.append(-5)
            elif i == u"一等座":
                seat_type_list.append(-6)
            elif i == u"二等座":
                seat_type_list.append(-7)
            elif i == u"软卧":
                seat_type_list.append(-14)
            elif i == u"硬卧":
                seat_type_list.append(-10)
            elif i == u"硬座":
                seat_type_list.append(-9)
        for i in trains_code:
            for x in data["result"]:                            # 遍历返回值信息
                data_list = x.split("|")
                if i == data_list[3]:                           # 查找到车次信息
                    for y in seat_type_list:                    # 查看余票数据
                        if data_list[y] != u"无" and data_list[y] != "0" and data_list[y] != "":
                            if data_list[y] == u"有":           # 判断余票多的情况
                                print data_list
                                print data_list[y]
                                print "已获取到相关列车数据"
                                return {"errcode":"0","errmsg":"列车数据获取成功","data":data_list,"seat":y}  # 返回数据
                            try:                                # 判断余票大于人数的情况
                                if int(data_list[y]) >= person_count:
                                    print "已获取到相关列车数据"
                                    print data_list
                                    print data_list[y]
                                    return {"errcode":"0","errmsg":"列车数据获取成功","data":data_list,"seat":y}
                            except Exception as e:
                                pass
        return {"errcode":"4002","errmsg":"无数据"}              # 其他情况