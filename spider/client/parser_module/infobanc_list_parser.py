#coding: utf-8
import conf_parser
import requests
import lxml.html
import traceback

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    #print 'task', tasks
    #print 'item', items
    #print 'page', page
    while True:
        try:
            page_doc = lxml.html.document_fromstring(page)
            current_page_number = page_doc.xpath("//div[@class='wp-pagenavi']/span[@class='current']/text()") 
            #print 'number', current_page_number
            next_page_number = int(current_page_number[0]) + 1
        except:
            traceback.print_exc()
            return
        try:    
            session = requests.Session()
            post_data = {
                'p':next_page_number
                }
            new_page = session.post('http://suppliers.infobanc.com/directory/edible-oils-oil-seeds-biofuels/S-1119/index.htm', data = post_data)
            new_tasks, new_items = conf_parser.parse(new_page.text, new_page.content, url, parse_conf, page_encoding)
            #print 'new_tasks', new_tasks
            #print 'new_items', new_items
        except:
            #print '--------------------------error----------------'
            traceback.print_exc()
            return
        if not new_items or 'No result found' in new_page.text:
            break
        else:
            page = new_page.text
            tasks += new_tasks
            items += new_items

    return tasks, items
