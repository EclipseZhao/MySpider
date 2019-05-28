# -*- coding: utf-8 -*-
import re
import time
import random
from urllib import urlencode

import scrapy

from omim.utils import UserAgent
from omim.items import OmimItem


class OmimSpider(scrapy.Spider):

    name = 'entry_spider'
    allowed_domains = ['www.omim.org']

    def __init__(self, **kwargs):
        self.base_url = 'https://www.omim.org'
        self.mim = kwargs.get('mim')

    def start_requests(self):

        if self.mim:
            for mim in self.mim.split(','):
                entry_url = self.base_url + '/entry/' + mim
                yield scrapy.Request(entry_url, headers=UserAgent.random_ua(), callback=self.parse_entry)
        else:
            url = self.base_url + '/static/omim/data/mim2gene.txt'
            yield scrapy.Request(url, headers=UserAgent.random_ua(), callback=self.parse_mim2gene)

    def parse_mim2gene(self, response):

        body = iter(response.body.split('\n'))
        for n, line in enumerate(body):
            linelist = line.split('\t')
            if line.startswith('#') or 'move' in linelist[0]:
                continue
            mim = linelist[0]

            entry_url = self.base_url + '/entry/' + mim
            yield scrapy.Request(entry_url, headers=UserAgent.random_ua(), callback=self.parse_entry)
            if n > 5:
                break

    def parse_entry(self, response):

        content = response.css('#content .row .col-lg-8')[0]
        title = content.xpath('div[1]')

        prefix = title.xpath('div[1]').css('strong::text').get('none')
        text =  title.xpath('div[2]').css('.mim-font::text').get('').strip()

        print title.xpath('div[4]').css('::text').getall()

        print prefix
        print text
