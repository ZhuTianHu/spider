import json

def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    page_obj = json.loads(page)
    data = page_obj.get('theatre', {}).get('data', [])
    if not data:
        return [], []
    items = []
    for v in data:
        fix_phone = v.get('phone', [])
        mobile = v.get('mobile', [])
        fix_phone = [fix_phone] if type(fix_phone) is not list else fix_phone
        mobile = [mobile] if type(mobile) is not list else mobile 
        phone = fix_phone + mobile 
        items.append({
            'title': v.get('theatre_name', ''),
            'address': v.get('address', {}).get('address', ''),
            'landmark': v.get('address', {}).get('landmark', ''),
            'latitude': v.get('lat', ''),
            'longitude': v.get('lng', ''),
            'phone': phone, 
            'email': v.get('email', ''),
            'homepage': v.get('website', ''),
            'city': v.get('address', {}).get('city_name', ''),
            'locality': v.get('address', {}).get('locality_name', ''),
            'zone': v.get('address', {}).get('zone_name', '')
            })
    return [], items
