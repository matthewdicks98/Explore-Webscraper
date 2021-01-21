# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import os


class FormsSpider(scrapy.Spider):
    name = 'forms'
    allowed_domains = ['www.allabolag.se']

    companies = pd.read_csv(os.getcwd()+"/data/financials/financials_status_clean1.csv")

    ids = list(companies['id'].unique())
    #print(len(ids))

    start_urls = [f'https://www.allabolag.se/{Id}/verksamhet/' for Id in ids]

    #start_urls = ['https://www.allabolag.se/5560781345/verksamhet/']

    def parse(self, response):

        for element in response.css('html.no-js'):

            industry = element.xpath("//*[contains(text(),'Bransch')]/following-sibling::ul/li/a/text()").get()
            operation = element.xpath(
                "//*[contains(text(),'Bransch')]/following-sibling::ul/li/ul/li/a/text()").get()

            if industry:
                industry = industry.strip().replace(",", ";")

            if operation:
                operation = operation.strip().replace(",", ";")

            yield {
                'company': element.css('h1::text').get().replace(",", ";"),
                'id': int(element.css('span.orgnr::text')[1].get().replace('\n', '').replace('-', '').strip()),
                'company_form': element.xpath("//*[contains(text(),'Bolagsform')]/following-sibling::dd[1]/text()").get().strip().replace(",",";"),
                'county': element.xpath("//*[contains(text(),'Länsäte')]/following-sibling::dd[1]/text()").get().strip().replace(",", ";"),
                'industry': industry,
                'operation': operation,
                'registered_date': element.xpath("//*[contains(text(),'Bolaget registrerat')]/following-sibling::dd[1]/text()").get().strip()
            }
