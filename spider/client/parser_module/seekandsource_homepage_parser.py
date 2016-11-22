#coding: utf-8
import conf_parser
import requests
import lxml.html

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    new_url = url + '/feedback.aspx'
    tasks = [(u'seekandsource_detail', new_url)]
    items = []
    return tasks, items
