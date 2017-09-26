import scrapy

class RagialSpider(scrapy.Spider):
    name = 'ragialspider'
    allowed_domains = ["ragi.al"]

    def parse(self, response):
        item_name = response.xpath("//div[@class='mkt_left']/h1/a[2]/text()").extract_first().strip()
        quantity_sold = response.xpath("//table[@id='avgtable']/tr[1]/td[1]/text()").extract_first()
        minimum_price = response.xpath("//table[@id='avgtable']/tr[1]/td[2]/text()").extract_first()
        maximum_price = response.xpath("//table[@id='avgtable']/tr[1]/td[3]/text()").extract_first()
        average_price = response.xpath("//table[@id='avgtable']/tr[1]/td[4]/text()").extract_first()
        std_dev = response.xpath("//table[@id='avgtable']/tr[1]/td[5]/text()").re_first(r'\xb1(\S+)')

        #transform to number
        quantity_sold = self._transformToNumber(quantity_sold)
        minimum_price = self._transformToNumber(minimum_price)
        maximum_price = self._transformToNumber(maximum_price)
        average_price = self._transformToNumber(average_price)
        std_dev = self._transformToNumber(std_dev)

        next_page = response.xpath("//div[@class='mkt_left']/h1/a[2]/@href").extract_first()
        next_page = response.urljoin(next_page)

        yield scrapy.Request(next_page, callback=self.parse_sellers, meta={
            'item': {
                'item_name': item_name,
                'item_url': response.request.url,
                'quantity_sold': quantity_sold,
                'minimum_price': minimum_price,
                'maximum_price': maximum_price,
                'average_price': average_price,
                'std_dev': std_dev,
                'sellers': []
            }
        })

    def parse_sellers(self, response):
        item = response.meta['item']

        next_page = response.xpath("//td[@class='next']/a/@href").extract_first()
        next_page = response.urljoin(next_page)

        more_pages = False

        for seller in response.xpath("//table/tr"):
            name = seller.xpath("td[1]/a/text()").extract_first()
            date = seller.xpath("td[2]/text()").extract_first()
            quantity = seller.xpath("td[3]/text()").re_first(r'(\d+)x')
            price = seller.xpath("td[4]/a/text()").extract_first()
            price = self._transformToNumber(price)

            seller_page = seller.xpath("td[1]/a/@href").extract_first()

            if(date == 'Now'):
                seller = {
                    'name': name,
                    'date': date,
                    'quantity': quantity,
                    'price': price
                }

                # yield scrapy.Request(seller_page, callback=self.parse_seller, meta={'seller': seller})

                item['sellers'].append(seller)
            else:
                more_pages = True

        yield item

        #TODO: make it work if there are more than 13 active vendors
        # yield scrapy.Request(next_page, callback=self.parse_sellers)

    def parse_seller(self, response):
        seller = response.meta['seller']
        seller_location = response.xpath("//div[@id='vend_info']/dl/dt[4]/input/@value").re(r'\/navi (\S+) (\d+)\/(\d+)')
        seller_location = ' '.join(seller_location)

        seller_store_name = response.xpath("//div[@class='mkt_left']/h2/text()").extract_first()

        seller['seller_location'] = seller_location
        seller['seller_store_name'] = seller_store_name

    def _transformToNumber(self, string):
        return int(string.strip().replace(',','').replace('z',''))