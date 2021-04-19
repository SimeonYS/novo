import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NnovoItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class NnovoSpider(scrapy.Spider):
	name = 'novo'
	start_urls = ['https://novo.brb.com.br/releases-imprensa/']

	def parse(self, response):
		post_links = response.xpath('//td/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		try:
			date = response.xpath('//h1/text()').get().split('–')[0].strip()
			title = response.xpath('//h1/text()').get().split('–')[1].strip()
		except IndexError:
			date = response.xpath('//h1/text()').get().split('-')[0].strip()
			title = response.xpath('//h1/text()').get().split('-')[1].strip()
		content = response.xpath('//div[@class="page-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NnovoItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
