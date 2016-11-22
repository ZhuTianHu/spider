#coding: utf-8
import conf_parser
import re
import requests

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    mcatId = re.findall("'fch_mcatID':'(.*)','fch_mcatName'", page) 
    mcatName = re.findall("'fch_mcatName':'(.*)','fch_catID'", page)
    catId = re.findall("'fch_catID':'(.*)','fch_searchCityId'", page)
    end = 28
    post_data = { 
            'biz': '', 
            'catId': catId,
            'debug_mod': 0,
            'end': end,
            'mcatId': mcatId,
            'mcatName': mcatName,
            'prod_serv': 'P',
            'rand': 4,
            'searchCity': '', 
            'showkm': ''
            }   
    session = requests.Session()
    while True:
        try:
            post_data['end'] = end 
            new_page = session.post("http://dir.indiamart.com/impcatProductPagination.php", data=post_data)
            new_tasks, new_items = conf_parser.parse(new_page.text, new_page.content, url, parse_conf, page_encoding)
            if not new_items or 'No result found' in new_page.text:
                break
            end += 20
            tasks += new_tasks
            items += new_items
        except Exception, e:
            break
    return tasks, items
