# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OmimItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    prefix = scrapy.Field()
    location = scrapy.Field()
    gene = scrapy.Field()
    genename = scrapy.Field()
    gene_mim = scrapy.Field()
    phenotype = scrapy.Field()
    pheno_mim = scrapy.Field()
    inheritance = scrapy.Field()
    pheno_map_key = scrapy.Field()
    pmids = scrapy.Field()
    hgnc_symbol = scrapy.Field()
