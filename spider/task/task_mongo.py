#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on

import sys
import time
import logging
import hashlib
import json
import urlparse
import requests
import random
import pymongo
from bson.objectid import ObjectId
from bson import json_util

import task_filter
sys.path.append("../")
from conf import mongo_conf


class Task(object):
    """Task management.
    Deal with task through mongodb.
    """
    def __init__(self):
        """Init task object."""
        self.cli = pymongo.MongoClient(mongo_conf.host, mongo_conf.port)
        self.spider_db = self.cli[mongo_conf.spider_db]
        # if status==1 or 2, add record in temporary db, 
        # in order to delete the whole db when no space left
        self.spider_trash_db = self.cli[mongo_conf.spider_trash_db]
        self.load_system_config()
        self.task_filter = task_filter.TaskFilter(self.get_master_host())
        self.record_server_host = self.get_record_server_host()
        self.port_list = ["9001", "9002", "9003", "9004"]
    def load_system_config(self):
        """Load system config from mongodb."""
        cursor = self.spider_db.conf.find()
        self.system_config = next(cursor, None)
        cursor.close()

    def get_master_host(self):
        """Get master host address from system config in mongodb."""
        if "master_host" in self.system_config:
            return self.system_config["master_host"]
        else:
            return None

    def get_record_server_host(self):
        if "record_server_host" in self.system_config:
            return self.system_config["record_server_host"]
        else:
            return None

    def find_task(self):
        """Get available tasks whose status is 0.
        
        Returns:
            An instance of cursor corresponding to this query.
        """
        return self.spider_db.task.find({'status' : 0})

    def get_task(self, cursor):
        """Get one task by iterate cursor.

        Args:
            cursor: An instance of cursor corresponding the query returned by pymongo.

        Returns:
            An single document indicates the task or None if no matching
            document is found.
        """
        try:
            task = next(cursor, None)
            return task
        except Exception, e:
            logging.error("Failed to read task, msg: %s" % e)
            return None

    def add_task(self, uid, site_name, task_type, url, batch_id, retry=0,
                 crawl_interval=0, country_code='', depth=0):
        """Insert task to mongodb, this will not check whether task has been
           crawled before, .

        Insert task into mongodb for crawler.
        
        Args:
            site_name: A string indicates site name of the task.
            task_type: A string indicates task type of the task.
            url: A string indicates the url of the task.
            batch_id: An integer indicates the batch id.
            retry: An integer indicates the number of retry times.
            crawl_interval: Time interval between crawl.
            country_code: Country code of url.

        Returns:
            status: An integer indicates the status of add task.
                    0: Add success.
                    1: Failed, the task has been crawled before.
                    2: Failed, can not insert task into mongodb as some reason.
        """
        if not url.startswith('http'):
            return 1
        cur_time = int(time.time())

        exec_time = cur_time + (2 ** (retry % 5) - 1) * 30 + crawl_interval 
        port = ramdom.sample(self.port_list, 1)
        task = {
                "url": url,
                "uid": uid,
                'site_name': site_name,
                "task_type": task_type,
                "batch_id": batch_id,
                "country_code": country_code,
                "status": 0,
                "status_time": cur_time,
                "create_time": cur_time,
                "retry": retry,
                "exec_time": exec_time,
                "port" : port
                }
        if depth >= 0:
            task['depth'] = depth
        try:
            self.spider_db.task.insert(task)
        except Exception, e:
            logging.error("Failed to add task (%s %d %s), msg: %s" 
                          % (task, batch_id, url, e))
            return 1
        return 0

    def get_by_master(self, task):
        """Task was get by master, change the status of the task in case that it may
        be crawled again.

        Args:
            task: Document of task from mongodb.

        Returns:
            A bool variable indicates whether change the status success, return
            True if success, else False.
        """
        try:
            task_id = (task['_id'] if type(task['_id']) is ObjectId else
                       ObjectId(task['_id']))
            self.spider_db.task.update(
                {'_id': task_id}, 
                {'$set': {'status': 1, 'status_time': int(time.time())}})
            return True
        except Exception, e:
            logging.error("Failed to update task status when get task by "
                          "master, msg: %s" % e)
            return False

    def get_by_client(self, task):
        """Task was get by client, change the status.

        Args:
            task: Document of task from mongodb.

        Returns:
            A bool variable indicates whether change the status success, return
            True if success, else False.
        """
        try:
            task_id = (task['_id'] if type(task['_id']) is ObjectId else
                       ObjectId(task['_id']))
            self.spider_db.task.update({'_id': task_id}, {'$set': {'status': 2, 'status_time': int(time.time())}})
            return True
        except Exception, e:
            logging.error("Failed to update task status when get task by "
                          "client, msg: %s" % e)
            return False
    
    def get_task_conf(self, uid, task_type):
        """Get task config.
        
        Args:
            task_type: A string of task type.

        Returns:
            A single document of task config.
        """
        try:
            cursor = self.spider_db.task_conf.find({'uid': uid, 'task_type': task_type})
            ret = next(cursor, None)
            cursor.close()
            return ret
        except Exception,e:
            logging.error("Failed to get task config, msg: %s" % e)
            return None

    def add_record(self, uid, record):
        """Add record.
        
        Args:
            record: A json object indicates the result parsed by spider.
        """
        status = record.get('status', 0)
        record_date = time.strftime("%Y%m%d", time.localtime())
        if status == 0:
            record_str = json.dumps({'uid': uid, 'content': json.dumps(record, ensure_ascii=False)}, ensure_ascii=False).encode('utf-8')
            for i in xrange(3):
                try:
                    resp = requests.post(self.record_server_host + '/records', data=record_str, timeout=10)
                    if resp.status_code == 200:
                        break
                except Exception, e:
                    logging.error("Failed to save record: %s" % record_str)
                    continue
        else:
            self.spider_trash_db['record_' + record_date].insert(record)

    def add_task_to_filter(self, uid, site_name, url, task_type, batch_id):
        """Try to add task to bloom filter when task was parsed successfully.

        Returns:
            An int variable indicates whether the task has been parsed before.
            0: Task has not been parsed before successfully.
            1: Task has been parsed before successuflly.
            2: Failed to test task by bloom filter.
        """
        try:
            task_sign = (hashlib.md5(url + task_type + 
                         str(batch_id))).hexdigest()
            if not self.task_filter.add_task_to_filter(uid, site_name, task_sign):
                return 1
        except Exception, e:
            logging.error("Failed to add task %s to bloom filter, msg: %s"
                          % (url, e))
            return 2
        return 0

    def task_in_filter(self, uid, site_name, url, task_type, batch_id):
        """Check whether task has been parsed before successfully,this will not
        add task to bloom filter.

        Returns:
            An int variable indicates whether the task has been parsed before.
            0: Task has not been parsed before successfully.
            1: Task has been parsed before successuflly.
            2: Failed to test task by bloom filter.
        """
        try:
            task_sign = (hashlib.md5(url + task_type + 
                         str(batch_id))).hexdigest()
            if self.task_filter.task_in_filter(uid, site_name, task_sign):
                return 1
        except Exception, e:
            logging.error("Failed to add task %s to bloom filter, msg: %s"
                          % (url, e))
            return 2
        return 0

    def finish_task(self, uid, task, record):
        """The task has been crawled, delete it from task collection, and store 
        the result.
        
        Args:
            task: Document of the task.
            record: Json object of record to be inserted.
        """
        try:
            logging.info("Finish task, %s" % record['url'])
            self.add_record(uid, record)
        except Exception, e:
            logging.error("insert task record failed: %s" %e)
            return
        self.del_by_client(task['_id'])

    def get_all_priority(self):
        """Get priority dict of all sites.

        Return:
            A dict indicates priority of each site. Return an empty dict if
            failed to get priorities.
        """
        ret = {}
        try:
            for site_info in self.spider_db.site.find({'status': 1}):
                if 'priority' not in site_info:
                    priority = 1
                else:
                    priority = site_info['priority'] 
                ret[site_info['task_type']] = priority
        except:
            return {}
        return ret

    def get_site_priority(self, site_name):
        """Get priority dict of specified site.

        Args:
            A string of site name.

        Return:
            A dict indicates priority of the site. Return an empty dict if
            failed to get priority.
        """
        if not site_name:
            return {} 
        ret = {}
        try:
            cursor = self.spider_db.site.find({'status': 1, 
                                               'site_name': site_name})
            site_info = next(cursor)
            if 'priority' not in site_info:
                priority = 1
            else:
                priority = site_info['priority'] 
            ret[site_info['site_name']] = priority
        except:
            return {}
        return ret
    
    def get_site_name(self, task_type):
        """Get site name of specified task type
        
        Args:
            A string of task type.

        Returns:
            A string of site name of the task type. Return None if Failed to get
            site name.
        """
        try:
            site_name = self.spider_db.task_conf.find_one({'task_type': task_type}, {'site_name': 1}).get('site_name', None)
        except:
            return None
        return site_name

    def del_by_client(self, task_id):
        """Delete task by task id.

        Args:
            task_id: A string of task id

        Returns:
            False if failed to delete task, else return True.
        """
        try:
            self.spider_db.task.remove({'_id': ObjectId(task_id)})
        except Exception,e:
            logging.error("Failed to remove task, msg: %s" % e)
            return False
        return True

    def update_crawl_statistics(self, uid, task_type, site_name, 
                                batch_id, tasknum=0, itemnum=0):
        """Update number of tasks and items.

        After parsed one task successfully, it may generate several tasks and
        items, update the number of tasks and items.
        
        Args:
            task_type: A string of task type.
            site_name: A string of site name.
            batch_id: An integer of batch id.
            tasknum: An integer indicates the number of tasks.
            itemnum: An integer indicates the number of items.

        Returns:
            False if failed to update, else True.
        """
        try:
            if not tasknum and not itemnum:
                return True
            date = time.strftime("%Y%m%d", time.localtime())    
            update_data = {}
            if tasknum:
                update_data["tasks.%s" % date] = tasknum
            if itemnum:
                update_data["items.%s" % date] = itemnum
            self.spider_db.crawl_statistics.update(
                    {'uid': uid,
                 'task_type': task_type, 
                 'batch_id': batch_id, 
                 'site_name': site_name},
                {'$inc': update_data},
                upsert=True, multi=False)
        except Exception, e:
            return False
        return True

    def close_cursor(self, cursor):
        """Close cursor of find_task"""
        cursor.close()

    def clear_status(self):
        """Clear status of tasks.

        When restart the master, set the satus of tasks that were read into
        master to 0.
        """
        self.spider_db.task.update(
            {'status': 1}, 
            {'$set': {'status': 0, 'status_time': int(time.time())}},
            multi=True)

    def __del__(self):
        self.cli.close()
