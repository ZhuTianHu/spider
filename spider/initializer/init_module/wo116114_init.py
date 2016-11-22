#coding: utf-8
import logging
import sys
import lxml.html
sys.path.append("../../")
import getpage

def get_cityid():
    city_url = "http://www.wo116114.com/"
    try:
        page_obj = getpage.get(url=city_url, use_proxy=False, render_js=True)
        page_doc = lxml.html.document_fromstring(page_obj.text)
        city_ids = []
        for val in page_doc.xpath("//div[@class='pro_nr02']//ul/li/a/@onclick"):
            id = val[val.find('\'')+1 : val.find(',')-1]
            city_ids.append(val[val.find('\'')+1 : val.find(',')-1])
    except Exception,e:
        logging.error("get city id failed, msg: %s" %e)
        return [] 
    return city_ids 

def init_site(site_info):
    city_ids = get_cityid()
    if not city_ids:
        return [] 
    init_urls = list()
    for id in city_ids:
        init_urls.append(site_info['init_urls'][0] %id)
    return init_urls 
        
