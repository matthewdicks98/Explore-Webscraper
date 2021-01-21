# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os 
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from shutil import which
from scrapy.selector import Selector
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
import math

class FinancialsSpider(scrapy.Spider):
    name = 'financials'
    allowed_domains = ['www.allabolag.se']
    i = 0

    companies = pd.read_csv(os.getcwd()+"/data/financials/final_companies.csv")

    ids = list(companies['company_no'].values)

    start_urls = [f'https://www.allabolag.se/{Id}/bokslut' for Id in ids[:1000]]


    def parse(self, response):
        self.i+=1
        print(self.i)
        for element in response.css('html.no-js'):
            for i in range(2, len(set(element.css('label.chart__label::text').getall()))+2):
                yield {
                    'company': element.css('h1::text').get().replace(",",";"),
                    'id': int(element.css('span.orgnr::text')[1].get().replace('\n', '').strip().replace('-', '')),
                    #'year': element.css('label::text')[i-2].get(),
                    'year': element.xpath(f'//th[@class = "data-pager__page data-pager__page--{i-2}"]/text()').get().strip()[:7][:4],
                    'date': element.xpath(f'//th[@class = "data-pager__page data-pager__page--{i-2}"]/text()').get().strip()[:7],
                    'net_sales': element.css(f'td:nth-child({i})::text').get().replace('\n', '').replace(' ', '').strip(),
                    'other_sales': element.css(f'td:nth-child({i})::text')[1].get().replace('\n', '').replace(' ', '').strip(),
                    'op_profit_ebit': element.css(f'td:nth-child({i})::text')[2].get().replace('\n', '').replace(' ', '').strip(),
                    'prof_after_net_fin_items': element.css(f'td:nth-child({i})::text')[3].get().replace('\n', '').replace(' ', '').strip(),
                    'results': element.css(f'td:nth-child({i})::text')[4].get().replace('\n', '').replace(' ', '').strip(),
                    'sub_unpaid_cap': element.css(f'td:nth-child({i})::text')[5].get().replace('\n', '').replace(' ', '').strip(),
                    'fixed_assets': element.css(f'td:nth-child({i})::text')[6].get().replace('\n', '').replace(' ', '').strip(),
                    'current_assets': element.css(f'td:nth-child({i})::text')[7].get().replace('\n', '').replace(' ', '').strip(),
                    'assets': element.css(f'td:nth-child({i})::text')[8].get().replace('\n', '').replace(' ', '').strip(),
                    'equity': element.css(f'td:nth-child({i})::text')[9].get().replace('\n', '').replace(' ', '').strip(),
                    'untaxed_reserves': element.css(f'td:nth-child({i})::text')[10].get().replace('\n', '').replace(' ', '').strip(),
                    'provisions': element.css(f'td:nth-child({i})::text')[11].get().replace('\n', '').replace(' ', '').strip(),
                    'lt_liabilities': element.css(f'td:nth-child({i})::text')[12].get().replace('\n', '').replace(' ', '').strip(),
                    'curr_liabilities': element.css(f'td:nth-child({i})::text')[13].get().replace('\n', '').replace(' ', '').strip(),
                    'lia_and_equity': element.css(f'td:nth-child({i})::text')[14].get().replace('\n', '').replace(' ', '').strip(),
                    'salar_board_ceo': element.css(f'td:nth-child({i})::text')[15].get().replace('\n', '').replace(' ', '').strip(),
                    'royalties_board_ceo': element.css(f'td:nth-child({i})::text')[16].get().replace('\n', '').replace(' ', '').strip(),
                    'sal_other_empl': element.css(f'td:nth-child({i})::text')[17].get().replace('\n', '').replace(' ', '').strip(),
                    'perf_other_empl': element.css(f'td:nth-child({i})::text')[18].get().replace('\n', '').replace(' ', '').strip(),
                    'social_exp': element.css(f'td:nth-child({i})::text')[19].get().replace('\n', '').replace(' ', '').strip(),
                    'dividends': element.css(f'td:nth-child({i})::text')[20].get().replace('\n', '').replace(' ', '').strip(),
                    'revenue': element.css(f'td:nth-child({i})::text')[21].get().replace('\n', '').replace(' ', '').strip(),
                    'num_employes': element.css(f'td:nth-child({i})::text')[22].get().replace('\n', '').replace(' ', '').strip(),
                    'net_sales_empl': element.css(f'td:nth-child({i})::text')[23].get().replace('\n', '').replace(' ', '').strip(),
                    'pers_cost_empl': element.css(f'td:nth-child({i})::text')[24].get().replace('\n', '').replace(' ', '').strip(),
                    'op_prof_ebitda': element.css(f'td:nth-child({i})::text')[25].get().replace('\n', '').replace(' ', '').strip(),
                    'net_change': element.css(f'td:nth-child({i})::text')[26].get().replace('\n', '').replace(' ', '').replace(",",".").strip(),
                    'du_pont_model': element.css(f'td:nth-child({i})::text')[27].get().replace('\n', '').replace(' ', '').replace(",", ".").strip(),
                    'prof_margin': element.css(f'td:nth-child({i})::text')[28].get().replace('\n', '').replace(' ', '').replace(",", ".").strip(),
                    'gross_prof': element.css(f'td:nth-child({i})::text')[29].get().replace('\n', '').replace(' ', '').replace(",", ".").strip(),
                    'working_cap': element.css(f'td:nth-child({i})::text')[30].get().replace('\n', '').replace(' ', '').replace(",", ".").strip(),
                    'solidity': element.css(f'td:nth-child({i})::text')[31].get().replace('\n', '').replace(' ', '').replace(",", ".").strip(),
                    'quick_ratio': element.css(f'td:nth-child({i})::text')[32].get().replace('\n', '').replace(' ', '').replace(",", ".").strip(),
                }
