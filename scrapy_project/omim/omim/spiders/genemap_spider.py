# -*- coding: utf-8 -*-
import json
from urllib import urlencode

import scrapy

from omim.utils import UserAgent
from omim.items import OmimItem


class OmimSpider(scrapy.Spider):

    name = 'genemap_spider'
    allowed_domains = ['www.omim.org']

    def __init__(self, **kwargs):

        self.max_page = int(kwargs.get('max_page', 65535))
        self.start = int(kwargs.get('start', '1'))
        self.limit = kwargs.get('limit', '5')
        self.filter = kwargs.get('filter', 'gm_exists:true')
        self.sort = kwargs.get('sort', 'chromosome_number asc, chromosome_sort asc')
        self.prefix = kwargs.get('prefix', '*,+,#,%,none')
        self.outfile = kwargs.get('outfile', 'omim.genemap.xls')

        self.now_page = self.start

    def start_requests(self):

        for prefix in self.prefix.split(','):
            params = {
                'index': 'entry',
                'retrieve': 'geneMap',
                'search': 'prefix:' + prefix,
                'start': self.start,
                'limit': self.limit,
                'filter': self.filter,
                'sort': self.sort,
            }

            self.logger.debug(json.dumps(params, indent=2))

            url = 'https://www.omim.org/search/?' + urlencode(params)
            yield scrapy.Request(url, headers=UserAgent.random_ua(), meta={'prefix': prefix})

    def parse(self, response):
        '''
            爬取geneMap表格
        '''
        self.logger.info('>>> \033[32mcrawling page {}\033[0m'.format(self.now_page))

        # soup = bs4.BeautifulSoup(response.body, 'lxml')
        msg = response.css('#content .container')[0].re(r'Results: .+? entries.')[0]
        self.logger.info('\033[36m{} of search prefix:{}\033[0m'.format(msg, response.meta['prefix']))

        self.logger.debug('>>> get next page ...')
        next_page = None
        for a in response.css('a[href*="?index=entry"]'):
            if 'Next' in a.css('::text').get():
                self.logger.debug(a.attrib['href'])
                next_page = a
                break

        tbody = response.css('#content table tbody')

        for tr in tbody[0].css('tr'):

            # 每行返回一个item
            item = OmimItem()

            tds = tr.css('td')

            if len(tds) == 11:
                a = tds[1].css('span a')
                if len(a) == 2:
                    location = a[-1].css('::text').get('.')
                else:
                    location = tds[1].css('span::text').getall()[-1].strip()

                gene = tds[2].css('span::text').get('.').strip()
                genename = tds[3].css('span::text').get('.').strip()
                gene_mim = tds[4].css('span a::text').get('.').strip()
                phenotype = tds[5].css('span::text').get('.').strip()
                pheno_mim = tds[6].css('span a::text').get('.').strip()
                inheritance = tds[7].css('span abbr::text').getall()
                pheno_map_key = tds[8].css('span abbr::text').get('.').strip()
            # 一个基因多个表型的情况，只有4列
            else:
                phenotype = tds[0].css('span::text').get('.').strip()
                pheno_mim = tds[1].css('span a::text').get('.').strip()
                inheritance = tds[2].css('span abbr::text').getall()
                pheno_map_key = tds[3].css('span abbr::text').get('.').strip()

            inheritance = ','.join(inheritance) or '.'
            tmp_dict = locals().copy()
            keys = 'location gene genename gene_mim phenotype pheno_mim inheritance pheno_map_key'.split()
            for key in keys:
                item[key] = tmp_dict[key]

            # ============================================================================================================
            # 注意：
            #     scrapy.Request要么返回Item，要么返回Request，不能返回一个值
            #     即不能 pmids = scrapy.Request(entry_url, headers=UserAgent.random_ua(), callback=self.search_entry_pmid)
            #     dont_filter=True 不过滤重复
            # ============================================================================================================
            response.meta['item'] = item
            entry_url = response.urljoin('/entry/' + gene_mim)
            self.logger.debug('get pmids for entry %s', gene_mim)

            yield scrapy.Request(
                entry_url,
                headers=UserAgent.random_ua(),
                callback=self.search_entry_detail,
                meta=response.meta,
                dont_filter=True)

        # ========================================================================
        # 使用递归的方式进行爬取，当下一页存在且没有超过设定最大page时，自动爬取下一页
        # ========================================================================
        if (next_page is not None) and (self.now_page < self.max_page):
            self.now_page += 1
            yield response.follow(
                next_page,
                headers=UserAgent.random_ua(),
                meta=response.meta,
                callback=self.parse)

    def search_entry_detail(self, response):
        '''
            获取指定MIM的文献列表
        '''
        ol = response.css('#referencesFold ol')
        pmids = ol.re(r'href="https://www\.ncbi\.nlm\.nih\.gov/pubmed/(\d+)"')
        pmids = ','.join(pmids) or '.'

        hgnc_symbol = '.'
        hgnc_alink = response.css('#approvedGeneSymbols')
        if hgnc_alink:
            hgnc_symbol = hgnc_alink[0].xpath('following-sibling::p[1]').css('a::text').get()

        item = response.meta['item']
        item['pmids'] = pmids
        item['hgnc_symbol'] = hgnc_symbol
        item['prefix'] = response.meta['prefix']

        yield item
