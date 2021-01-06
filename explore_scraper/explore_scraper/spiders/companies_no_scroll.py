# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from shutil import which
from scrapy.selector import Selector
from selenium.webdriver.common.keys import Keys
import time


class CompaniesNoScrollSpider(scrapy.Spider):
    name = 'companies_no_scroll'
    allowed_domains = ['www.allabolag.se']
    start_urls = ['https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_/']
    htmls = []

    def __init__(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        firefox_path = which("geckodriver-v0.28.0-linux64/geckodriver")

        driver = webdriver.Firefox(
            executable_path=firefox_path, options=firefox_options)

        # loop through the number of pages needed to get all the companies
        num_pages = 400
        for i in range(1,num_pages+1):
            driver.get(
                f"https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_?page={i}")

            # let the page load
            time.sleep(1)

            self.htmls.append(driver.page_source)

        driver.quit()

    def parse(self, response):

        for i in range(len(self.htmls)):
            resp = Selector(text=self.htmls[i])
            # getting all the comapnies
            companies_data = resp.xpath(
                '//div[@class="search-results__item tw-flex-1"]')

            for company in companies_data:
                name = company.xpath('.//div[2]/h2/a/text()').get()
                #link = company.xpath('.//div[2]/h2/a/@href').get()
                number = company.xpath('.//dl/dd[1]/text()').get().replace("-", "")

                yield {
                    'company_no': number,
                    'company_name': name
                }
