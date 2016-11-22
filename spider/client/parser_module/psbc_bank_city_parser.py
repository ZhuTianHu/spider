#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import conf_parser
import re


def parse(page, raw_page, url, parse_conf, page_encoding=None, task_db=None):
    tasks, items = conf_parser.parse(page, raw_page, url, parse_conf, page_encoding) 
    new_tasks = []
    for task_type, task_url in tasks:
        if task_type == 'psbc_bank_district':
            try:
                params = re.findall('\((.*)\)', task_url)[0]
                province_id, city_code, district_code = re.findall('(\d+)', params)
                new_tasks.append((task_type, "http://www.psbc.com/portal/main"
                                  "?transName=queryDeptAtm&ProvinceId=%s&CityCode=%s"
                                  "&DistrictCode=%s&intpage=1"
                                  % (province_id, city_code, district_code)))
            except Exception, e:
                print e
                continue
    return new_tasks, items
