# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from shutil import which
from scrapy.selector import Selector
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas as pd
import numpy as np
import math


class BoardSpider(scrapy.Spider):
    name = 'board'
    allowed_domains = ['www.allabolag.se']
    start_urls = ['https://www.allabolag.se/5560004615/befattningar/']

    # getting the ids that have already been collected from the base ids [already collected 7000]
    base = pd.read_csv(os.getcwd()+"/data/List of Base Companies.csv", encoding='iso-8859-1')
    base_ids = list(base['company_no'].unique())[:7000]

    # get the ids from the true dataset and remove the ids that have already been collected
    data = pd.read_csv(os.getcwd()+"/data/financials/financials_status_forms_clean2.csv")
    data_filtered = data[~data['id'].isin(base_ids)]
    ids = list(data_filtered['id'].unique())

    all_companies = []

    load_time = 1

    def __init__(self):

        self.s = time.time()

        firefox_options = Options()
        firefox_options.add_argument("--headless")

        firefox_path = which("geckodriver-v0.28.0-linux64/geckodriver")

        # disabling cookies
        fp = webdriver.FirefoxProfile()
        fp.set_preference("network.cookie.cookieBehavior", 2)

        self.driver = webdriver.Firefox(
            executable_path=firefox_path, options=firefox_options, firefox_profile=fp)

        count = 0
        for Id in self.ids[50000:58000]:
            self.driver.get(f'https://www.allabolag.se/{Id}/befattningar/')
            time.sleep(self.load_time)
            print(f"%%%%%%%%%%%%%%%%%%%% {count} %%%%%%%%%%%%%%%%%%")
            count+=1

            response = Selector(text=self.driver.page_source)

            # get all the info for that specific company
            companies_dict = self.parse_page(response)
            self.all_companies.append(companies_dict)

        self.driver.quit()

    def parse_page(self, response):

        # explicitely defining storage
        executives_dict = {}
        name = None
        Id = None
        num_board_members = None
        avg_age_board = None
        executives = []
        active_assignments = []
        prev_assignments = []
        companies = []

        # get the company name
        name = response.xpath('//h1[1]/text()').get()
        if name:
            name = name.replace(",", ";")
        else:
            name = np.nan

        # get the company id
        Id = response.xpath('//div[@class="subheadline tw-mt-4"]/span/text()').get()
        if Id:
            Id = Id.replace('\n', '').replace('-', '').strip()
        else:
            Id = np.nan

        # getting the number of board members
        num_members_text = response.xpath('//h1[contains(text(),"Befattningshavare")]/following-sibling::div/div/p/text()').get()

        if num_members_text:
            num_board_members = int(num_members_text.split(" ")[3])
        else:
            num_board_members = np.nan

        # get the average age of the board
        avg_age_board = response.xpath(
            '//h4[@class="tw-flex tw-items-end text-8xl tw-leading-none tablet:tw-h-40"]/text()').get()

        if avg_age_board:
            pass
        else:
            avg_age_board = np.nan

        # getting the information for each executive
        executives, active_assignments, prev_assignments, companies = self.get_executives_info(response)

        # create the company dictionary 
        executives_dict['name'] = name
        executives_dict['id'] = Id
        executives_dict['num_board_members'] = num_board_members
        executives_dict['avg_age_board'] = avg_age_board
        executives_dict['executives'] = executives
        executives_dict['active_assignments'] = active_assignments
        executives_dict['prev_assignments'] = prev_assignments
        executives_dict['companies'] = companies

        return executives_dict


    def get_executives_info(self, response):

        # defining storage
        executive_names = []
        active_assignments = []
        prev_assignments = []
        companies = []

        # getting the executives with assignments
        excecutive_assignments = response.xpath(
            '//h3[contains(text(),"Exekutiva befattningar")]').get()

        if excecutive_assignments:

            executives = response.xpath(
                '//div[@class = "tw-flex tw-w-full tw-flex-col"][1]/div/div[@class="tw-px-2 tw-py-3 tablet:tw-px-2 tablet:tw-py-3 tablet:tw-flex tablet:tw-justify-between tablet:tw-items-center hover:tw-bg-gray-100"]')

            i = 1
            for executive in executives:

                # helps to get the correct arrow
                i+=1

                # storage for a single executive
                name = None
                exec_active_assignments = None
                exec_prev_assignments = None
                exec_companies = ''

                # get the name of the executive
                name = executive.xpath(".//div/h3/a/text()").get()
                if name:
                    name = " ".join(name.replace(
                        ",", ";").strip().split(" ")[:-1])
                else:
                    name = np.nan

                executive_names.append(name)

                # get the number active assignments
                active_assignment_obj = executive.xpath(
                    './/div[3]/span/text()').get()

                if active_assignment_obj:
                    exec_active_assignments = int(active_assignment_obj.split(" ")[0])
                else:
                    exec_active_assignments = np.nan
                
                active_assignments.append(exec_active_assignments)

                # get the number prev assignments
                prev_assignment_obj = executive.xpath(
                    './/div[4]/span/text()').get()

                if prev_assignment_obj:
                    exec_prev_assignments = int(prev_assignment_obj.split(" ")[0])
                else:
                    exec_prev_assignments = np.nan
                
                prev_assignments.append(exec_prev_assignments)

                # get the names of each of the companies that they work for
                exec_companies = self.get_companies(self.driver.current_url, response, i, exec_active_assignments)
                if exec_companies:
                    # add the data for that specific executive
                    companies.append(exec_companies)
                else:
                    companies.append(str(np.nan))
            
        else:
            # create data that can act as a place holder for the comapnies that don't have any data
            pass

        return executive_names, active_assignments, prev_assignments, companies

    def get_companies(self, original_url, response, exec_count, active_assignments):
        exec_companies = []
        exec_companies_string = ''

        # click on the arrow to load the info that we need

        # first check if the arrow exists
        arrow_obj = response.xpath(
            f'//div[@class="tw-flex tw-w-full tw-flex-col"][1]/div[{exec_count}]/div/div[4]/i')
        
        if not arrow_obj:
            # if there is no arrow object then just return the nones
            return None

        arrow = self.driver.find_element_by_xpath(
            f'//div[@class="tw-flex tw-w-full tw-flex-col"][1]/div[{exec_count}]/div/div[4]/i')
        self.driver.execute_script("arguments[0].click();", arrow)
        new_resp = Selector(text=self.driver.page_source)

        if active_assignments > 3:

            # get the link to all the companies
            link = new_resp.xpath(
                '//div[@class="tw-mt-8"]/div[@class="tw-flex tw-justify-center tw-my-3"]/a/@href').get()

            # calculate the number of pages that need to be loaded
            num_pages = math.ceil(active_assignments/20)

            # setting the base url
            base_url = "https://www.allabolag.se"

            # loop through the pages to get the companies
            for j in range(num_pages):

                self.driver.get(base_url+link+f'?page={j+1}')
                time.sleep(2)
                search_results_pages = Selector(text=self.driver.page_source)

                # get company names
                search_results = search_results_pages.xpath(
                    '//div[@class="search-results__item tw-flex-1"]')

                # go get all the names
                for company in search_results:
                    exec_company_assignment_name = company.xpath(
                        './/div[2]/h2/a/text()').get()
                    if exec_company_assignment_name:
                        exec_company_assignment_name = exec_company_assignment_name.strip().replace(',', ';')
                        
                    else:
                        exec_companies_assignmant_name = str(np.nan)

                    exec_companies.append(exec_company_assignment_name)

        else:
            # can get all the info we need from current page
            exec_assingments = new_resp.xpath('//div[@class="tw-mt-8"]/div[1]/div')
            for assignment in exec_assingments:

                exec_company_assignment_name = assignment.xpath('.//div/h3/a/text()').get()
                if exec_company_assignment_name:
                    exec_company_assignment_name = exec_company_assignment_name.strip().replace(",", ";")
                else:
                    exec_company_assignment_name = str(np.nan)

                exec_companies.append(exec_company_assignment_name)

        #creating string that can go into the dataframe
        exec_companies_string = '|'.join(exec_companies)

        # load orignal page 
        self.driver.get(original_url)
        time.sleep(self.load_time)

        return exec_companies_string
        

    def parse(self, response):
        for i in range(len(self.all_companies)):
            # get the company info
            company_dict = self.all_companies[i]
            # loop through all the executives 
            for j in range(len(company_dict['executives'])):
                yield {
                    'company':company_dict['name'],
                    'id': company_dict['id'],
                    'number_of_board_memebers': company_dict['num_board_members'],
                    'average_age_board': company_dict['avg_age_board'],
                    'executives': company_dict['executives'][j],
                    'total_active_assignments': company_dict['active_assignments'][j],
                    'total_prev_assignments': company_dict['prev_assignments'][j],
                    'companies': company_dict['companies'][j]
                }
        
        e = (time.time() - self.s)/60
        print(f"################### {e} ##################")
