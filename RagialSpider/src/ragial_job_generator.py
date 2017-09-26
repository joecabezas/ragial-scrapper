import logging
import os
import json

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class RagialJobGenerator():

	SPIDER_OUPUT_JSON = 'spider_output.json'

	def __init__(self, inputs):
		# super(RagialJobGenerator, self).__init__()
		self.inputs = inputs

	def runSpider(self):
		start_urls = map(lambda item: item.url, self.inputs.values())

		process = CrawlerProcess(get_project_settings())
		process.crawl(
			'ragialspider',
			domain='ragi.al',
			start_urls=start_urls
		)
		process.start()

	def get_jobs(self):
		self._fetch_spider_data(True)

		# print json.dumps(self.spider_data, indent=4)

		items_processed = []
		for item in self.spider_data:
			processed_item = self._process_item(item)

			if(processed_item):
				items_processed.append(processed_item)

		# print json.dumps(items_processed, indent=4)

		jobs = []
		for processed_item in items_processed:
			item_jobs = self._get_jobs_for_item(processed_item)
			if(item_jobs):
				for job in item_jobs:
					jobs.append(job)

		return jobs

	def _fetch_spider_data(self, call_spider=True):
		if(call_spider):
			try:
				os.remove(self.SPIDER_OUPUT_JSON)
			except OSError:
				pass
			self.runSpider()
		with open(self.SPIDER_OUPUT_JSON) as file:
			self.spider_data = json.load(file)

	#processes each item obtained in spider
	def _process_item(self, item):

		item_url = item.get('item_url')
		input_item = self.inputs.get(item_url)

		if not(input_item):
			return

		logging.debug("_process_item: item: %s", item)
		logging.debug("_process_item: input_item: %s", input_item)
		logging.debug("_process_item: input_item.auto_price: %s", input_item.auto_price)
		logging.debug("_process_item: input_item.maximum_price: %s", input_item.maximum_price)

		buying_price = -1
		if(input_item.auto_price):
			#calculate selling price
			average_price = item.get('average_price')
			std_dev = item.get('std_dev')
			buying_price = average_price - std_dev
		else:
			buying_price = input_item.maximum_price

		#check if any seller is selling item in this price
		sellers = item.get('sellers')
		filtered_sellers = []
		for seller in sellers:
			item_price = seller.get('price')
			if item_price <= buying_price:
				filtered_sellers.append(seller)

		item['sellers'] = filtered_sellers
		item['buying_price'] = buying_price
		return item

	def _get_jobs_for_item(self, processed_item):
		sellers = processed_item.get('sellers')

		jobs = []
		for seller in sellers:
			jobs.append({
				'item_name': processed_item.get('item_name'),
				'item_price': seller.get('price'),
				'item_quantity': seller.get('quantity'),
				'seller_name': seller.get('name'),
				'seller_location': 'PENDING',
				'selling_price': 'PENDING'
			})

		return jobs