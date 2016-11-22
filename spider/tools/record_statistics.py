#!/usr/bin/env python
# -*= encoding: utf-8 -*-
# Created on

import sys
import time
import logging
import argparse
import pymongo

sys.path.append("../")
from conf import mongo_conf


"""This module will count the satus of crawler everyday.""" 
def get_count(record_name, status):
    selected_db = db if status == 0 else trash_db
    # status=0
    match = {'status': status}
    if status == 1:
        match['retry'] = 499
    if status == 2:
        match['retry'] = {'$gt': 3}
    try:
        data = selected_db[record_name].aggregate([
                 {'$match': match},
                 {'$group': {'_id': '$task_type','count': {'$sum': 1}}}])
    except Exception, e:
        logging.error('Failed to get record count that status=%s, msg: %s' % (status, e))
        return {}
    return {'status': status, 'data': data['result']}

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--date", help="date to statistics, fromat: %%Y%%m%%d")
args = parser.parse_args()

cli = pymongo.MongoClient(mongo_conf.host, mongo_conf.port)
db = cli[mongo_conf.spider_db]
trash_db = cli[mongo_conf.spider_trash_db]

if args.date:
    date = args.date
else:
    date = time.strftime("%Y%m%d", time.localtime(time.time() - 24 * 60 * 60))

res = [] 
record_name = 'record_%s' % date
for status in range(3):
    ret = get_count(record_name, status)
    if not ret:
        continue
    res.append(ret)
if res:
    db.daily_statistics.insert({'date': date, 'items': res})

cli.close()



