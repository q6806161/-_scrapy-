# -*- coding: utf-8 -*-
from fontTools.ttLib import TTFont
from scrapy.exceptions import DropItem
import base64
import pymysql
import re
import os
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


"""
func: 用于对爬取到的items的值进行字符替换
para: pattern_font_url 用于提取字典item["Font_Url"]值的font_url
      result_dict 存储每个网页十六进制字符与数字对应关系的字典
"""
class HouseInfoTranslationPipeline(object):
    
    def process_item(self, item, spider):
        pattern_font_url = re.compile(r"""
        font-family.*?base64,(.*?)'
        """,re.VERBOSE|re.S)
        font_url_text = item["Font_Url"]
        font_url = re.findall(pattern_font_url,font_url_text)[0]
        result_dict = self.translate_func(font_url)
        for key,value in item.items():
            value_new = ''
            if value:
                for w in value:
                    if hex(ord(w)) in result_dict.keys():
                        w = re.sub(w,result_dict[hex(ord(w))],w)
                    value_new += w
                item[key] = value_new 
            else:
                item[key]="None"
        return item

    def translate_func(self, font_url):
        #手动确认编码和数字之间的对应关系，保存到字典中
        initial_dict={'glyph00001': '0', 'glyph00002': '1', 'glyph00003': '2', 'glyph00004': '3', 
       'glyph00005': '4', 'glyph00006': '5', 'glyph00007': '6', 'glyph00008': '7', 
       'glyph00009': '8', 'glyph00010': '9'}
        b = base64.b64decode(font_url)
        code_file = 0
        while True:
            file_ttf = f"{code_file}.ttf"
            if os.path.exists(file_ttf):
                code_file +=1
            else:
                with open(file_ttf,"wb") as f:
                    f.write(b)
                break
        # 获取新ttf文件并转化为xml方便解析
        font_2 = TTFont(file_ttf)
        file_xml=file_ttf.replace('ttf','xml')
        font_2.saveXML(file_xml)
        os.remove(file_ttf)
        pattern_code_obj = re.compile(r"""(
        <map\s+code="(\S+)"\s+name="(\w+\d+)"/>  # 用于获取响应中新的编码和字符对象编号
        )""",re.VERBOSE|re.S)
        with open(file_xml,'r',encoding='utf-8') as online_ttf:
            # 实时字符对应字典
            online_codes_dict = dict([(code_obj[1],code_obj[2]) for code_obj in re.findall(pattern_code_obj, online_ttf.read())])
        # 和手动编码字典对应进行更新
        result_dict = {online_code:initial_dict[online_obj] for online_code,online_obj in online_codes_dict.items()}
        os.remove(file_xml)
        return result_dict



class MysqlFirstWritePipeline(object):

    def __init__(self):
        self.database = pymysql.connect(
        host='127.0.0.1', # 上传github记得修改
        port=3306,user='root',  #使用自己的用户名 
        passwd='123456',  # 使用自己的密码
        db='anjuke',  # 数据库名
        charset='utf8')
        # self.database.query("CREATE TABLE boss_job_items(\
        # job_id INT NOT NULL AUTO_INCREMENT,\
        # job_name VARCHAR(100) NOT NULL,\
        # salary_range VARCHAR(100) NOT NULL,\
        # company VARCHAR(50) NOT NULL,\
        # industry VARCHAR(50) NOT NULL,\
        # company_scale VARCHAR(50) NOT NULL,\
        # city VARCHAR(50) NOT NULL,\
        # experience_request VARCHAR(50) NOT NULL,\
        # bachelor VARCHAR(100) NOT NULL,\
        # job_kind VARCHAR(100) NOT NULL,\
        # job_url VARCHAR(200) NOT NULL,\
        # PRIMARY KEY ( job_id ))\
        # ENGINE=InnoDB DEFAULT CHARSET=utf8")
        self.cursor = self.database.cursor()
    
    def process_item(self, item, spider):
        City = item["City"]                            # 城市
        House_Title = item["House_Title"]              # 租房标题
        Rent_Style = item["Rent_Style"]                # 整租或合租
        Rent_Salary = item["Rent_Salary"]              # 租金
        House_Type = item["House_Type"]                # 户型
        House_Area = item["House_Area"]                # 房间面积
        Floor = item["Floor"]                          # 楼层
        Agent_Name = item["Agent_Name"]                # 中介名称
        Community = item["Community"]                  # 小区
        Rouse_Direction = item["Rouse_Direction"]      # 朝向
        Elevator = item["Elevator"]                    # 有无电梯
        Subway = item["Subway"]                        # 地铁
        Item_Url = item["Item_Url"]                    # 对应url

        sql = f"""INSERT INTO `anjuke` (`City`,`House_Title`, `Rent_Style`, `Rent_Salary`,`House_Type`,
         `House_Area`, `Floor`,`Agent_Name`,`Community`,`Rouse_Direction`,`Elevator`,`Subway`,`Item_Url`
        ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        self.cursor.execute(sql,(City, House_Title, Rent_Style, Rent_Salary, House_Type, House_Area, Floor, 
        Agent_Name, Community, Rouse_Direction, Elevator, Subway, Item_Url))
        self.database.commit()



"""
func: 用于mysql数据存储，database—anjuke（可自主命名）
                        table—rentinfo（可自主命名）                    
"""
class MysqlWritePipeline(object):

    def __init__(self):
        self.database = pymysql.connect(
        host='127.0.0.1', # 上传github记得修改
        port=3306,user='root',  #使用自己的用户名 
        passwd='123456',  # 使用自己的密码
        db='anjuke',  # 数据库名
        charset='utf8')
        # self.database.query("CREATE TABLE boss_job_items(\
        # job_id INT NOT NULL AUTO_INCREMENT,\
        # job_name VARCHAR(100) NOT NULL,\
        # salary_range VARCHAR(100) NOT NULL,\
        # company VARCHAR(50) NOT NULL,\
        # industry VARCHAR(50) NOT NULL,\
        # company_scale VARCHAR(50) NOT NULL,\
        # city VARCHAR(50) NOT NULL,\
        # experience_request VARCHAR(50) NOT NULL,\
        # bachelor VARCHAR(100) NOT NULL,\
        # job_kind VARCHAR(100) NOT NULL,\
        # job_url VARCHAR(200) NOT NULL,\
        # PRIMARY KEY ( job_id ))\
        # ENGINE=InnoDB DEFAULT CHARSET=utf8")
        self.cursor = self.database.cursor()
    
    def process_item(self, item, spider):
        City = item["City"]                            # 城市
        House_Title = item["House_Title"]              # 租房标题
        Rent_Style = item["Rent_Style"]                # 整租或合租
        Rent_Salary = item["Rent_Salary"]              # 租金
        House_Type = item["House_Type"]                # 户型
        House_Area = item["House_Area"]                # 房间面积
        Rouse_Direction = item["Rouse_Direction"]      # 朝向
        Floor = item["Floor"]                          # 楼层
        Decoration = item["Decoration"]                # 装修
        House_Kind = item["House_Kind"]                # 房租类型
        Community = item["Community"]                  # 小区
        House_Equipment = item["House_Equipment"]      # 房间配套
        House_Description = item["House_Description"]  # 房源概况
        Agent_Name = item["Agent_Name"]                # 中介名称
        Agent_Level = item["Agent_Level"]              # 中介星级（打败同业人员多少percent）
        House_Score = item["House_Score"]              # 房源评分
        Service_Score = item["Service_Score"]          # 中介服务评分
        Evaluation_Score = item["Evaluation_Score"]    # 用户评价
        Agent_Company = item["Agent_Company"]          # 中介公司
        Branch_Office = item["Branch_Office"]          # 所处分公司
        Company_License = item["Company_License"]      # 公司营业执照号
        Publish_Date = item["Publish_Date"]            # 发布时间

        sql = f"""INSERT INTO `rentinfo` (`City`,`House_Title`, `Rent_Style`, `Rent_Salary`,
        `House_Type`, `House_Area`, `Rouse_Direction`, `Floor`, `Decoration`, `House_Kind`,
        `Community`,`House_Equipment`,`House_Description`,`Agent_Name`,`Agent_Level`,
        `House_Score`,`Service_Score`,`Evaluation_Score`,`Agent_Company`,`Branch_Office`,
        `Company_License`,`Publish_Date`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s,%s)"""
        self.cursor.execute(sql,(City,House_Title, Rent_Style, Rent_Salary,House_Type,
        House_Area, Rouse_Direction, Floor, Decoration, House_Kind,Community,
        House_Equipment, House_Description, Agent_Name, Agent_Level, House_Score,
        Service_Score, Evaluation_Score, Agent_Company, Branch_Office, Branch_Office,
        Company_License))
        self.database.commit()
