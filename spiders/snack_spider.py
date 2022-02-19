import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import Request

class SpiderSnack(scrapy.Spider):
    name = 'snack_spider'
    allowed_domains = ['americanuncle.it']
    start_urls = ['https://www.americanuncle.it/collections/snack-americani']
    
    headers = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
    }
    
    custom_settings = {
        'FEED_URI': 'all_items.csv',
        'FEED_FORMAT': 'csv',
        'DOWNLOAD_DELAY': 2
    }
    
    try:
        os.remove('all_items.csv')
    except OSError:
        pass
    
    def parse(self, response):
        
        all_products = response.css('div.product-block.grid__item.one-quarter.small-down--one-half')
        
        # look through each product and extract the data
        for product in all_products:
            name = product.css('div.product-block__title a::attr(href)').get().replace('/collections/snack-americani/products/', '')
            price = product.css('div.product-price span.theme-money::text').get()
            stars = product.css('span.jdgm-prev-badge__stars::attr(data-score)').get()
            link = product.css('div.product-block__title a::attr(href)').get()
            yield Request(f'https://www.americanuncle.it/collections/snack-americani/products/{name}', callback=self.parse_details, meta={'name': name, 'price': price, 'stars': stars, 'link': link})
        
        # repeat the process until no page is found     
        next_page = response.css('span.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_details(self, response):
        
        name = response.meta['name']
        price = response.meta['price']
        stars = response.meta['stars']
        link = response.meta['link']
        
        # send the data to the csv file
        yield {
            'name': name,
            'price': price,
           'stars': stars,
           'link': link
        }

# main driver
if __name__ == '__main__':
    p = CrawlerProcess()            
    p.crawl(SpiderSnack)
    p.start()
