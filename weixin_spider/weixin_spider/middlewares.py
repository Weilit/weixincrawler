#!usr/bin/env
# -*-coding:utf-8 -*-
import logging
from spiders.spider_tools import mytools
from scrapy.contrib.spidermiddleware.httperror import HttpErrorMiddleware

logger = logging.getLogger(__name__)


class UserAgentmiddleware(object):

    def process_request(self, request, spider):
        """需要重新设置headers的爬虫列表"""
        if spider.name == 'weixin':
            headers = spider.headers
            request.headers['accessToken'] = headers['accessToken']
            request.headers['vid'] = headers['vid']
        else:
            request.headers['User-Agent'] = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.119 Chrome/64.0.3282.119 Safari/537.36']


class Httpstatus(HttpErrorMiddleware):
    """响应码判断中间件,如果HTTP响应码非200,则自动添加初始爬取的URL到队列，防止爬虫空跑"""

    def process_spider_exception(self, response, exception, spider):

        if response.status != 200:
            logger.info(
                "Ignoring response %(response)r: HTTP status code is not handled or not allowed and push url into redis",
                {'response': response}, extra={'spider': spider},
            )
            mytools.lpushUrlIntoRedisWith(spider.redis_key, response.url)
