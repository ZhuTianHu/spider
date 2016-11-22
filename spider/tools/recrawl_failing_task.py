#!/usr/bin/env python
# -*- encoding: utf-8 -*=
# Created on

import sys
import os
import datetime
import json
import hashlib
import logging

import argparse
import pymongo

sys.path.append("../")
from task import task_mongo
from conf import mongo_conf


"""This module will recrawl failed task by get failed task from records."""
cli = pymongo.MongoClient(mongo_conf.host, mongo_conf.port)
db = cli[mongo_conf.spider_db]
trash_db = cli[mongo_conf.spider_trash_db]

parser = argparse.ArgumentParser(usage="recrawl failing task")
parser.add_argument("start_time", help="start time of record")
parser.add_argument("end_time", help="end time of record")
parser.add_argument("status", type=int)
parser.add_argument("-t", "--task_type", help="task type to recrawl, support regex task_type", default='')
args = parser.parse_args()

cur_time = args.start_time
task_obj = task_mongo.Task()
if args.status == 1:
    search_option = {'status': 1, 'retry': 499}
elif args.status == 2:
    search_option = {'status': 2, 'retry': {'$gt': 3}}
if args.task_type:
    if args.task_type.startswith('/'):
        search_option['task_type'] = {'$regex': args.task_type.strip('/')}
    else:
        search_option['task_type'] = args.task_type

while cur_time <= args.end_time:
    collection_name = 'record_' + cur_time
    try:
        collection = trash_db[collection_name]
        for record in collection.find(search_option):
            task_type = record['task_type']
            url = record['url']
            batch_id = record['batch_id']
            site_name = task_obj.get_site_name(task_type)
            if not site_name:
                logging.error('get site name of %s failed' % task_type)
                continue
            task_obj.add_task(site_name, task_type, url, batch_id)
    except Exception, e:
        logging.error("get record failed, %s" % e)
        break
    cur_time = datetime.datetime.strftime(
        datetime.datetime.strptime(cur_time, "%Y%m%d") + datetime.timedelta(days=1), "%Y%m%d")
cli.close()
