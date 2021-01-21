# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.exporters import CsvItemExporter
import os

class ExploreScraperPipeline(object):


    def open_spider(self, spider):
        # open files
        # # self.status_file = open(os.getcwd()+"/data/financials/status_forms_test1000.csv",'w+b')
        # # self.fin_file = open(os.getcwd()+"/data/financials/fin_forms_test1000.csv", 'w+b')
        # # self.status_exporter = CsvItemExporter(self.status_file)
        # # self.fin_exporter = CsvItemExporter(self.fin_file)
        #self.status_exporter.start_exporting()
        #self.fin_exporter.start_exporting
        pass

    def close_spider(self, spider):
        # close files
        # # self.status_exporter.finish_exporting()
        # # self.fin_exporter.finish_exporting()
        # # self.status_file.close()
        # # self.fin_file.close()
        pass


    def process_item(self, item, spider):
        # write items to files

        # # if spider.name == 'status':
        # #     self.status_exporter.export_item(item)
        # # elif spider.name == 'financials':
        # #     self.fin_exporter.export_item(item)
        return item
