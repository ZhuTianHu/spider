import conf_parser
import re

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if tasks:
        new_tasks = []
        for task_type, url in tasks:
            if task_type == 'csc86_list':
                new_tasks.append((task_type, re.sub(',', '', url)))
            else:
                new_tasks.append((task_type, url))
        return (new_tasks, items)
    return (tasks, items)

