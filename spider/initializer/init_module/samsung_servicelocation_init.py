#coding: utf-8
import sys
import lxml.html
import urllib2
sys.path.append("../../")
import getpage

def get_serviceinfo():
    prov_url = "http://support-cn.samsung.com/support/ServiceLocations.asp"
    try:
        page_obj = getpage.get(url=prov_url, use_proxy=False)
        page_doc = lxml.html.document_fromstring(page_obj.text)
        prov_ids = page_doc.xpath("//ul[@id='ulpro']//a/text()")
        categorys = page_doc.xpath("//ul[@class='product-categories']//label/@value")
    except Exception, e:
        logging.error("get prov id failed, msg: %s" %e)
        return ([], [])
    return (prov_ids, categorys)

def get_cityid(prov_id):
    city_url = "http://support-cn.samsung.com/support/ServiceLocations-ajax.asp?v=%s&act=3" %(urllib2.quote(prov_id.encode('utf-8')))
    try:
        page = getpage.get(url=city_url, use_proxy=False).text
        city_ids = []
        for val in page.split(","):
            start_pos = val.find('"')
            end_pos = val.find('"', start_pos+1)
            city_ids.append(val[start_pos+1:end_pos])
    except Exception, e:
        logging.error("get city id failed, msg: %s" %e)
        return [] 
    return city_ids 

def init_site(site_info):
    prov_ids, categorys = get_serviceinfo()
    init_urls = list()
    try:
        for prov_id in prov_ids:
            for city_id in get_cityid(prov_id):
                for category in categorys:
                    init_urls.append(site_info['init_urls'][0] %(urllib2.quote(prov_id.encode('utf-8')),
                                                                 urllib2.quote(city_id.encode('utf-8')),
                                                                 urllib2.quote(category.encode('utf-8'))))
    except Exception, e:
        return [] 
    return init_urls 

if __name__ == "__main__":
    prov_ids, categorys = get_serviceinfo()
    print prov_ids
    print categorys
    city_ids = get_cityid(prov_ids[0])
    print city_ids
    url = "http://support-cn.samsung.com/support/ServiceLocations.asp?province=%s&city=%s&productlist=%s"
    print url %(urllib2.quote(prov_ids[0].encode('utf-8')),
             urllib2.quote(city_ids[0].encode('utf-8')),
             urllib2.quote(categorys[0].encode('utf-8')))

        
