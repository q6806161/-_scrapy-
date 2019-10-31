import re
import scrapy
import random
import sys,os
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,Join 
from selenium import webdriver
from selenium.webdriver.common.by import By
from house_info.items import HouseInfoItem
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from house_info.settings import ua

class AnjukeSpider(scrapy.Spider):
    name = 'anjuke'
    allowed_domains = ['*']
    # start_urls = ['https://xm.zu.anjuke.com']

    """
    初始请求先进行买房，租房的url进行跳转
    """
    def start_requests(self):
        start_urls = 'https://xm.zu.anjuke.com'
        # info_kind = input("请输入你要爬取的房源信息种类：'新房\二手房\租房\商铺写字楼\海外地产\楼 讯\房产研究院\房 价\问 答'")
        # for url in start_urls:
        # url = start_urls.split('.')
        # url = f"{url[0]}.zu.{url[1]}.{url[2]}"
        custom_headers={
            'User-Agent':random.choice(ua),
            'referer': "https://www.baidu.com",
        }
        yield scrapy.Request(url=start_urls, callback=self.parse,headers=custom_headers, dont_filter=True)

    
    # 用于每个城市区域url提取
    def parse(self,response):
        district_url_list = response.xpath('/html/body/div[@class="w1180"]/div[@class="div-border items-list"]/div[@class="items"]/span[@class="elems-l"]/div[@class="sub-items sub-level1"]/a[position()>1 and position()<9]/@href').extract()
        for district_url in district_url_list:
            custom_headers = {
                'User-Agent':random.choice(ua),
                "referer":response.url}
            yield scrapy.Request(url=district_url,meta = {'dont_redirect': True},callback=self.items_url, headers=custom_headers, dont_filter=True)
    

    
    def items_url_new(self,response):
        items_list = response.xpath('/html/body/div[@class="w1180"]/div[@class="maincontent"]/div[@class="list-content"]/div[@class="zu-itemmod"]')
        l_0 = ItemLoader(item=HouseInfoItem(),response=response)
        l_0.add_xpath('City','//*[@class="city-view"][1]/text()',re=('[\u4e00-\u9fff]+'))
        l_0.add_xpath('Font_Url','//*[contains(text(),"font-family")][1]/text()')
        l_0.add_xpath('District','//*[@class="sub-items sub-level1"]/a[@class="selected-item"][1]/text()')
        for item_single in items_list:
            l_1 = ItemLoader(item=HouseInfoItem(),selector=item_single)
            l_1.add_xpath('House_Title','//*[@class="zu-info"]/h3/b[@class="strongbox"]/text()')
            l_1.add_xpath('Rent_Style','//*[@class="details-item bot-tag"]/span[1]/text()')
            l_1.add_xpath('House_Type','//*[@class="details-item tag"]//text()[position()<5]',Join(),re=['[^\s"]+'])
            l_1.add_xpath('House_Area','//*[@class="details-item tag"]//text()[position()>5 and position()<8]',re=['[^\s"]+'])
            l_1.add_xpath('Floor','//*[@class="details-item tag"]//text()[position()=9]',re=['[^\s"]+'])
            l_1.add_xpath('Agent_Name','//*[@class="details-item tag"]//text()[position()=9]',re=['[^\s"]+'])
            l_1.add_xpath('Community','//*[@class="details-item"][1]/text()')
            l_1.add_xpath('Rouse_Direction','//*[@class="details-item bot-tag"]/span[2]/text()')
            l_1.add_xpath('Elevator','//*[@class="details-item bot-tag"]/span[3]/text()')
            l_1.add_xpath('Subway','//*[@class="details-item bot-tag"]/span[4]/text()')
            l_1.add_xpath('Item_Url','zu-itemmod"]/@link')
            yield l_1.load_item()
            yield l_0.load_item()

    
    # 每个区域房源信息抽取
    def items_url(self, response):
        item = HouseInfoItem()
        item["City"] = re.sub('[^\u4e00-\u9fff]+','',response.xpath('/html/body/div[@class="header header-center clearfix"]/div[@class="cityselect"]/div[@class="city-view"]/text()').extract_first())
        item["Font_Url"] = response.xpath('/html/head//script[contains(text(),"font-family")]/text()').extract_first()
        item["District"] = response.xpath('/html/body/div[@class="w1180"]/div[@class="div-border items-list"]/div[@class="items"]/span[@class="elems-l"]/div[@class="sub-items sub-level1"]/a[@class="selected-item"]/text()').extract_first()
        items_list = response.xpath('/html/body/div[@class="w1180"]/div[@class="maincontent"]/div[@class="list-content"]/div[@class="zu-itemmod"]')
        for item_single in items_list:
            item["House_Title"] = item_single.xpath('./div[@class="zu-info"]/h3/a/b/text()').extract_first()
            item["Rent_Style"] = item_single.xpath('./div[@class="zu-info"]/p[@class="details-item bot-tag"]/span[1]/text()').extract_first()
            item["Rent_Salary"] = item_single.xpath('./div[@class="zu-side"]/p/strong/b/text()').extract_first()
            item["House_Type"] = re.sub('[^\d\u4e00-\u9fff]+','',''.join(item_single.xpath('./div[@class="zu-info"]/p[@class="details-item tag"]//text()').extract()[1:5]))
            item["House_Area"] = ''.join(item_single.xpath('./div[@class="zu-info"]/p[@class="details-item tag"]//text()').extract()[-6:-4])
            item["Floor"] = ''.join(item_single.xpath('./div[@class="zu-info"]/p[@class="details-item tag"]//text()').extract()[-3])
            item["Agent_Name"] = ''.join(item_single.xpath('./div[@class="zu-info"]/p[@class="details-item tag"]//text()').extract()[-1])
            item["Community"] = re.sub('[^\(\)-,\d\u4e00-\u9fff]+','',''.join((item_single.xpath('./div[@class="zu-info"]/address[@class="details-item"]//text()').extract())))
            item["Rouse_Direction"] = item_single.xpath('./div[@class="zu-info"]/p[@class="details-item bot-tag"]/span[2]/text()').extract_first()
            item["Elevator"] = item_single.xpath('./div[@class="zu-info"]/p[@class="details-item bot-tag"]/span[3]/text()').extract_first()
            item["Subway"] = item_single.xpath('./div[@class="zu-info"]/p[@class="details-item bot-tag"]/span[4]/text()').extract_first()
            item["Item_Url"] = item_single.xpath('./div[@class="zu-info"]/h3/a/@href').extract_first()
            yield item
        # 翻页操作
        next_page = response.xpath('/html/body/div[@class="w1180"]/div[@class="maincontent"]/div[@class="page-content"]/div[@class="multi-page"]/a[@class="aNxt"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(url=next_page,callback=self.items_url, dont_filter=True)
