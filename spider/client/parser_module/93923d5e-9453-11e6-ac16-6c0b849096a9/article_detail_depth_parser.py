#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging

import lxml.html
import lxml.etree
import tldextract

from parser_module.content_extract import list_extract
from parser_module.content_extract import content_extract


def parse(page, raw_page, url, parse_conf, page_encoding=None):
    """Extract list url of page"""
    ret_tasks = []
    ret_items = []

    if not page or not parse_conf:
        return (ret_tasks, ret_items)

    try:
        doc = lxml.html.document_fromstring(page)
        doc.make_links_absolute(url)
    except Exception, e:
        logging.error("Failed to convert html string to dom tree of url %s, "
                      "msg: %s" % (url, e))
        return (ret_tasks, ret_items)
    url_obj = tldextract.extract(url)
    links = [(lxml.etree.tounicode(node,method='text'), node.xpath('@href'))
             for node in doc.xpath('//a')]
    ret_tasks = [('article_detail_depth', y[0].strip()) for x, y in links if
                 list_extract.is_useful_link(x,y) 
                 and y[0].strip() != url
                 and y[0].strip().split("//")[1].split('/')[0] == url.split("//")[1].split('/')[0]
                 and tldextract.extract(y[0]).subdomain == url_obj.subdomain
                 and tldextract.extract(y[0]).domain == url_obj.domain
                 and tldextract.extract(y[0]).suffix == url_obj.suffix]

    # extract content 
    try:
        time, title, content = content_extract.parse(url, page)
    except Exception, e:
        logging.error("Failed to parse page %s, msg: %s" % (url, e))
        return (ret_tasks, ret_items)
    if title or content:
        ret_items.append({
            'title': title, 
            'content': content
        })
    return (ret_tasks, ret_items)

