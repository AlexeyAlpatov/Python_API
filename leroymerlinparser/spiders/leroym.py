import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from Python_API.leroymerlinparser.items import LeroymerlinparserItem


class LeroymSpider(scrapy.Spider):
    name = 'leroym'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://novosibirsk.leroymerlin.ru/catalogue/shtukaturki/']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_xpath('name', "//h1/span/text()")
        loader.add_xpath('price', "//showcase-price-view[@slot='primary-price']/span[@slot='price']/text()")
        loader.add_xpath('cur', "//showcase-price-view[@slot='primary-price']/span[@slot='currency']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('photos', "//picture[@slot='pictures']/img/@src")
        yield loader.load_item()
