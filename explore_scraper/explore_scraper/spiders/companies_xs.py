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
import pandas as pd
import numpy as np
import os

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class CompaniesXsSpider(scrapy.Spider):
    name = 'companies_xs'
    allowed_domains = ['www.allabolag.se']
    start_urls = [
        'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_/']
    #c1 = ''
    #test_url = ''
    #Id = ''
    ids = []
    names = []
    sudo_ids = []
   

    def __init__(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        firefox_path = which("geckodriver-v0.28.0-linux64/geckodriver")

        # disabling cookies
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.cookie.cookieBehavior", 2)

        driver = webdriver.Firefox(
            executable_path=firefox_path, options=firefox_options, firefox_profile=fp)

        driver.get(
            'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_?page=1')

        # read in the companies that have a number that ends in XXXX
        xs = pd.read_csv(os.getcwd()+'/data/XS.csv')
        nrows = xs.shape[0]
        unrecognized = 0
        id_not_matched = 0
        s = time.time()
        for i in range(25500,25500):
            c1 = xs.iloc[i]['company_name']
            print("@@@@@@@@@@@@@ "+str(25500-i))
            if not c1.isascii():
                print(f"$$$$$$$$$$$$$$ {c1}")
                unrecognized += 1
                continue
            driver.get(
                'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_?page=1')
            time.sleep(2)
            
            search_box = driver.find_element_by_xpath(
                '//input[@class="search-form__input search-form__input--keyword tw-rounded-l tw-text-gray-500"]')
            search_box.click()
            time.sleep(1)
            search_box.send_keys(c1.replace(";",","))
            search_box.send_keys(Keys.ENTER)
            time.sleep(3)
            
            if driver.current_url == 'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_?page=1':
                time.sleep(3)
            print("################### "+driver.current_url)

            
            response = Selector(text=driver.page_source)
            search_results = response.xpath(
                '//div[@class = "search-results__item tw-flex-1"]/div/h2')
            
            if len(search_results)==0:
                time.sleep(3)
                response = Selector(text=driver.page_source)
                search_results = response.xpath(
                    '//div[@class = "search-results__item tw-flex-1"]/div/h2')

            # the company may not exist anymore
            if response.xpath('//div[@class="search-results__item"]/h3/text()').get() == ' Inga träffar':
                unrecognized += 1
                continue

            # get the first search result
            if str(search_results[0].xpath('.//a/@href').get().split('/')[1])[:6] != str(xs.iloc[i]['company_no'])[:6]:
                id_not_matched += 1
                continue
            else:
                self.ids.append(search_results[0].xpath('.//a/@href').get().split('/')[1])
                self.names.append(c1)
                self.sudo_ids.append(xs.iloc[i]['company_no'])
        
        # for each company
        # search for it in the search box
        # select the first one
        # add to dictionary
        f = open('unrecognized_middle500.txt','w')
        f.write(str(unrecognized)+"\n"+str((time.time()-s)/60)+"\n"+str(id_not_matched))
        f.close()
        driver.close()

    def parse(self, response):
        for i in range(len(self.names)):
            yield{
                'company_no':self.sudo_ids[i],
                'company_name':self.names[i],
                'company_no_real':self.ids[i]
            }
