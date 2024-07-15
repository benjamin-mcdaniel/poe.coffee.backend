BOT_NAME = 'image_scraper'

SPIDER_MODULES = ['image_scraper.spiders']
NEWSPIDER_MODULE = 'image_scraper.spiders'

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'image_scraper.pipelines.ImageScraperPipeline': 300,
}
