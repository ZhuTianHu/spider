#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import json
from parser_module import conf_parser

sys.path.append("../")
from task import task_mongo

sys.path.append("../../")
import getpage

if len(sys.argv) < 3:
    print "Usage: python %s url task_type" % sys.argv[0]
    exit()

url = sys.argv[1]
task_type = sys.argv[2]

task_obj = task_mongo.Task()

task_conf = task_obj.get_task_conf(task_type)['task_conf']
if not task_conf:
    exit()

print url
page_obj = getpage.get(url, use_proxy=False)
if not page_obj:
    print "get page failed"
    exit()

tasks, items = conf_parser.parse(page_obj.text, url, task_conf, page_obj.encoding)

print "task num: %d" % len(tasks)
for task_type, url in tasks:
    print task_type, url
print "------------------------------------------------------------------------"

print "item num: %d" % len(items)
for item in items:
    item_str = json.dumps(item, ensure_ascii=False).encode("utf-8")
    print item_str
