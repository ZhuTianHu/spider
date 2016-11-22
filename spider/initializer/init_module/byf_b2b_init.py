#coding: utf-8
import logging
import sys
import lxml.html
sys.path.append("../../")
import getpage

def get_provid():
    url = "http://www.byf.com/b2b/list.aspx?p=017000"
    try:
        page_obj = getpage.get(url=url, use_proxy=False, render_js=True)
        page_doc = lxml.html.document_fromstring(page_obj.text)
        prov_ids = []
        for val in page_doc.xpath("//select[@id='ddlProvince']/option/@value"):
            if val:
                prov_ids.append(val)
    except Exception,e:
        logging.error("get prov id failed, msg: %s" %e)
        return [] 
    return prov_ids 

def init_site(site_info):
    prov_ids = get_provid()
    if not prov_ids:
        return [] 
    init_urls = list()
    for id in prov_ids:
        init_urls.append(site_info['init_urls'][0] %id)
    return init_urls 
        
