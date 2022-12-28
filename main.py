# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows,
# actions, and settings.
from datetime import datetime
import json
from urllib.parse import urljoin

import bs4
import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess


class GlassesSpider(scrapy.Spider):
    name = "glasses"
    active_url = ""
    products = []

    # Replace with the actual URL of the page you want to crawl
    start_urls = [
        {"face_shape": "oval",
         "gender": "female",
         "url": "https://www.zennioptical.com/b/glasses-for-oval-face-female?page=100",
         },
        {"face_shape": "oval",
         "gender": "male",
         "url": "https://www.zennioptical.com/b/glasses-for-oval-face-male?page=100",
         },
        {"face_shape": "square",
         "gender": "female",
         "url": "https://www.zennioptical.com/b/glasses-for-square-face-female?page=100",
         },
        {"face_shape": "square",
         "gender": "male",
         "url": "https://www.zennioptical.com/b/glasses-for-square-face-male?page=100",
         },

        {"face_shape": "diamond",
         "gender": "female",
         "url": "https://www.zennioptical.com/b/glasses-for-diamond-face-female?page=100",
         },
        {"face_shape": "diamond",
         "gender": "male",
         "url": "https://www.zennioptical.com/b/glasses-for-diamond-face-male?page=100",
         },

        {"face_shape": "round",
         "gender": "female",
         "url": "https://www.zennioptical.com/b/glasses-for-round-face-female?page=100",
         },
        {"face_shape": "round",
         "gender": "male",
         "url": "https://www.zennioptical.com/b/glasses-for-round-face-male?page=100",
         },

        {"face_shape": "heart",
         "gender": "female",
         "url": "https://www.zennioptical.com/b/glasses-for-heart-face-female?page=100",
         },
        {"face_shape": "heart",
         "gender": "male",
         "url": "https://www.zennioptical.com/b/glasses-for-heart-face-male?page=100",
         },

        {"face_shape": "triangle",
         "gender": "female",
         "url": "https://www.zennioptical.com/b/glasses-for-triangle-face/Gender-Woman/_/N-1341992444?sizeOrder=1234510000&page=100",
         },
        {"face_shape": "triangle",
         "gender": "male",
         "url": "https://www.zennioptical.com/b/glasses-for-triangle-face/Gender-Men/_/N-1341992444?sizeOrder=1234510000&page=100",
         }
    ]

    def start_requests(self):
        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)")
        for i, start_url in enumerate(self.start_urls):
            self.active_url = start_url
            url = start_url["url"]
            yield Request(url, dont_filter=True, meta=start_url)

    @staticmethod
    def close(spider, reason):
        spider.write_2_file()
        closed = getattr(spider, 'closed', None)
        if callable(closed):
            return closed(reason)

    def parse(self, response):
        product_urls = response.css(
            "div#product-tiles-container div.product-item div.item-top div.color-swatch a::attr(data-url)").extract()
        for p in product_urls[0:2]:
            url = urljoin(response.url, p)
            yield scrapy.Request(url, callback=self.parse_product, meta=response.meta)

    def parse_product(self, response):
        bs = bs4.BeautifulSoup(response.text, "html.parser")
        scripts = bs.find_all('script')
        product_sku = response.url.split("skuId=")[1]
        product = json.loads(scripts[20].contents[0].split("pdpProductData=")[1])

        tags = response.xpath("//*[@id='details']/div/div[1]/div[2]/div[2]/ul/li[5]/a/text()").extract()
        tags = [tag.replace('\n', "") for tag in tags]

        glasses_shape = response.xpath("//*[@id='details']/div/div[1]/div[2]/div[2]/ul/li[2]/a/text()").extract()[0]

        product_detail = [d for d in product["skus"] if d['skuId'] == product_sku][0]

        product_detail_dict = {
            "product_name": product["productName"],
            "product_url": response.url,
            "product_desc": product["productDescription"],
            "price_with_cur": product_detail["frmtListPrice"],
            "price_no_cur": product_detail["listPrice"],
            "image_path": product_detail["mediaInfo"]['auxillaryImages'][0]["path"].replace("//",""),
            "face_shape": response.meta["face_shape"],
            "gender": response.meta["gender"],
            "tags": tags,
            "glasses_shape": glasses_shape
        }
        self.products.append(product_detail_dict)
        yield product_detail_dict

    def write_2_file(self):
        time_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        file_name = "products_{}.json".format(time_str)
        with open(file_name, 'w') as f:
            json.dump(self.products, f)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(GlassesSpider)
    process.start()  # the script will block here until the crawling is finished

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
