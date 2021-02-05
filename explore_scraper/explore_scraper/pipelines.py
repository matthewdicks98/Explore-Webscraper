# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.exporters import CsvItemExporter
import os

class ExploreScraperPipeline(object):
    """
    This class handles the collecting and writing data to the correct files when running the 
    driver code. This gets enabled through enabling(uncommenting) the ITEM_PIPELINES in the 
    settings file. This class must only be used when running the driver code.
    """

    def open_spider(self, spider):
        """
        Opens the files for writing and initializes the exporting
        """
        
        # open files
        self.status_file = open(os.getcwd()+"/data/financials/status_forms_test10.csv",'w+b')
        self.fin_file = open(os.getcwd()+"/data/financials/fin_forms_test10.csv", 'w+b')
        self.status_exporter = CsvItemExporter(self.status_file)
        self.fin_exporter = CsvItemExporter(self.fin_file)

    def close_spider(self, spider):
        """
        Closes the files and exporters
        """

        # close files
        self.status_exporter.finish_exporting()
        self.fin_exporter.finish_exporting()
        self.status_file.close()
        self.fin_file.close()


    def process_item(self, item, spider):
        """
        Processes each item and writes it to the relavent file
        """

        # write items to files
        if spider.name == 'status':
            self.status_exporter.export_item(item)
        elif spider.name == 'financials':
            self.fin_exporter.export_item(item)
        return item
