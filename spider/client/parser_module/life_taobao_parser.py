import conf_parser
import urlparse

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, url in tasks:
        if task_type == 'life_taobao_city':
            if not url.startswith('http'):
                continue
            query = urlparse.urlparse(url).query
            new_tasks.append((task_type, 'http://bendi.koubei.com/list.htm?%s' % query))
        else:
            new_tasks.append((task_type, url))
    return new_tasks, items
