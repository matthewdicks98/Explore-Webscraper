# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import os


class StatusSpider(scrapy.Spider):
    name = 'status'
    allowed_domains = ['www.allabolag.se']

    companies = pd.read_csv(os.getcwd()+"/data/financials/final_companies.csv")

    ids = list(companies['company_no'].values)

    start_urls = [
        f'https://www.allabolag.se/{Id}/verksamhet/' for Id in ids]

    # company with banckrupsy: 5567658033

    def parse(self, response):
        
         for element in response.css('html.no-js'):
            # get the status
            status = None
            actual_status = None

            if element.xpath('//div[@class = "flex-grid__column"][2]/div/dl/dd[1]/text()').get() == ' Bolaget är aktivt':
                status = 'aktivt'
                actual_status = 'aktivt'
            elif 'Registrerad' in element.xpath('//div[@class = "flex-grid__column"][2]/div/dl/dd[1]/text()').get():
                status = 'Registrerad'
                actual_status = 'Registrerad'
            elif element.xpath('//div[@class = "flex-grid__column"][2]/div/dl/dd[1]/text()').get() == ' Bolaget är inaktivt':
                status = 'inaktivt'
                actual_status = 'inaktivt'
                
            # get the remark
            remark = None
            default_date = None
            remarks = []
            if element.xpath('//dl[@class = "accordion-body display-none"]/dd[1]/text()').get() == ' Bolaget är aktivt':
                remark = None
            else:
                for list_item in element.xpath('//ul[@class = "remarks"]/li'):
                    text = list_item.xpath(".//text()").get().strip()
                    if 'Konkurs' in text:
                        bankrup =  text.split(" ")[0]
                        bankrup_type = text.split(" ")[1]
                        remark = bankrup+" "+bankrup_type
                        default_date = text.split(" ")[-1]
                        break
            
            if remark == None and actual_status == 'Registrerad':
                status = 'aktivt'
            elif remark != None and actual_status == 'Registrerad':
                status = 'inaktivt'

            company_form = element.xpath("//*[contains(text(),'Bolagsform')]/following-sibling::dd[1]/text()").get()
            county = element.xpath("//*[contains(text(),'Länsäte')]/following-sibling::dd[1]/text()").get()
            registered_date = element.xpath("//*[contains(text(),'Bolaget registrerat')]/following-sibling::dd[1]/text()").get()
            industry = element.xpath("//*[contains(text(),'Bransch')]/following-sibling::ul/li/a/text()").get()
            operation = element.xpath("//*[contains(text(),'Bransch')]/following-sibling::ul/li/ul/li/a/text()").get()

            if county:
                county = county.strip().replace(",", ";")

            if company_form:
                company_form = company_form.strip().replace(",", ";")

            if registered_date:
                registered_date = registered_date.strip()

            if industry:
                industry = industry.strip().replace(",", ";")

            if operation:
                operation = operation.strip().replace(",", ";")

            yield {
                'company': element.css('h1::text').get().replace(",",";"),
                'id': int(element.css('span.orgnr::text')[1].get().replace('\n','').replace('-','').strip()),
                #'status': element.css('dd:contains("Bolaget")::text').get() or element.css('dd:contains("Registrerad")::text').get(),
                'status':status,
                'actual_status': actual_status,
                'remark': remark,
                'default_date': default_date,
                'company_form': company_form,
                'county': county,
                'industry': industry,
                'operation': operation,
                'registered_date': registered_date
            }
