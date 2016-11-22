import re
import conf_parser

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, url in tasks:
        if task_type != 'grotal_detail':
            new_tasks.append((task_type, url))
        else:
            for v in re.findall('javascript:Navigate\("(.*)"\);', url):
                detail_url = "http://www.grotal.com/%s" % v
                new_tasks.append((task_type, detail_url))
    return new_tasks, items
