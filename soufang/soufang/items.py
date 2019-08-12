# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#新房
class NewHouseInfo(scrapy.Item):
    province = scrapy.Field()             #省份
    city = scrapy.Field()                 #城市
    name = scrapy.Field()                 #小区名字
    label = scrapy.Field()                #标签
    price = scrapy.Field()                #价格
    house_type = scrapy.Field()           #户型
    site = scrapy.Field()                 #地址
    phone = scrapy.Field()                #咨询电话
    opening = scrapy.Field()              #开盘情况
    origin_url = scrapy.Field()           #原始url
    genre = scrapy.Field()                #类型（新房，旧房）


#旧房
class EsfHouseInfo(scrapy.Item):
    province = scrapy.Field()         #省份
    city = scrapy.Field()             #城市
    esf_name = scrapy.Field()         #房子名称
    info_url = scrapy.Field()         #具体信息url
    price = scrapy.Field()            #总价
    unit_price = scrapy.Field()       #单价
    house_type = scrapy.Field()       #户型
    house_size = scrapy.Field()       #面积
    orientation = scrapy.Field()      #朝向
    dizhi = scrapy.Field()            #地址
    genre = scrapy.Field()  # 类型（新房，旧房）
