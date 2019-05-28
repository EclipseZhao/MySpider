# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HgmdItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HgmdGeneItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    gene = scrapy.Field()
    aliases = scrapy.Field()
    refseq = scrapy.Field()
    desc = scrapy.Field()
    location = scrapy.Field()

class HgmdMutationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    hgmdid = scrapy.Field()
    gene = scrapy.Field()
    mutation = scrapy.Field()
    variant_class = scrapy.Field()
    phenotype = scrapy.Field()
    rsid = scrapy.Field()

    cits = scrapy.Field()
    pmids = scrapy.Field()
    chrom = scrapy.Field()
    pos = scrapy.Field()
    ref = scrapy.Field()
    alt = scrapy.Field()

