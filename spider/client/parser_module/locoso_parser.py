import conf_parser

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if tasks:
        return (tasks, items)

    list_parse_conf = task_db.get_task_conf('locoso_list')['task_conf']
    tasks, items = conf_parser.parse(page, raw_page, url, list_parse_conf, page_encoding)
    return tasks, items
