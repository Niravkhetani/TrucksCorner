import scrapy
from TruckCorner.items import TruckcornerItem
from fake_headers import Headers
import pandas as pd
import ast,re
from scrapinghub import ScrapinghubClient


class DetailSpider(scrapy.Spider):
    name = 'detailSpider'
    urls = "https://www.truckscorner.com/used/1/trucks-1.html"
    allowed_domains = ["truckscorner.com"]
    project_id = 512586

    def __init__(self,collection_name=None, *args, **kwargs):
        print("in inti")
        try:
            super(DetailSpider, self).__init__(*args, **kwargs)
            global current_collection, additional_information, url, listing_urls, category_names, category_ids, thumb_urls, \
                subcategory_names, subcategory_ids, city, state, country, \
                collection_keys, foo_store, titles, make, model, year, serial_no, item_custom_info,\
                item_title, categories, buying_format

            listing_urls = []
            category_names = []
            category_ids = []
            subcategory_names = []
            subcategory_ids = []
            collection_keys = []
            thumb_urls = []
            city = []
            state = []
            country = []
            titles = []
            make = []
            model = []
            year = []
            serial_no = []
            additional_information = []
            current_collection = ''
            categories = []
            buying_format = []


            table = pd.read_csv("TruckCorner/spiders/listing.csv")
            titles = list(table['title'])
            listing_urls = list(table['item_url'])
            thumb_urls = list(table['thumbnail_url'])
            categories = list(table['category'])
            buying_format = list(table['buying_format'])


            apikey = '3b7e1d959149492ab9a71b9aae0fbff4'
            # client = ScrapinghubClient(apikey)
            # project_id = 400514
            # project = client.get_project(project_id)
            # collections = project.collections
            # if not collection_name:
            #     collection_list = collections.list()[-1]
            #     collection_name = collection_list.get('name')
            #     # collection_name = '2_256'
            #     foo_store = collections.get_store(collection_name)
            #     print("MyStore", collection_name)
            # else:
            #     foo_store = collections.get_store(collection_name)
            # current_collection = str(collection_name)
            # print("Getting Items from collection" + str(collection_name))
            # print("Length of collection" + str(foo_store.count()))
            #
            # item_custom_info = []
            #
            # for elem in foo_store.iter():
            #     collection_keys.append(elem['_key'])
            #     listing_urls.append(elem['item_url'])
            #     titles.append(str(elem['title']))
            #     thumb_urls.append(str(elem['thumbnail_url']))
            #     category_names.append(elem['category']['cat1_name'])
            #     category_ids.append(elem['category']['cat1_id'])
            #     subcategory_names.append(elem['category']['cat2_name'])
            #     subcategory_ids.append(elem['category']['cat2_id'])
            #     item_custom_info.append(elem['item_custom_info'])
            #
            # print("Fetched from collection" + str(collection_name))
        except Exception as e:
            print(e)

    def start_requests(self):
        header = Headers(
            browser="chrome",  # Generate only Chrome UA
            os="win",  # Generate ony Windows platform
            headers=True  # generate misc headers
        )
        header1 = ""
        for i in range(1, 10):
            header1 = header.generate()
        print(header1)
        yield scrapy.Request(self.urls, self.parse, headers=header1)

    def parse(self, response):
        try:
            header = Headers(
                browser="chrome",  # Generate only Chrome UA
                os="win",  # Generate ony Windows platform
                headers=True  # generate misc headers
            )
            header1 = ""
            for i in range(1, 10):
                header1 = header.generate()
            print(len(listing_urls))
            for i in range(0, len(listing_urls)):
                yield scrapy.Request(url=listing_urls[i], callback=self.parse_data, meta={
                    'listing_url': listing_urls[i],
                    'thumb_urls':thumb_urls[i],
                    'categories':categories[i],
                    'buying_format':buying_format[i],
                    'titles': titles[i]}, dont_filter=True,headers=header1)
        except Exception as e:
            print(e)

    def parse_data(self, response):
        item = TruckcornerItem()

        item['item_title'] = response.meta['titles']

        item['item_url'] = response.url

        if response.meta['thumb_urls']:
            item['thumbnail_url'] = response.meta['thumb_urls']
        else:
            item['thumbnail_url'] = ''

        data = ast.literal_eval(response.meta['categories'])
        print(data)
        input()
        if categories:
            item['item_main_category'] = data.get('cat1_name')
            item['item_main_category_id'] = data.get('cat1_id')

            item['item_category'] = data.get('cat2_name')
            item['item_source_category_id'] = data.get('cat2_id')

            item['item_sub_category'] = data.get('cat3_name')
            item['item_source_sub_category_id'] = data.get('cat3_id')
        print(response.meta["buying_format"])
        if str(response.meta["buying_format"]) == "nan":
            print("in if ")
            response.meta["buying_format"] = ""
        item['buying_format'] = response.meta["buying_format"]
        item['country'] = response.xpath("//div[@class='u-bold mbs']/a/text()").get('')


        item['vendor_name'] = response.xpath("//p[@class='u-bold h3-like man']/text()").get('').strip()
        item['vendor_url'] = ''

        item['img_url'] = response.xpath("//div[@class='slider--no txtcenter']/img/@src").getall()

        item['source_item_id'] = ''


        lista = []
        for i in response.xpath('//*[@id="viTabs_0_is"]/div/table//text()').extract():
            if i.strip():
                lista.append(i.strip())
        data = response.xpath("//table[@class='table--specs']//tr")
        data_dict = {}
        category1 = data.xpath("td/text()").getall()
        category2 = data.xpath("td[2]//text()").getall()
        cat1 = []
        cat2 = []
        for i in category1:
            cat1.append(i.strip().strip("\n").strip())
        cat1 = list(filter(None, cat1))
        cat1_new = []
        for i in cat1:
            cat1_new.append(re.sub(r':', '', i))
        for i in category2:
            cat2.append(i.strip().strip("\n").strip())
        cat2 = list(filter(None, cat2))
        for key,val in zip(cat1_new,cat2):
            data_dict[key] = val
        try:
            item['model'] = data_dict['Model ']
        except:
            item['model'] = ''
        try:
            new_location = []
            location=response.xpath("//div[@class='u-bold mbs']//text()").getall()
            for i in location:
                new_location.append(i.strip())
            new_location = str(new_location)
            new_location = re.sub(r'[^\w]',' ',new_location)
            item['item_location'] = new_location
        except:
            item['item_location'] = ''
        try:
            price = data_dict['Price excl. taxes ']
            if price:
                item['price'] = price
                item['currency'] = 'USD'
            else:
                item['currency'] = ''
                item['price'] = ''
        except:
            item['currency'] = item['price'] = ''

        item['price_original'] = item['price']

        item['serial_number'] = ''

        try:
            item['make'] = data_dict['Make ']
        except:
            print(data_dict['Make '])
            item['make'] = ''
        try:
            item['year'] = data_dict['Year ']
        except:
            item['year'] = ''

        item['vendor_contact'] = ''
        item['details'] = ''
        # item['extra_fields'] = ''
        item['price_original'] = item['price']
        # foo_store.delete(response.meta['collection_item_key'])
        yield item

    # def get_images(self, response):
    #     gallery = []
    #     images = response.xpath('//*[@id="vi_main_img_fs"]/ul/li//img/@src').extract()
    #     for i in images:
    #         gallery.append(i)
    #     return gallery





