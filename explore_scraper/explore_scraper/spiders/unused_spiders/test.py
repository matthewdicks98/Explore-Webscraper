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


class CompaniesXsSpider(scrapy.Spider):
    name = 'companies_xs'
    allowed_domains = ['www.allabolag.se']
    start_urls = [
        'https://www.allabolag.se/bransch/bygg-design-inredningsverksamhet/6/_/']
    url = ''
    name = ''

    def __init__(self):
        firefox_options = Options()
        firefox_options.add_argument("--headless")

        firefox_path = which("geckodriver-v0.28.0-linux64/geckodriver")

        # disabling cookies
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.cookie.cookieBehavior", 2)

        driver = webdriver.Firefox(
            executable_path=firefox_path, options=firefox_options, firefox_profile=fp)

        # read in the companies that have a number that ends in XXXX
        xs = pd.read_csv('../data/XS.csv')

        # try do the bottom for one company
        search_box = driver.find_element_by_xpath(
            '//input[@class="tw-placeholder-gray-500 tw-text-gray-500 tw-flex-1 tw-h-12"]')
        self.name = xs.iloc[2]['company_name']
        search_box.send_keys(name)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)
        self.url = driver.current_url

        # for each company
        # search for it in the search box
        # select all the companies with the same 4x id
        # for each of them get their id
        # add to dictionary

    def parse(self, response):
        yield {
            'name': self.name,
            'url': self.url
        }
