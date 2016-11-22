import conf_parser

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if not tasks:
        return (tasks, items)
    new_tasks = []
    task_detail_url = "http://www.zjs.com.cn/WS_Business/GetPCAData.ashx?PCC=%s"
    import urlparse
    for task_type, url in tasks:
        if task_type == "zjs_detail":
            try:
                parse_res = urlparse.urlparse(url)
                parse_qs = urlparse.parse_qs(parse_res.query, True)
                new_url = task_detail_url %(parse_qs['areaid'][0])
            except exception:
                logging.error('parse url failed, url: %s' %url)
                continue
            new_tasks.append((task_type, new_url))
    return (new_tasks, items)
