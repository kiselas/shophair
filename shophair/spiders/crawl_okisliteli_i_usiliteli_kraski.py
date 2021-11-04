# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import datetime


class CrawlOkisliteliIUsiliteliKraskiSpider(CrawlSpider):
    name = "crawl_okisliteli_i_usiliteli_kraski"
    allowed_domains = ["www.shophair.ru"]
    start_urls = ["https://www.shophair.ru/sredstva_dlya_okrashivania_volos/okisliteli_i_usiliteli_kraski/"]
    domain = "www.shophair.ru"

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//a[@class='pagination_go_next']"),
             process_request='add_req_header', follow=True),
        Rule(LinkExtractor(restrict_xpaths="//div[@class='pr_name']/a"),
             process_request='add_req_header', callback='parse_item'),
    )

    def add_req_header(self, request):
        request.cookies[
            'cityName2'] = "%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3"
        return request

    @staticmethod
    def discount_calc(current_price, original_price):  # считаем скидку по формуле
        print(current_price, original_price)
        current_price = int(current_price)
        original_price = int(original_price)
        discount = round(((original_price - current_price) / original_price) * 100, 1)
        return discount

    @staticmethod
    def isBlank(myString):  # проверяем пустое ли значение
        if myString and myString.strip():
            return False
        return True

    def parse_item(self, response):

        for product in response.xpath("//div[@class='inner-page asd']"):
            if product.xpath(".//span[@itemprop='sku'][2]/text()"):
                rpc = product.xpath(".//span[@itemprop='sku'][2]/text()").get()
            else:
                rpc = product.xpath(".//span[@itemprop='sku'][1]/text()").get()

            marketing_tags = []
            if product.xpath(".//div[@class='sticker-new']"):
                marketing_tags.append('new')

            if product.xpath(".//div[@class='wrap_price']/span[@class='name_price']"):
                in_stock = False
            else:
                in_stock = True

            original_price = product.xpath( ".//div[@class='flocktory_class dn']/@oldprice").get()
            current_price = product.xpath(".//div[@class='flocktory_class dn']/@price").get()

            discount_price = self.discount_calc(current_price, original_price)

            yield {
                'timestamp': datetime.datetime.now(),
                "RPC": rpc,
                'url': response.url,
                'title': product.xpath(".//span[@class='name_product']/text()").get(),
                "marketing_tags": marketing_tags,
                'brand': product.xpath(".//h1[@class='brand_product']/text()").get(),
                "section": product.xpath(".//span[@itemprop='name']/text()").getall(),
                "price_data": {
                    "current": current_price,
                    "original": original_price,
                    "sale_tag": f'Скидка: {discount_price}%',
                },
                "stock": {
                    "in_stock": in_stock,
                    "count": 0
                },
                "assets": {
                    "main_image": self.domain + product.xpath("//div[@class='r_cp_images_list']//img/@src").get(),
                    "set_images": [],
                    "view360": [],
                    "video": []
                },
                "metadata": {
                    "__description": product.xpath(".//div[@class='pr_description_left'] /p/text()"),
                    "АРТИКУЛ": product.xpath(".//span[@itemprop='sku'][1]/text()").get(),
                    "СТРАНА ПРОИЗВОДИТЕЛЬ": "Китай"
                },
                "variants": 1,
            }
