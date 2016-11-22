#coding: utf-8
import logging
import json
import sys
import lxml
import lxml.html
sys.path.append("../../")
import getpage

def get_provID():
    province_url = "http://www.yto.net.cn/cn/service/map.htm"
    try:
        pageobj = getpage.get(url=province_url, use_proxy=False)
        page = pageobj.text
    except Exception,e:
        logging.error("download province info failed, msg: %s" %e)
        return False
    try:
        provID_list = list()
        pageroot = lxml.html.document_fromstring(page)
        provID_list = pageroot.xpath("//select[1]//option[position()>1]/@value")
        if type(provID_list) is not list:
            return False
    except Exception,e:
        logging.error("parse province info failed, msg: %s" %e)
        return False
    return provID_list

def init_site(site_info):
    provID_list = get_provID()
    if not provID_list:
        return [] 
    init_urls = list()
    for provID in provID_list:
        init_urls.append(site_info['init_urls'][0] %provID)
    return init_urls 
        
