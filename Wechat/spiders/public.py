# -*- coding: utf-8 -*-
import json
import sys

import scrapy
from urllib.parse import quote
import re
from ..items import WechatItem


class PublicSpider(scrapy.Spider):
    name = 'public'
    allowed_domains = ['weixin.sogou.com', 'mp.weixin.qq.com']
    WeChat_cookie = 'CJb+3KgEElxvV1ZzLTVEM082ckwxYVhzQk5hd2VFTE9Mdnh4T1AtVmhmWC1nQ0FoSThaM2lRa2dxaUVCdzJDSmZkLVczZEE2ZHdKQVl5VWVSdjk1ZFJsLUlLb2lrTmdEQUFBfjDMre/fBTgNQJVO'

    def start_requests(self):
        self.public_name = input('请输入要爬取的公众号：')
        sougou_url = 'https://weixin.sogou.com/weixin?query=' + quote(self.public_name)
        yield scrapy.Request(sougou_url, callback=self.parse)

    def parse(self, response):
        lis = response.css('.news-box .news-list2 li')
        for li in lis:
            a = li.css('.txt-box > .tit > a')
            a_name = ''.join(a.css('::text').getall())
            if a_name == self.public_name:
                url = a.css('::attr(href)').get()
                yield scrapy.Request(url, callback=self.parse_find)

    def parse_find(self, response):
        biz = re.search(r'var biz = "(.*?)"', response.text, re.S).group(1)
        url = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' + biz
        yield scrapy.Request(url, callback=self.parse_public_history, cookies={'wap_sid2': self.WeChat_cookie})

    def parse_public_history(self, response):
        biz = re.search(r'biz=(.*)', response.url, re.S).group(1)
        appmsg_token = re.search(r'appmsg_token = "(.*?)"', response.text, re.S).group(1)
        for i in range(300):
            url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz={}&f=json&offset={}&count=10&appmsg_token={}'.format(
                biz, i * 10, appmsg_token)
            yield scrapy.Request(url, callback=self.parse_json, cookies={'wap_sid2': self.WeChat_cookie})

    def parse_json(self, response):
        res = json.loads(response.text)
        if res['errmsg'] == 'ok':
            content_list = json.loads(res['general_msg_list'])['list']
            if content_list:
                for content in content_list:
                    detail_url = content['app_msg_ext_info']['content_url']
                    yield WechatItem(detail_url=detail_url)
