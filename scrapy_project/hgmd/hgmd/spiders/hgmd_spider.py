# -*- coding: utf-8 -*-
import re
import scrapy

from hgmd.items import HgmdGeneItem, HgmdMutationItem


class HgmdSpiderSpider(scrapy.Spider):

    name = 'hgmd_spider'
    allowed_domains = ['hgmdtrial.biobase-international.com']

    def __init__(self, **kwargs):
        self.base_url = 'http://hgmdtrial.biobase-international.com/hgmd/pro'
        self.page = kwargs.get('page', '1')
        self.limit = kwargs.get('limit', '50')
        self.max_page = int(kwargs.get('max_page', 99999999))

        self.genes = kwargs.get('gene')

    def start_requests(self):

        if self.genes:
            for gene in self.genes.split(','):
                mutation_url = self.base_url + '/all.php'
                data = {
                    'gene': gene,
                    'sort': 'location',
                    'database': 'Get all mutations'
                }
                yield scrapy.FormRequest(
                    mutation_url,
                    method='POST',
                    formdata=data,
                    callback=self.parse_mutation,
                    meta={'gene': gene})
        else:
            gene_url = self.base_url + '/browseGene.php'
            data = {
                'display': 'All',
                'page': self.page,
                'limit': self.limit
            }
            print data
            yield scrapy.FormRequest(gene_url, method='POST', formdata=data, meta={'data': data})

    def parse(self, response):
        '''
            获取所有基因列表
        '''
        td = response.css('table')[0].css('td')[1]
        now_page = int(td.css('form input[name="page"]').attrib['value'])
        total_page = int(td.re(r' of (\d+)')[0])

        self.logger.info('\033[32mcrawling genelist at page {now_page}/{total_page}\033[0m'.format(**locals()))

        for tr in response.css('table')[1].css('tr')[1:]:
            item = HgmdGeneItem()
            item['gene'] = tr.css('.center a::text').get()
            item['aliases'] = tr.css('td>span::text').get()
            item['refseq'] = tr.css('td')[1].css('::text').get()
            item['desc'] = tr.css('td')[2].css('::text').get()
            item['location'] = tr.css('td')[3].css('::text').get()
            yield item

            # 获取每个基因上的所有变异
            mutation_url = self.base_url + '/all.php'
            data = {
                'gene': item['gene'],
                'sort': 'location',
                'database': 'Get all mutations'
            }
            yield scrapy.FormRequest(
                mutation_url,
                method='POST',
                formdata=data,
                callback=self.parse_mutation,
                meta={'gene': item['gene']})

        # 递归获取下一页基因
        if (now_page < total_page) and (now_page < self.max_page):
            response.meta['data']['page'] = str(now_page + 1)
            yield scrapy.FormRequest(
                response.url,
                method='POST',
                formdata=response.meta['data'],
                meta=response.meta)

    def parse_mutation(self, response):
        '''
            获取一个基因上的所有突变
        '''
        heading = ''.join(response.css('h3.heading')[0].css('*::text').getall())
        self.logger.info('\033[36m{}\033[0m'.format(heading))

        for table in response.css('table.gene'):
            for tr in table.css('tr')[1:]:
                item = HgmdMutationItem()
                item['gene'] = response.meta['gene']
                item['hgmdid'] = tr.css('td form input[type="submit"]').attrib['value']
                item['mutation'] = '|'.join(''.join(each.css('::text').getall()) for each in tr.css('td')[1:-4])
                item['variant_class'] = tr.css('td')[-4].css('span::text').get()
                item['phenotype'] = tr.css('td')[-3].css('::text').get('.')
                item['rsid'] = '.'
                dbsnp = tr.css('td')[-1].css('a[target="dbSNP"]')
                if dbsnp:
                    item['rsid'] = dbsnp.attrib['title'].split()[-1]

                mutation_detail_url = self.base_url + '/mut.php?acc=' + item['hgmdid']

                yield scrapy.Request(mutation_detail_url, meta={'item': item}, callback=self.parse_mutation_detail)
                # yield item

    def parse_mutation_detail(self, response):

        item = response.meta['item']

        for tr in response.css('table.gene')[3].css('tr'):
            if tr.css('a::text').get() == 'Variant Call Format (VCF)':
                vcf_format = tr.css('td::text').getall()[-1].strip()
                if vcf_format == 'Not available':
                    chrom = pos = ref = alt = '.'
                else:
                    chrom, pos, _, ref, alt = vcf_format.split()
                break

        cits = []
        pmids = []

        for tr in response.css('table.gene')[2].css('tr')[1:]:
            paper = ' '.join(each.strip() for each in tr.css('td')[0].css('::text').extract())
            try:
                cit, pmid, title = re.findall(r'\d+?\. (.+?)\s*PubMed:\s*(\d+)\s*(.+)$', paper)[0]
                cits.append(cit)
                pmids.append(pmid)
            except IndexError:
                self.logger.debug('NO PubMed: {}'.format(item['hgmdid']))
                # raise scrapy.exceptions.CloseSpider('special cit for {}'.format(item['hgmdid']))
        cits = '|'.join(cits)
        pmids = '|'.join(pmids)

        temp_dict = locals().copy()
        for key in 'chrom pos ref alt cits pmids'.split():
            item[key] = temp_dict[key]

        yield item