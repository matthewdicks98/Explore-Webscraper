# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from shutil import which
from scrapy.selector import Selector
from selenium.webdriver.common.keys import Keys
import time
 
#### this scrolling method will run in about 24 hours but it can handle the changing number of companies
#### you do not need to know the number of companies to do this


class CompaniesSpider(scrapy.Spider):
    name = 'companies'
    allowed_domains = ['www.allabolag.se/'] # do not put http protocol here 
    start_urls = ['https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_/']


    def __init__(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        firefox_path = which("geckodriver-v0.28.0-linux64/geckodriver")

        driver = webdriver.Firefox(executable_path=firefox_path, options = firefox_options)
        driver.get(
            "https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_")
        
        # let the page load
        time.sleep(1)
        s = time.time()

        # perform scrolling actions to get all the companies
        # You can set your own pause time. My laptop is a bit slow so I use 1 sec
        scroll_pause_time = 3
        last_height = driver.execute_script("return document.body.scrollHeight")   # get the screen height of the web
        i = 1

        while True:

            # scroll one screen height each time
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(i)
            i+=1
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # If heights are the same it will exit the function
                break
            last_height = new_height


        print("################## Scrolling time {:.2f} min ##################".format((time.time()-s)/60))
        f = open("scrolling_time_1200.txt", "a")
        f.write(str((time.time()-s)/60))
        f.write(f"\n{i}")
        f.close()


        self.html = driver.page_source
        driver.quit()


    def parse(self, response):

        resp = Selector(text=self.html)

        # get the number of companies
        num_companies = int(resp.xpath('//h3[@data-v-de280356=""]/text()').get().strip())

        # getting all the comapnies
        companies_data = resp.xpath('//div[@class="search-results__item tw-flex-1"]')
        
        for company in companies_data:
            name = company.xpath('.//div[2]/h2/a/text()').get()
            #link = company.xpath('.//div[2]/h2/a/@href').get()
            number = company.xpath('.//dl/dd[1]/text()').get().replace("-","")

            yield {
                'company_no':number,
                'company_name':name
            }
            
