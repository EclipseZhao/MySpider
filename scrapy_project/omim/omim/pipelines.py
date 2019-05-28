# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from omim.items import OmimItem


class OmimPipeline(object):

    def open_spider(self, spider):
        self.header = 'prefix location gene genename gene_mim phenotype pheno_mim inheritance pheno_map_key pmids hgnc_symbol'.split()
        self.file = open(spider.outfile, 'w')
        self.file.write('\t'.join(self.header) + '\n')

    def close_spider(self, spider):
        self.file.close()
        spider.logger.info('\033[32msave file: {}\033[0m'.format(spider.outfile))

    def process_item(self, item, spider):
        if isinstance(item, OmimItem):
            line = '\t'.join('{%s}' % each for each in self.header)
            line = line.format(**dict(item))
            self.file.write(line + '\n')
        return item
