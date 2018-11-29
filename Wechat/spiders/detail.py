# -*- coding: utf-8 -*-
import re

import scrapy
import redis
from ..items import DetailItem


class DetailSpider(scrapy.Spider):
    name = 'detail'
    allowed_domains = ['mp.weixin.qq.com']

    def start_requests(self):
        red = redis.StrictRedis('localhost', port=6379)
        detail_url_list = red.smembers('wechat:detail_urls')
        for detail_url in detail_url_list:
            yield scrapy.Request(detail_url.decode('utf-8'))

    def parse(self, response):
        title = response.css('#activity-name::text').get().strip()
        head = response.css('#meta_content > span::text').getall()
        head = ''.join(head).strip() if ''.join(head) else ''
        end = response.css('#js_name::text').get().strip()
        author = '{}{}'.format(head, end)
        author = re.sub(r'Original.*?\n.*?\b', '原创：', author)
        date = re.search(r'publish_time = "(.*?)"', response.text, re.S).group(1)
        plist = response.css('div.rich_media_content p')
        content = list()
        pictures = list()
        for p in plist:
            cont = p.xpath('.//text()').getall()
            content.extend(cont)
            img = p.xpath('.//img/@data-src').getall()
            pictures.extend(img)
        content = '.'.join(content)
        yield DetailItem(
            title=title,
            author=author,
            date=date,
            content=content,
            pictures=pictures
        )
