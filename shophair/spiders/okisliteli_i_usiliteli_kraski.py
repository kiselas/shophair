# -*- coding: utf-8 -*-
import scrapy
import datetime

class OkisliteliIUsiliteliKraskiSpider(scrapy.Spider):
    name = "okisliteli_i_usiliteli_kraski"
    allowed_domains = ["www.shophair.ru"]
    start_urls = ["https://www.shophair.ru/sredstva_dlya_okrashivania_volos/okisliteli_i_usiliteli_kraski"]
    domain = "www.shophair.ru"

    @staticmethod
    def discount_calc(current_price, original_price):
        print(current_price, original_price)
        current_price = int(current_price)
        original_price = int(original_price)
        # формула для подсчета скидки (считает, даже если верстка на сайте для отобр. скидки изменится)
        discount = round(((original_price - current_price)/original_price)*100, 1)
        return discount

    @staticmethod
    def isBlank(myString):
        if myString and myString.strip():
            # myString is not None AND myString is not empty or blank
            return False
        # myString is None OR myString is empty or blank
        return True

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, cookies={'cityName2': '%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3'}, callback=self.parse)

    def parse(self, response):
        for product in response.xpath("//div[@class='wrap_product_item']"):

            marketing_tags = []
            if product.xpath(".//div[@class='sticker-new']"):
                marketing_tags.append('new')

            if product.xpath(".//span[@class='old_price line-through-no']"):
                in_stock = False
            else:
                in_stock = True

            if in_stock:
                original_price = product.xpath(".//span[@class='new_price']/text()").get()

                if self.isBlank(original_price):
                    original_price = product.xpath(".//span[@class='new_price']/span[1]/text()").get()

                if product.xpath(".//div[@class='wrap_prices_item wrap_prices_item__discount']//span[@class='price_desc_red'][2]"):
                    current_price = product.xpath(
                        ".//div[@class='wrap_prices_item wrap_prices_item__discount']//span[@class='price_desc_red'][2]/text()").get()
                else:
                    current_price = original_price
                discount_price = self.discount_calc(current_price, original_price)
            else:
                original_price = 0
                current_price = 0
                discount_price = 0


            yield {
                'timestamp': datetime.datetime.now(),
                "RPC": "",
                'url': response.urljoin(product.xpath(".//div[@class='pr_name']/a/@href").get()),
                'title': product.xpath(".//div[@class='pr_name']/a/@title").get(),
                "marketing_tags": marketing_tags,
                'brand': product.xpath(".//div/a/span[@class='list_brand_name']/text()").get(),
                "section": [],
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
                    "main_image": "",
                    "set_images": [],
                    "view360": [],
                    "video": []
                },
                "metadata": {
                    "__description": "",  # {str} Описание товар
                    "АРТИКУЛ": "A88834",
                    "СТРАНА ПРОИЗВОДИТЕЛЬ": "Китай"
                },
                "variants": 1,
            }

        next_page = response.xpath("//a[@class='pagination_go_next']/@href").get()

        if next_page:
            next_page_url = self.start_urls[0] + '/' + next_page
            yield scrapy.Request(next_page_url, cookies={
                    'cityName2': '%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3'},
                                     callback=self.parse)
