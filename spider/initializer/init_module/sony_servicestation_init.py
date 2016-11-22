#coding: utf-8
import sys
import lxml.html
import urllib2
sys.path.append("../../")
import getpage

def init_site(site_info):
    init_urls = []
    try:
        page = getpage.get('http://service.sony.com.cn/Maintenance_Station/2518.htm', use_proxy=0)
        page_doc = lxml.html.document_fromstring(page.text)
        for v in page_doc.xpath("//select[@class='default']/option[position()>1]/@value"):
            init_urls.append('http://service.sony.com.cn' + v)
    except Exception, e:
        return [] 
    return init_urls


        
