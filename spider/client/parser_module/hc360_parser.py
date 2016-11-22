import conf_parser
import urlparse

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, url in tasks:
        new_tasks.append((task_type, url))
        if task_type == 'hc360_category':
            url_parts = list(urlparse.urlparse(url))
            if not url[4]:
                new_tasks.append((task_type, url+'?af=1'))
                new_tasks.append((task_type, url+'?af=2'))
            else:
                new_tasks.append((task_type, url+'&af=1'))
                new_tasks.append((task_type, url+'&af=2'))
    return new_tasks, items
