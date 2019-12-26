# coding:utf-8
from scrapy_redis.spiders import RedisCrawlSpider
import redis
import json
import copy
import requests


class WeixinSpider(RedisCrawlSpider):
    name = 'weixin'
    allowed_domains = ['weixin.com']
    redis_key = 'weixin:start_urls'
    start_urls = ['https://i.weread.qq.com/book/articles?bookId=MP_WXS_2390582660&count=10']  # 肖磊看市
    headers = {}
    # 需要添加对401代码的处理，不然如果accessToken过期并不会进行处理
    handle_httpstatus_list = [401]

    def __init__(self):
        self.r = redis.Redis('localhost', port=6379)
        self.data = {}
        for url in self.start_urls:
            self.r.lpush(self.redis_key, url)
        self.get_headers()

    def get_headers(self):
        """获取微信阅读的请求headers, 需要通过手机抓包获取到data里的参数，然后通过调用此方法获取accessToken和vid, 并添加到headers里"""
        url = 'https://i.weread.qq.com/login'
        data = '{"deviceId":"3339194867987932323232323","inBackground":0,"kickType":1,"refCgi":"https://i.weread.qq.com/mp/cover?bookId=MP_WXS_3548542976","refreshToken":"onb3MjkNtSPdfSJlDdp5cCVIJYWw@kbFVENIIQris7ZvDvT9XlQAA","trackId":"8618730000000","wxToken":0}'
        html = requests.post(url=url, data=data, timeout=5).json()
        self.headers['accessToken'] = html['accessToken']
        self.headers['vid'] = html['vid']

    def parse(self, response):
        """若出现401表示accessToken过期，所以调用get_headers方法重新获取"""
        try:
            if response.status == 401:
                self.get_headers
            else:
                res = json.loads(response.body)['reviews']
                for article in res[:1]:
                    article = article['review']
                    title = article['mpInfo']['title']
                    cover_url = article['mpInfo']['pic_url']
                    author = article['mpInfo']['mp_name']
                    dis = article['mpInfo']['content']
                    article_data = copy.deepcopy(self.data)
                    article_data['cover_url'] = cover_url
                    article_data['title'] = title
                    article_data['description'] = dis
                    article_data['author'] = author
                    yield article_data
        except Exception as e:
            print(e)
        finally:
            self.r.lpush(self.redis_key, response.url)
