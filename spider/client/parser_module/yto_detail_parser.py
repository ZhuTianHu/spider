#coding: utf-8

import json
def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    try:
        page = page[page.find('(')+1:-1]
        page = json.loads(page)
    except Exception,e:
        return (None, None)
    data = page['Data']
    if not data:
        return (None, None)
    data = data[0]
    ret_urls = []
    ret_item = [{
        'company': u'圆通快递',
        'phone': data['QueryTel'].split(';'),
        'fax': data['Fax'],
        'station': data['StationName'],
        'address': data['PathName'],
        'manager': data['HandlerName'],
        'area': data['PathName'].split(','),
        'support_area': [data['ServeArea'].strip('<br/>'), data['SpecialArea'].strip('<br/>')],
        'unsupport_area': data['StopArea'].strip('<br/>'),
        'service': data['EspecialServe'],
        'remark': data['Remark']
        }]
    return (ret_urls, ret_item)

        


    
