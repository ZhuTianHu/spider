#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks = []
    items = []
    if not page:
        return tasks, items
    try:
        dst_dict = {}
        json_obj = json.loads(page)
        
        replace_dict = {
            u"crank": u"骚扰电话",
            u"fraud": u"诈骗电话",
            u"house agent": u"房产中介",
            u"promote sales": u"业务推销",
            u"express": u"快递外卖"
        }

        if 'res' in json_obj:
            info_list = json_obj["res"]
            for info in info_list:
                phone_number = ""
                phone_mark = ""
                if info.has_key("phone"):
                    phone_number = info["phone"]

                if info.has_key("shop_name"):
                    phone_mark = info["shop_name"]
                elif info.has_key("incoming_shop_name"):
                    phone_mark = info["incoming_shop_name"]
                elif info.has_key("incoming_shop_info"):
                    phone_mark = info["incoming_shop_info"]
                elif info.has_key("incoming_classify_type"):
                    phone_mark = info["incoming_classify_type"]
                elif info.has_key("classify_type"):
                    phone_mark = info["classify_type"]

                if phone_mark in replace_dict:
                    dst_dict[phone_number] = replace_dict[phone_mark]
                else:
                    dst_dict[phone_number] = phone_mark
        items.append(dst_dict)
    except Exception, e:
        pass
    return tasks, items
