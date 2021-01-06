# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.exporters import CsvItemExporter
import os

class ExploreScraperPipeline(object):

    # @classmethod
    # def from_crawler(cls, crawler):
    #     pipeline = cls()
    #     crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    #     crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    #     return pipeline

    def open_spider(self, spider):
        # open files
        self.status_file = open(os.getcwd()+"/data/financials/status_60000_.csv",'w+b')
        self.fin_file = open(os.getcwd()+"/data/financials/fin_60000_.csv", 'w+b')
        self.status_exporter = CsvItemExporter(self.status_file)
        self.fin_exporter = CsvItemExporter(self.fin_file)
        #self.status_exporter.start_exporting()
        #self.fin_exporter.start_exporting()

    def close_spider(self, spider):
        # close files
        self.status_exporter.finish_exporting()
        self.fin_exporter.finish_exporting()
        self.status_file.close()
        self.fin_file.close()


    def process_item(self, item, spider):
        # write items to files

        if spider.name == 'status':
            self.status_exporter.export_item(item)
        elif spider.name == 'financials':
            self.fin_exporter.export_item(item)
        return item
