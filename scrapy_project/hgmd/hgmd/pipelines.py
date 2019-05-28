# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
from scrapy.exceptions import DropItem

from hgmd.items import HgmdGeneItem, HgmdMutationItem

reload(sys)
sys.setdefaultencoding('utf8')


class HgmdPipeline(object):

    def open_spider(self, spider):
        self.file1 = open('hgmd.genelist.txt', 'w')
        self.header1 = 'gene aliases refseq desc location'.split()
        self.file1.write('#' + '\t'.join(self.header1) + '\n')

        self.file2 = open('hgmd.database.txt', 'w')
        self.header2 = 'hgmdid gene chrom pos ref alt mutation phenotype cits pmids variant_class rsid'.split()
        self.file2.write('#' + '\t'.join(self.header2) + '\n')

    def close_spider(self, spider):
        self.file1.close()
        self.file2.close()

    def process_item(self, item, spider):
        if isinstance(item, HgmdGeneItem):
            line = '\t'.join('{%s}' % each for each in self.header1)
            line = line.format(**dict(item))
            self.file1.write(line + '\n')
        elif isinstance(item, HgmdMutationItem):
            line = '\t'.join('{%s}' % each for each in self.header2)
            line = line.format(**dict(item))
            self.file2.write(line + '\n')

        return item

