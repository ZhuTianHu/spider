import conf_parser
import re

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if items:
        introduction_url = url.replace('qt=shopmenu', 'qt=shopdetail')
        tasks.append(('baidu_food_introduction', introduction_url))
    return (tasks, items)

