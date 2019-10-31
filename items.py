# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HouseInfoItem(scrapy.Item):
    # define the fields for your item here like:
    City = scrapy.Field()               # 城市
    Item_Url = scrapy.Field()           # 对应网址
    House_Title = scrapy.Field()        # 租房标题
    Rent_Style = scrapy.Field()         # 整租或合租
    Rent_Salary = scrapy.Field()        # 租金
    House_Type = scrapy.Field()         # 户型
    House_Area = scrapy.Field()         # 房间面积
    Rouse_Direction = scrapy.Field()    # 朝向
    Floor = scrapy.Field()              # 楼层
    Decoration = scrapy.Field()         # 装修
    House_Kind = scrapy.Field()         # 房子类型
    Community = scrapy.Field()          # 小区
    House_Equipment = scrapy.Field()    # 房间配套
    House_Description = scrapy.Field()  # 房源概况
    Agent_Name = scrapy.Field()         # 中介名称
    Agent_Level = scrapy.Field()        # 中介星级（打败同业人员多少percent）
    House_Score = scrapy.Field()        # 房源评分
    Service_Score = scrapy.Field()      # 中介服务评分
    Evaluation_Score = scrapy.Field()   # 用户评价
    Agent_Company = scrapy.Field()      # 中介公司
    Branch_Office = scrapy.Field()      # 所处分公司
    Company_License = scrapy.Field()    # 公司营业执照号
    Publish_Date = scrapy.Field()       # 发布时间
    Font_Url = scrapy.Field()           # 字符替换url
    Elevator = scrapy.Field()           # 有无电梯
    Subway = scrapy.Field()             # 地铁
    District = scrapy.Field()           # 城市区域
    pass
