import scrapy
from TruckCorner.items import listingUrlFieldItem
from fake_headers import Headers



class ListingSpider(scrapy.Spider):
    name = "listing"
    allow_domains = ["truckscorner.com"]

    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate ony Windows platform
        headers=True  # generate misc headers
    )
    urls = "https://www.truckscorner.com/used/1/trucks-1.html"

    def start_requests(self):
        header1 = self.header.generate()
        yield scrapy.Request(self.urls,self.parse,headers=header1)

    def parse(self,response):
        header1 = self.header.generate()
        item   = listingUrlFieldItem()
        text = response.xpath("//div[@class='listing--element  js-classified']")
        for i in text:
            item['title']  = i.xpath("a[@class='link']/div/text()").get('')
            item['category'] = {
                    'cat1_name' : i.xpath("//div[@class='u-bold u-small']/text()").get().strip(),
                    'cat1_id': i.xpath("//div[@class='u-bold u-small']/text()").get().strip(),
                    'cat2_name':'',
                    'cat2_id':'',
                    'cat3_name':'',
                    'cat3_id':''
            }
            item['item_custom_info'] = {
                "desc":''
            }
            item['thumbnail_url'] = i.xpath("div[@class='img']/div/img/@data-src").get('')
            item['item_url'] = "https://www.truckscorner.com"+i.xpath("a[@class='link']/@href").get('')
            buying_format = i.xpath(".//*[@class='maicons maicons-auction']").get('')
            if buying_format == "":
                item['buying_format'] = "sale"
            else:
                item['buying_format'] = "auction"
            yield item
        next = response.xpath("//li[@class='pagination--nav nav-right']/a/@href").get()
        if next is not None:
            next1 = response.urljoin(next)
            yield scrapy.Request(next1,self.parse,headers=header1)
