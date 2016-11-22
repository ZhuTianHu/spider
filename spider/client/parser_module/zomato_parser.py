import conf_parser

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, url in tasks:
        if task_type == "zomato_list":
            new_tasks.append((task_type, "%s/restaurants" % url))
        else:
            new_tasks.append((task_type, url))
    return (new_tasks, items)
