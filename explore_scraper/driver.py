import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

import sys
import os
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings

sys.path.insert(1,os.getcwd()+"/explore_scraper/spiders")
from financials import FinancialsSpider
from status import StatusSpider

settings = Settings()
os.environ['SCRAPY_SETTINGS_MODULE'] = 'explore_scraper.settings'
settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
settings.setmodule(settings_module_path, priority='project')

configure_logging()
runner = CrawlerProcess(get_project_settings())
runner.crawl(StatusSpider)
runner.crawl(FinancialsSpider)
runner.start()
# d = runner.join()
# d.addBoth(lambda _: reactor.stop())

# reactor.run()
