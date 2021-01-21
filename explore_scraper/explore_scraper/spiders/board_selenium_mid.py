# -*- coding: utf-8 -*-
import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
import numpy as np
import pandas as pd
import os
import time
import math

class BoardSeleniumMidSpider(scrapy.Spider):
    name = 'board_selenium_mid'

    companies = pd.read_csv(
        os.getcwd()+"/data/List of Base Companies.csv", encoding='iso-8859-1')

    ids = list(companies['company_no'].unique())
    start_urls = [
        f'https://www.allabolag.se/{Id}/befattningar' for Id in ['5568589823', '5563014082', '5566764535', '5564791738'][2:4]]

    s = time.time()
    count = 0

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)


    def parse(self, response):

        # getting the driver
        driver = response.meta['driver']

        # name
        name = response.xpath('//h1[1]/text()').get()
        if name:
            name = name.replace(",", ";")

        print(f"##################### {name} #######################")

        # id
        Id = response.xpath('//div[@class="subheadline tw-mt-4"]/span/text()').get()
        if Id:
            Id = Id.replace('\n', '').replace('-', '').strip()

        print(f"##################### {Id} #######################")

        # getting the number of board members
        num_members_text = response.xpath(
            '//h1[contains(text(),"Befattningshavare")]/following-sibling::div/div/p/text()').get()

        if num_members_text:
            num_members = num_members_text.split(" ")[3]
        else:
            num_members = num_members_text

        # get the average age of the board
        avg_age = response.xpath(
            '//h4[@class="tw-flex tw-items-end text-8xl tw-leading-none tablet:tw-h-40"]/text()').get()

        # getting the total assignments
        excecutive_assignments = response.xpath(
            '//h3[contains(text(),"Exekutiva befattningar")]').get()

        # creating storage
        exec_names = []
        total_active_assignments = []
        total_prev_assignments = []
        execs_companies = []

        # number of executive positions
        num_execs = 0

        if excecutive_assignments:

            executives = response.xpath(
                '//div[@class = "tw-flex tw-w-full tw-flex-col"][1]/div/div[@class="tw-px-2 tw-py-3 tablet:tw-px-2 tablet:tw-py-3 tablet:tw-flex tablet:tw-justify-between tablet:tw-items-center hover:tw-bg-gray-100"]')

            i = 1
            for executive in executives:
                i += 1
                num_execs+=1

                exec_name = executive.xpath(".//div/h3/a/text()").get()
                if exec_name:
                    exec_name = " ".join(exec_name.replace(",",";").strip().split(" ")[:-1])
                    exec_names.append(exec_name)
                else:
                    exec_names.append(np.nan)

                total_active_assignment_obj = executive.xpath(
                    './/div[3]/span/text()').get()

                if total_active_assignment_obj:
                    total_active_assignments.append(int(total_active_assignment_obj.split(" ")[0]))
                else:
                    total_active_assignments.append(np.nan)

                total_prev_assignment_obj = executive.xpath(
                    './/div[4]/span/text()').get()

                if total_prev_assignment_obj:
                    total_prev_assignments.append(int(total_prev_assignment_obj.split(" ")[0]))
                else:
                    total_prev_assignments.append(np.nan)

                # getting the companies that the executives work for

                # need to click on the arrow to load exec info
                print(f"############## {driver.current_url}")
                arrow = driver.find_element_by_xpath(f'//div[@class="tw-flex tw-w-full tw-flex-col"][1]/div[{i}]/div/div[4]/i')
                print("##############")
                driver.execute_script("arguments[0].click();", arrow)
                new_resp = Selector(text=driver.page_source)

                # getting all the companies that belong to that specific exec
                exec_company_assignments = []
                exec_company_assignments_string = ''

                if int(total_active_assignment_obj.split(" ")[0]) > 3:

                    # store the original url
                    original_url = driver.current_url

                    # get the link to all the companies
                    link = new_resp.xpath(
                        '//div[@class="tw-mt-8"]/div[@class="tw-flex tw-justify-center tw-my-3"]/a/@href').get()

                    # calculate how many pages need to be loaded
                    num_pages = math.ceil(int(total_active_assignment_obj.split(" ")[0])/20)

                    # setting the base url
                    base_url = "https://www.allabolag.se"
                    
                    for j in range(num_pages):

                        # load the page
                        driver.get(base_url+link+f'?page={j+1}')
                        time.sleep(1)
                        search_results_pages = Selector(text=driver.page_source)

                        # get the company names
                        search_results = search_results_pages.xpath(
                            '//div[@class="search-results__item tw-flex-1"]')

                        # go get all the names 
                        for company in search_results:
                            exec_company_assignments_name = company.xpath(
                                './/div[2]/h2/a/text()').get()
                            if exec_company_assignments_name:
                                exec_company_assignments_name = exec_company_assignments_name.strip().replace(',',';')
                                exec_company_assignments.append(exec_company_assignments_name)
                            else:
                                exec_company_assignments.append(str(np.nan))

                    # need to reload the original page
                    if len(executives)>1:
                        driver.get(original_url)
                        time.sleep(2)

                    exec_company_assignments_string = '|'.join(
                        exec_company_assignments)
                    execs_companies.append(exec_company_assignments_string)

                else:
                    exec_assingments = new_resp.xpath('//div[@class="tw-mt-8"]/div[1]/div')
                    for assignment in exec_assingments:

                        exec_company_assignments_name = assignment.xpath('.//div/h3/a/text()').get()
                        if exec_company_assignments_name:
                            exec_company_assignments_name = exec_company_assignments_name.strip().replace(",",";")
                            exec_company_assignments.append(exec_company_assignments_name)
                        else:
                            exec_company_assignments.append(str(np.nan))

                    #creating string that can go into the dataframe
                    exec_company_assignments_string = '|'.join(exec_company_assignments)
                    execs_companies.append(exec_company_assignments_string)

        for i in range(num_execs):

            yield {
                'name': name,
                'id': Id,
                'number_of_board_members': num_members,
                'avg_age_of_board': avg_age,
                'executive':exec_names[i],
                'total_active_assignments': total_active_assignments[i],
                'total_prev_assignments': total_prev_assignments[i],
                'assignment_companies': execs_companies[i]
            }   

        self.count += 1
        print(f"$$$$$$$$$$$$$$$$$$ {self.count} $$$$$$$$$$$$$$$$$")
        e = (time.time() - self.s)/60
        print(f"################### {e} ##################")
