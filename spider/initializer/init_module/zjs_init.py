#coding: utf-8
import logging
import json
import sys
import urllib
sys.path.append("../../")
import getpage

def get_provID():
    province_url = "http://www.zjs.com.cn/WS_Business/GetPCAData.ashx?province=0&city=0&county=0&companyname=0"
    try:
        pageobj = getpage.get(url=province_url, use_proxy=False)
        page = json.loads(pageobj.text)
    except Exception,e:
        logging.error("download province info failed, msg: %s" %e)
        return False
    provID_list = list()
    for info in page:
        provID_list.append(info['Cname'])
    return provID_list

def init_site(site_info):
    provID_list = get_provID()
    if not provID_list:
        return [] 
    init_urls = list()
    for provID in provID_list:
        init_urls.append(site_info['init_urls'][0] %urllib.quote(provID.encode('gbk')))
    return init_urls 
        
