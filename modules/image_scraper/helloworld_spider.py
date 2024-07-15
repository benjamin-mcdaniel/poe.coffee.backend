import scrapy

class HelloWorldSpider(scrapy.Spider):
    name = "helloworld"
    allowed_domains = ['example.com']
    start_urls = ['http://example.com']

    def parse(self, response):
        self.log('Hello World! Scraping example.com')
