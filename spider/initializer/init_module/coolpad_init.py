#coding: utf-8
import sys
import lxml.html
sys.path.append("../../")
import getpage

def get_pagenum(site_info):
    try:
        page = getpage.get(site_info['url'], use_proxy=0)
        page_doc = lxml.html.document_fromstring(page.text)
        pagenum = page_doc.xpath("//input[@name='pageInfo.pageTotal']/@value")[0]
    except Exception, e:
        return None
    return pagenum

def init_site(site_info):
    pagenum = get_pagenum(site_info)
    if not pagenum:
        return []
    init_urls = list()
    pagenum = int(pagenum)
    for num in xrange(1, pagenum+1):
        init_urls.append(site_info['init_urls'][0] %num)
    return init_urls 

