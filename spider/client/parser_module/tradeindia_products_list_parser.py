#coding: utf-8
import conf_parser
import requests
import lxml.html

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    session = requests.Session()
    for item in items:
        phone_url = item.get('phone_url', None)
        if not phone_url:
            continue
        try:
            phone_url = "http://products.tradeindia.com" + phone_url.split("'")[1]
            page = session.get(phone_url)
            page_doc = lxml.html.document_fromstring(page.text)
            phone_list = item.get('phone', [])
            for key in ['Mobile', 'Phone', 'Fax']:
                phone = page_doc.xpath("//tr[contains(td/strong/text(), '%s')]/td[3]/text()" % key)
                if not phone:
                    continue
                if type(phone) is list:
                    phone_list += phone
                else:
                    phone_list.append(phone)
        except:
            continue
        item['phone'] = phone_list
    return tasks, items
