# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv

class ScrapyGamePipeline:
    def open_spider(self, spider):
        self.file = open('output.csv', 'w', newline='')
        dictWriter = csv.DictWriter(self.file, fieldnames = ["Id", "url", "author_name", "contact_info"])
        dictWriter.writeheader()
        self.writer = csv.writer(self.file, delimiter=',')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        data = ItemAdapter(item)
        self.writer.writerow([data['Id'], data['url'], data['author_name'], data['contact_info']])
        return item
