# -*- coding: utf-8 -*-
import scrapy
import re
from soufang.items import NewHouseInfo, EsfHouseInfo



class SfwSpider(scrapy.Spider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        trs = response.xpath("//div[@id='c02']//tr")
        province = None
        for tr in trs:
            tds = tr.xpath(".//td[not(@class)]")
            province_td = tds[0]       #省份的td标签
            province_text = province_td.xpath(".//text()").get()  #当前的省份
            province_text = re.sub(r"\s", "", province_text)
            if province_text:
                province = province_text
            #不爬取海外的房子
            if province == "其它":
                continue

            city_td = tds[1]           #城市的td标签
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city_name = city_link.xpath(".//text()").get()  #城市名
                city_url = city_link.xpath(".//@href").get()   #城市url
                print("省份：%s"%province)
                print("城市：%s"%city_name)
                # print("城市url：%s"%city_url)

                city_url_split = city_url.split("fang")
                bj_url_split = city_url_split[0].split("//")   #这里是为了找北京的，北京的和其他的不一样
                # print(bj_url_split)
                if bj_url_split[1] == 'bj.':
                    new_city_url = "http://newhouse.fang.com/house/s/"
                    esf_city_url = "http://esf.fang.com/"
                else:
                    # 拼接新房url
                    new_city_url = city_url_split[0] + 'newhouse.fang.com/house/s/'
                    #拼接旧房子url
                    esf_city_url = city_url_split[0] + 'esf.fang.com/'

                # print("新："+new_city_url)
                # print("旧："+esf_city_url)
                #请求每个城市的新旧房子的url,并把省份和城市通过meta以元祖的形式传过去
                yield scrapy.Request(url=new_city_url, callback=self.parse_new_city, meta={'info': (province, city_name)})
                yield scrapy.Request(url=esf_city_url, callback=self.parse_esf_city, meta={'info': (province, city_name)})


    #新房
    def parse_new_city(self, response):
        province, city_name = response.meta.get('info')     #元祖可以通过这种形式解包，获取到省份和城市
        floors = response.xpath("//div[@class='nlcd_name']/a") #所有楼盘
        for floor in floors:
            floor_name = floor.xpath(".//text()").get().strip()     #楼盘名字
            floor_url = "https:" + floor.xpath(".//@href").get().strip()     #楼盘url
            # print(floor_name)
            #请求新楼盘url,并调用parse_new_house函数，把meta传过去
            yield scrapy.Request(url=floor_url, callback=self.parse_new_house, meta={'info': (province, city_name, floor_name)})
        #查找尾页，确定又多少页，然后在回调自己本身，注意要传meta,否则会报错
        wei_page_url = response.xpath("//ul[@class='clearfix']/li[@class='fr']/a[@class='last']/@href").get()
        if wei_page_url:
            wei_page_num = int(re.sub(r'/', '', wei_page_url.split("b9")[1]))
            if wei_page_num:
                for i in range(2, wei_page_num+1):
                    page_url = '{}b9{}'.format(response.url, i)
                    # print(page_url)
                    yield scrapy.Request(url=page_url, callback=self.parse_new_city, meta={'info': (province, city_name)})


    #新房的具体信息,在请求楼盘详情
    def parse_new_house(self, response):
        province, city_name, floor_name = response.meta.get('info')
        label = ",".join(response.xpath("//div[@id='xfptxq_B04_44']//a/text()").getall())             #标签
        price = response.xpath("//div[@class='information_li mb5']/div[@class='inf_left fl ']/span/text()").get()   #单价
        house_type = ",".join(response.xpath("//div[@id='xfptxq_B04_13']//a/text()").getall())                #户型
        site = response.xpath("//div[@id='xfptxq_B04_12']/span/@title").get()             #地址
        phone = re.sub(r"咨询电话：", "", "".join(response.xpath("//div[@id='phone400']//span/text()").getall()))     #质询电话
        opening = response.xpath("//a[@id='xfptxq_B04_23']/text()").get()     #开盘情况
        if not opening:
            opening = '暂无资料'
        item = NewHouseInfo(province=province, city=city_name, name=floor_name,
                            label=label, price=price, house_type=house_type,
                            site=site, phone=phone, opening=opening, origin_url=response.url,
                            genre='新房')
        yield item

        # print("省份：{}，城市：{}，小区：{}，标签：{}，单价：{}，户型：{}，地址：{}，电话：{}，
        # 开盘情况：{}，原始URL：{}".format(province,city_name,floor_name,label,price,house_type,
        # site,phone,opening,response.url))





    #二手房
    def parse_esf_city(self, response):
        province, city_name = response.meta.get('info')      #元祖可以通过这种形式解包，获取到省份和城市
        dls = response.xpath("//div[@class='shop_list shop_list_4']//dl")
        for dl in dls:
            a = dl.xpath(".//dd[not(@class)]/h4[@class='clearfix']/a")
            esf_name = a.xpath(".//@title").get()           #房子名称
            esf_url = a.xpath(".//@href").get()             #房子url
            esf_url = response.urljoin(esf_url)            #拼接
            price = "".join(dl.xpath(".//span[@class='red']//text()").getall())   #总价
            unit_price = dl.xpath(".//dd[@class='price_right']/span[not(@class)]/text()").get()   #单价
            dizhi = re.sub(r"\s", "", "-".join(dl.xpath(".//p[@class='add_shop']//text()").getall()))   #地址
            info = dl.xpath(".//p[@class='tel_shop']//text()").getall()    #具体信息
            house_type = None           #户型
            house_size = None           #大小
            orientation = None          #朝向
            for i in info:
                i = re.sub(r"\s", '', i)
                try:
                    if i[-1] == '厅':
                        house_type = i
                    if i[-1] == '㎡':
                        house_size = i
                    if i[-1] == '向':
                        orientation = i
                except IndexError:
                    pass
            item = EsfHouseInfo(province=province, city=city_name, esf_name=esf_name, info_url=esf_url,
                                price=price, unit_price=unit_price, dizhi=dizhi, house_type=house_type,
                                house_size=house_size, orientation=orientation, genre='旧房')
            yield item

        #默认是100页
        for page in range(1, 101):
            next_url = response.url + 'house/i3{}/'.format(page)
            print('下一页', next_url)
            yield scrapy.Request(url=next_url, callback=self.parse_esf_city, meta={'info': (province, city_name)})






