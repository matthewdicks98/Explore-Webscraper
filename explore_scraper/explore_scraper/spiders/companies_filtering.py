# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from shutil import which
from scrapy.selector import Selector
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
import math
import socket

class CompaniesFilteringSpider(scrapy.Spider):
    name = 'companies_filtering'
    allowed_domains = ['www.allabolag.se']
    start_urls = [
        'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_/']
    country_hits = []
    names = []
    numbers = []
    url = ''

    def __init__(self):
        s = time.time()
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        firefox_path = which("geckodriver-v0.28.0-linux64/geckodriver")

        # disabling cookies
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.cookie.cookieBehavior",2)

        driver = webdriver.Firefox(
            executable_path=firefox_path, options=firefox_options, firefox_profile=fp)


        # fetch the main url
        driver.get(
            "https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_")

        main_html = driver.page_source
        main_response = Selector(text=main_html) 

        
        # get the country hits
        c = driver.find_element_by_xpath(
            '//div[@class="group tw-flex tw-justify-between tw-items-center tw-px-4 tw-border-t tw-border-gray-200 tw-cursor-pointer"][3]')
        time.sleep(2)
        c.click()
        time.sleep(2)
        response = Selector(text=driver.page_source)
        country_selectors = response.xpath('//div[@class="tw-flex tw-flex-row tw-justify-between tw-mb-2"]')[1:]
        for country in country_selectors:
            self.country_hits.append(int(country.xpath(
                './/span[@class="tw-text-gray-700"]/text()').get()[1:-1].replace(" ", "")))
        print("#####################")
        print(self.country_hits)
        print("######################")
        # select a country (in same order as the hits found above)
        num_countries = len(self.country_hits)
        #num_countries = 21 # just to test revenue
        for i in range(1,num_countries+1):
            print(f"{i} has started")
            # select the box ans load the page
            checkbox = driver.find_element_by_xpath(
                f'//div[@class="tw-flex tw-flex-row tw-justify-between tw-mb-2"][{i}]/label/span')


            time.sleep(2)
            checkbox.click()
            time.sleep(2)
            response = Selector(text=driver.page_source)

            #visited = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

            # check the counts 
            # if i in visited:
            #     # used to parse the countries 1 by one
            #     pass
            if self.country_hits[i-1] > 8000:
                # filter based on revenue
                self.revenue_filter(driver, driver.current_url)
            else:
                # get the number of pages and extract all the htmls from the urls
                num_pages = math.ceil(self.country_hits[i-1]/20)
                time.sleep(2)
                url = driver.current_url
                time.sleep(2)
                self.get_pages(driver, num_pages, url)

            #print(f"################### NUMBER OF PAGES {len(self.htmls)} ####################")
            print("################### "+driver.current_url)

            # unclick the current country
            checkbox = driver.find_element_by_xpath(
                f'//div[@class="tw-flex tw-flex-row tw-justify-between tw-mb-2"][{1}]/label/span')
            
            time.sleep(2)
            checkbox.click()
            time.sleep(2)
            print(f"{i} is done")

        driver.quit()
        print(f"############# Time Taken {(time.time()-s)/60}")

    def get_pages(self, driver_l, num_pages, url):  # driver_l, num_pages, url
        #page_htmls = []
        url = url + "?page="
        for i in range(1,num_pages+1):
            page_url = url+str(i)
            driver_l.get(page_url)
            time.sleep(1) # can increase this to increase the number of pages
            self.parse_page(driver_l.page_source)
            #page_htmls.append(driver_l.page_source)
            # instead of storing the whole html send it to a method where we can process the html and extract
            # the 20 names and numbers
        #r = Selector(text=driver_l.page_source)
        #print("#################################"+r.xpath('//div[@data-v-de280356=""]/h3/text()').get())
        #return page_htmls

    def parse_page(self, html):
        # create a list of names and number that can be added to the global names and numbers
        response = Selector(text=html)
        companies_data = response.xpath(
            '//div[@class="search-results__item tw-flex-1"]')

        for company in companies_data:
            name = company.xpath('.//div[2]/h2/a/text()').get()
            if name:
                name = name.replace(",", ";")

            number = company.xpath('.//dl/dd[1]/text()').get()
            if number:
                number = number.replace("-", "")
            
            self.names.append(name)
            self.numbers.append(number)


    def revenue_filter(self, driver, base_url):  # driver, base_url
        # set the revenue ranges
        # last must set the url to be 5000-
        ranges = [0,1,100,500,1000,2500,5000]
        revenue_htmls = []

        # set the base of the url
        base_url = base_url + "/xr/"

        # for a given range get the hits and then get all the pages assocated with it
        for i in range(len(ranges)):
            # get the base page
            if i == len(ranges) - 1:
                url = base_url + str(ranges[i]) + "-"
            else:
                url = base_url + str(ranges[i]) + "-" + str(ranges[i+1])

            driver.get(url)
            time.sleep(1)

            response = Selector(text = driver.page_source)

            # get the hits for this page
            num_hits = response.xpath('//div[@data-v-de280356=""]/h3/text()').get()
            print("##################")
            print(num_hits)
            print("######################")
            if num_hits == " Inga träffar":
                continue
            else:
                num_hits = int(num_hits.replace(" ",""))
                assert num_hits < 8000
                num_pages = math.ceil(num_hits/20)
                time.sleep(2)
                url = driver.current_url
                time.sleep(2)
                self.get_pages(driver, num_pages, url)

        # clear the revenue filter
        driver.get(base_url[:-4])



    def parse(self, response):
        assert len(self.numbers) == len(self.names)
        for i in range(len(self.numbers)):
            yield {
                'company_no': str(self.numbers[i]),
                'company_name': self.names[i]
            }
