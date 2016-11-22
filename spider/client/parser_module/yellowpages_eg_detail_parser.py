import lxml.html
import sys
sys.path.append("../../")
import getpage
import conf_parser

def get_phone(phone_id):
    if not phone_id:
        return []
    url = 'http://www.yellowpages.com.eg/en/get-phones/%s/' % phone_id
    page = getpage.get(url, use_proxy=0)
    page_obj = lxml.html.document_fromstring(page.text)
    phone_doc = page_obj.xpath("//span[@class='detail']/text()")
    phones = []
    for each in phone_doc:
        phones += [v.strip() for v in each.split(',')]
    return phones

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    if items:
        for item in items:
            id = item.get('phone_id', None)
            item['phone'] = get_phone(id)
    return (tasks, items)

