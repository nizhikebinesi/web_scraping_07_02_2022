import scrapy
from scrapy.http import TextResponse
from scrapy.loader import ItemLoader

from otparser.items import OtparserItem


class OnlineTradeSpider(scrapy.Spider):
    name = "online_trade"
    # TODO: check allowed_domains
    allowed_domains = ["www.onlinetrade.ru"]
    start_urls = ["https://www.onlinetrade.ru/"]

    def __init__(self, query):
        super().__init__()
        self.search_url = (
            f"https://www.onlinetrade.ru/sitesearch.html" f"?query={query}"
        )

    def parse_item(self, response: TextResponse):
        print("PARSE_ITEM")
        title_xpath = "//h1/text()"
        price_xpath = '//span[@itemprop="price"]/@content'
        small_images_xpath = (
            '//img[contains(@class, "displayedItem__images__thumbImage")]/@src'
        )

        loader = ItemLoader(item=OtparserItem(), response=response)
        # раньше - item['url'] = response.url
        # response.xpath
        loader.add_value("url", response.url)
        loader.add_xpath("title", title_xpath)
        loader.add_xpath("price", price_xpath)
        loader.add_xpath("img_urls", small_images_xpath)
        print()
        yield loader.load_item()

    def parse_search(self, response: TextResponse):
        # items_xpath = '//div[contains(@id, "item_container_")
        # and contains(@id, "__ID")]' \
        #               '//a[contains(@class, "indexGoods__item__name")]' \
        #               '/@href'
        # item_urls = response.xpath(items_xpath).getall()
        items_xpath = (
            '//div[contains(@id, "item_container_") and contains(@id, "__ID")]'
            '//a[contains(@class, "indexGoods__item__name")]'
        )
        item_urls = response.xpath(items_xpath)
        for item_url in item_urls:
            # url = response.urljoin(item_url)
            # print(url)
            yield response.follow(item_url, callback=self.parse_item)
            break

    def parse(self, response, **kwargs):
        # первоначальный запрос был нужен для получения cookies
        yield response.follow(
            self.search_url, callback=self.parse_search, dont_filter=True
        )