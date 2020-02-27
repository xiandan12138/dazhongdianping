#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@project: dazhongdianping
@file: dzdp.py.py
@ide: PyCharm
@time: 2020-02-24 18:30:41
@author: Mr.Li
Copyright © 2020—2020 Mr.Li. All rights reserved.
"""

import requests
import re    # re库是对字符串进行解析，而lxml文件可以对xml文件进行解析
from lxml import etree
from fake_useragent import UserAgent
import time    #暂停程序，避免封号
import random    #生成随机时间值

def get_url_list():

    url_list = []
    for i in list(range(72)):  # 我所抓的评论一共72页，尚未完善自动化获取评论页数的代码
        url_list.append('http://www.dianping.com/shop/18335920/review_all/p' + str(i + 1))
    return url_list

def get_css_content(html, headers):
    print('------begin to get css content------')
    css_l = re.search(r'<link rel="stylesheet" type="text/css" href="(//s3plus.sankuai.com.*?.css)">', html)
    css_link = 'http:' + css_l.group(1)
    html_css = requests.get(css_link, headers).text
    return html_css

def get_font_dic(css_content):
    print('------begin to get font dictionary------')
    # 获取svg链接和svg页面的html源码
    svg_l = re.search(r'svgmtsi.*?(//s3plus.sankuai.com.*?svg)\);', css_content)
    svg_link = 'http:' + svg_l.group(1)
    svg_html = requests.get(svg_link).text
    # 解析出字典
    y_list = re.findall('d="M0 (.*?) H600"', svg_html)  # y_list的元素为str
    font_dic = {}
    j = 0    # j为第j行
    font_size = int(re.findall(r'font-size:(.*?)px;fill:#333;}', svg_html)[0])
    for y in y_list:
        font_l = re.findall(r'<textPath xlink:href="#' + str(j + 1) + '" textLength=".*?">(.*?)</textPath>', svg_html)
        font_list = re.findall(r'.{1}', font_l[0])
        for x in range(len(font_list)):    # x为每一行第x个字
            font_dic[str(x * font_size) + ',' + y] = font_list[x]
        j += 1
    return font_dic, y_list

def get_html_full_review(html, css_content, font_dic, y_list):
    font_key_list = re.findall(r'<svgmtsi class="(.*?)"></svgmtsi>', html)
    # print(len(font_key))
    for font_key in font_key_list:
        pos_key = re.findall(r'.' + font_key + '{background:-(.*?).0px -(.*?).0px;}', css_content)
        pos_x = pos_key[0][0]
        pos_y_original = pos_key[0][1]
        for y in y_list:
            if int(pos_y_original) < int(y):
                pos_y = y
                break
        html = html.replace('<svgmtsi class="' + font_key + '"></svgmtsi>', font_dic[pos_x + ',' + pos_y])
    return html

def reviews_output(html_full_review):
    print('------开始提取评论并写入文件------')
    html = etree.HTML(html_full_review)
    reviews_items = html.xpath("//div[@class='reviews-items']/ul/li")
    for i in reviews_items:
        # reviews = i.xpath("./div/div[@class='review-words Hide']")    #定位到目标元素
        # r = reviews[0].xpath('string(.)').strip()    #提取目标元素的文本内容，这两行也可以直接缩写为下面一行
        #r = i.xpath("./div/div[@class='review-words Hide']")[0].xpath('string(.)').strip()
        r = i.xpath("./div/div[@class='review-words Hide']/text()")
        for temp in r:
            with open('reviews.txt', 'a+', encoding='UTF-8') as f:
                f.write(temp)
            f.close()
    print('------写入完成，延迟10-25秒------')
    time.sleep(10 + 15 * random.random())

if __name__ == '__main__':
    url_list = get_url_list()
    n = 0
    # url = 'http://www.dianping.com/shop/18335920/review_all/p1'
    headers = {
        'Cookie': 'cy=4; cye=guangzhou; _lxsdk_cuid=17075fecc2a7d-012d477ae5fa96-4c302879-144000-17075fecc2bc8; _lxsdk=17075fecc2a7d-012d477ae5fa96-4c302879-144000-17075fecc2bc8; _hc.v=15503fd2-0489-9321-e379-d7ee36ab5d46.1582527598; dplet=4c5f24c2aef63c78f63f11f4816303fc; dper=680c7721cb3ab0bdf9606657b6762c9f264d43f65eb63500b751b18dccc47241b64ccdddbf11aa003901ed91959e2e9df4652fb2b0cdced78359723804e207c3fb5aa130aeb12a3b1c7b07f9248f4599bb048547261b38371fa0b9aa264e16e3; ua=dpuser_0196789228; ctu=05b472eca0e87267b3eda97d1073abb4a6b0385ada1685b06c5cf13643fc32d4; s_ViewType=10; aburl=1; __utma=1.1509819458.1582527777.1582527777.1582527777.1; __utmz=1.1582527777.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); ll=7fd06e815b796be3df069dec7836c3df; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=17080d6c36b-703-64f-c78%7C%7C281',
        'host': 'www.dianping.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': UserAgent().random
    }
    res = requests.get(url_list[0], headers=headers)
    # 获取css文件内容
    css_content = get_css_content(res.text, headers)
    # 获取字体字典
    font_dic, y_list = get_font_dic(css_content)
    for url in url_list:
        print('------开始解析第' + str(n + 1) + '个网页------')
        html_full_review = get_html_full_review(res.text, css_content, font_dic, y_list)
        reviews_output(html_full_review)
        n += 1