import conf_parser

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    tasks_zone = []
    for (name, val) in tasks:
        if name == 'anjuke_list':
            return (tasks, items)
        elif name == 'anjuke_zone':
            tasks_zone.append((name, val))
    list_parse_conf = task_db.get_task_conf('anjuke_list')['task_conf']
    tasks, items = conf_parser.parse(page, raw_page, url, list_parse_conf, page_encoding)
    return tasks + tasks_zone, items
