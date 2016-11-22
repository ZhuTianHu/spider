#coding: utf-8
import logging
import sys
import lxml.html
import urllib2
sys.path.append("../../")
import getpage

def get_provid():
    prov_url = "http://www.oppo.com/index.php?q=service/oppostore/p/%E5%8C%97%E4%BA%AC/c//g/1"
    try:
        page_obj = getpage.get(url=prov_url, use_proxy=False, render_js=True)
        page_doc = lxml.html.document_fromstring(page_obj.text)
        prov_ids = []
        for val in page_doc.xpath("//ul[@id='province']//a/text()"):
            prov_ids.append(val)
    except Exception,e:
        logging.error("get prov id failed, msg: %s" %e)
        return [] 
    return prov_ids 

def init_site(site_info):
    url = "http://www.yellowpages.com.tr/includes/showcategories.php?component=show_category_index&search_language=ar&letter=all&start=%d&rand=0.2919477721217565"
    init_urls = list()
    for num in [21*i for i in xrange(32)]:
        init_urls.append(site_info['init_urls'][0] % num)
    return init_urls        
