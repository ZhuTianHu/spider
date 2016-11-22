#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import time
import logging

from imp import load_source
import pymongo

sys.path.append("..")
from conf import mongo_conf
from task import task_mongo
from lib import timer


cli = pymongo.MongoClient(mongo_conf.host, mongo_conf.port)
db = cli[mongo_conf.spider_db]
task = task_mongo.Task()
cur_path = os.path.abspath('./')


def check_site(site_info):
    """Check site info to decide whether to crawl the site

    Not crawl when:
        (1) status is not 1;
        (2) crawl_interval not set in site_info and the site has been crawled
            before;
        (3) crawl_interval is set but the next crawl time not reached;
        (4) batch_id is not set

    """
    if "status" not in site_info or site_info["status"] != 1:
        return False

    if site_info["crawl_time"] == 0:
        return True

    if "crawl_interval" not in site_info:
        return False

    if ("crawl_inerval" in site_info and 
        site_info["crawl_time"] + site_info["crawl_interval"] > time.time()):
        return False

    if "batch_id" not in site_info:
        return False
    return True


def _add_task(site_info):
    """Add task to collection"""
    flag = True
    if 'task_type' not in site_info:
        return False
    for url in site_info.get("init_urls", []):
        if task.task_in_filter(site_info['uid'], site_info['site_name'], url,
                               site_info['task_type'], 
                                  site_info['batch_id']) != 0:
            logging.info("add duplicate task (%s %s %s %d %s)" 
                         % (site_info['uid'], site_info['site_name'], site_info['task_type'], site_info['batch_id'], url))
            continue

        ret = task.add_task(site_info['uid'], site_info['site_name'], site_info['task_type'],
                            url, site_info['batch_id'],
                            country_code=site_info.get('country_code', ''),
                            depth=0)
        if ret == 1:
            flag =  False
            logging.info("add task (%s %s %s %d %s) fail" % (site_info['uid'], site_info['site_name'], site_info['task_type'], site_info['batch_id'], url))
        else:
            logging.info("add task (%s %s %s %d %s) success"
                         % (site_info['uid'], site_info['site_name'], site_info['task_type'], site_info['batch_id'], url))
    return flag


def scan_site():
    """Scan site collection every 300 seconds"""
    cursor = db.site.find({"$query": {}, "$snapshot": True})
    while True:
        site_info = task.get_task(cursor)
        if not site_info:
            break
        if not check_site(site_info):
            #logging.info("no pass")
            continue
        logging.info("Read site: %s" % site_info["name"])
        logging.info("Country_name: %s" % site_info["country_code"])
        init_urls = get_init_urls(site_info)
        if not init_urls:
            continue
        site_info['init_urls'] = init_urls 
        if _add_task(site_info):
            try:
                db.site.update({'_id': site_info['_id']},
                               {'$set':{'crawl_time':int(time.time())}, 
                                '$inc':{'batch_id':1}})
            except Exception, e:
                logging.error("Failed to update site %s, msg: %s" 
                              % (site_info["name"], e))


def get_init_urls(site_info):
    """Get init urls.

    If init module of task type is not specified, use init_module to generate
    init urls, else return init_urls from site config directly.
    """
    if os.path.isfile("%s/init_module/%s/%s_init.py"
                      % (cur_path, site_info['uid'], site_info['task_type'])):
        try:
            init_module = load_source(
                "%s_%s_init" % (site_info['uid'], site_info['task_type']), 
                "%s/init_module/%s/%s_init.py" 
                % (cur_path, site_info['uid'], site_info['task_type']))
        except Exception, e:
            logging.error("Failed to import %s %s init module, msg: %s"
                          % (site_info['uid'], site_info['task_type'], e))
            return []
        return init_module.init_site(site_info)
    else:
        return site_info['init_urls']


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
    t = timer.Timer(300, scan_site)
    t.start()
    import signal
    signal.signal(signal.SIGINT, t.stop)
    signal.signal(signal.SIGTERM, t.stop)
    signal.pause()
