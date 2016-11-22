#coding: utf-8
import sys
import lxml.html
import urllib2
sys.path.append("../../")
import getpage

def init_site(site_info):
    #prov_url = 'http://support-cn.samsung.com/StoreLocation/data/js/zh-cn_region'
    prov_ids = range(10, 41)
    init_urls = list()
    for prov in prov_ids:
        init_urls.append(site_info['init_urls'][0] %prov)
    return init_urls 
 
if __name__ == "__main__":
    site_info = {'init_urls': ['http://support-cn.samsung.com/StoreLocation/store/index_default?type=2&productType=&province=%s']}
    print init_site(site_info)
