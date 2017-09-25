import json

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class RagialJobGenerator:

	SPIDER_OUPUT_JSON = 'spider_output.json'

	def runSpider(self):
		process = CrawlerProcess(get_project_settings())
		process.crawl('ragialspider', domain='ragi.al')
		process.start()

	def get_jobs(self):
		self._fetch_spider_data(False)

		# print json.dumps(self.spider_data, indent=4)

		items_processed = []
		for item in self.spider_data:
			items_processed.append(self._process_item(item))

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
			self.runSpider()
		with open(self.SPIDER_OUPUT_JSON) as file:
			self.spider_data = json.load(file)

	def _process_item(self, item):
		#calculate selling price
		average_price = item.get('average_price')
		std_dev = item.get('std_dev')
		buying_price = average_price - std_dev

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

if __name__ == '__main__':
	rjg = RagialJobGenerator()
	jobs = rjg.get_jobs()
	print json.dumps(jobs, indent=4)