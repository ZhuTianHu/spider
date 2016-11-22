#coding: utf-8
import conf_parser
import requests
import lxml.html
import traceback

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    session = requests.Session()
    for item in items:
        phone_div_info = item.get('phone_div', None)
        #print 'phone_div_info', phone_div_info
        phone_list = []
        if not phone_div_info:
            continue
        try:
            phone_div_id = phone_div_info.split('id')[1]        
            #print 'phone_div_id', phone_div_id
            phone_url = 'http://www.eworldtradefair.com/ajax.php'
            post_data = {
                    'action' : 'viewcompanyphones',
                    'campsid' : phone_div_id
                    }
            page = session.post(phone_url, data = post_data)
            #print 'page', page.text
            page_doc = lxml.html.document_fromstring(page.text)
            phone = page_doc.xpath("//strong/following-sibling::text()")
            #print phone
            if not phone:
                continue
            if type(phone) is list:
                for i in phone:
                    i = i.strip()
                    phone_list += [i]
            else:
                phone_list.append(phone.strip())
        except:
            traceback.print_exc()
            continue
        item['phone'] = phone_list
    return tasks, items
