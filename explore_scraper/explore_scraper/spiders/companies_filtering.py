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
    """
    This class was used to get the IDs and Names of companies from the site, 
    'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_/'. It used filtering by company location and
    by revenue to get all the data. This was needed because of the 400 page limit for a specific url. This scraper used
    selenium to perform javascript actions and scrape javascript pages. The headless browser used is firefox.
    """

    name = 'companies_filtering'
    allowed_domains = ['www.allabolag.se']
    start_urls = [
        'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_/']
    country_hits = []
    names = []
    numbers = []
    url = ''

    def __init__(self):
        """
        Initializes the headless firefox browser. It performs the filtering by company location and calls the get_pages 
        and revenue_filter funtions.
        """

        # start the clock
        s = time.time()

        # Initializing the firefox browser
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        firefox_path = which("geckodriver-v0.28.0-linux64/geckodriver")

        ## disabling cookies
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.cookie.cookieBehavior",2)

        driver = webdriver.Firefox(
            executable_path=firefox_path, options=firefox_options, firefox_profile=fp)


        # fetch the main url
        driver.get(
            "https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_")

        main_html = driver.page_source
        main_response = Selector(text=main_html) 

        
        # get the country hits (number of companies in a specific location)

        ## Opens the county filtering tab
        c = driver.find_element_by_xpath(
            '//div[@class="group tw-flex tw-justify-between tw-items-center tw-px-4 tw-border-t tw-border-gray-200 tw-cursor-pointer"][3]')
        time.sleep(2)
        c.click()
        time.sleep(2)
        response = Selector(text=driver.page_source)

        ## Gets the hits per county
        country_selectors = response.xpath('//div[@class="tw-flex tw-flex-row tw-justify-between tw-mb-2"]')[1:]
        for country in country_selectors:
            self.country_hits.append(int(country.xpath(
                './/span[@class="tw-text-gray-700"]/text()').get()[1:-1].replace(" ", "")))
        print("#####################")
        print(self.country_hits)
        print("######################")
        ## select a county (in same order as the hits found above)
        ## For each county click on the filter to obtain the filtered url
        ## The number of counties can be adjusted if scraping is done in batches
        num_countries = len(self.country_hits)
        for i in range(1,num_countries+1):
            print(f"{i} has started")
            # select the box and load the page
            checkbox = driver.find_element_by_xpath(
                f'//div[@class="tw-flex tw-flex-row tw-justify-between tw-mb-2"][{i}]/label/span')

            time.sleep(2)
            checkbox.click()
            time.sleep(2)
            response = Selector(text=driver.page_source)

            # The commented out code directly below was used to perform the scraping in batches

            ## If you have already scraped a particular county add the index of that county to the visited array
            ## visited = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

            ## check the counts 
            ## if i in visited:
            ##     # used to parse the countries 1 by one
            # #    pass
            if self.country_hits[i-1] > 8000:
                # filter based on revenue if more that 400 pages need to be loaded
                self.revenue_filter(driver, driver.current_url)
            else:
                # get the number of pages and extract all the htmls from the urls
                num_pages = math.ceil(self.country_hits[i-1]/20)
                time.sleep(2)
                url = driver.current_url
                time.sleep(2)
                self.get_pages(driver, num_pages, url)

            # Keep track of the speed of the program
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

    def get_pages(self, driver_l, num_pages, url): 
        """
        For each filtered url get scrape the 400 pages associated with the url. For each page call the parse_page function
        to collect the data for that page.
        """

        url = url + "?page="
        for i in range(1,num_pages+1):
            page_url = url+str(i)
            driver_l.get(page_url)
            time.sleep(1) # can increase this to increase the number of pages
            self.parse_page(driver_l.page_source)

    def parse_page(self, html):
        """
        create a list of names and number that can be added to the global names and numbers.
        """
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


    def revenue_filter(self, driver, base_url):
        """
        Filter the url based on revenue to allow us to scrape more data. This was needed because some counties had more than
        8000 companies. The revenue filter was not done by performing selenium actions but rather by manipulating the url.
        """
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

            # Inga träffar mean no hits
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
        """
        Once all the names and ids have been scraped this function writes all of them to a file specified in the command 
        line.
        """
        assert len(self.numbers) == len(self.names)
        for i in range(len(self.numbers)):
            yield {
                'company_no': str(self.numbers[i]),
                'company_name': self.names[i]
            }
