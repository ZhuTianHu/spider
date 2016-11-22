#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import json
from parser_module import conf_parser


"""Example of conf_parser

Read configuration of parse_conf.example, then parse test.html.
"""
parse_conf = json.load(open("parse_conf.example"))
url = "http://www.locoso.com/cate/-all"
page = open("test.html").read()

urls, items = conf_parser.parse(page, url, parse_conf)
print "urls: "
for task_type, url in urls:
    print task_type, url

print "\nitems:"
for item in items:
    print json.dumps(item, ensure_ascii=False).encode("utf-8")
