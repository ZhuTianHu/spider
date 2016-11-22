#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on

import sys
import time
import logging
import json

from tornado.options import options

import client_scheduler
sys.path.append("../")
from task import task_mongo
from task import task_scheduler
from lib import timer


class SpiderMaster(object):
    """Spider master.

    Manage the whole crawler. This module contains scheduler of crawler client
    and decide which task will allocate to client.
    """
    def __init__(self, max_task_size=3000000, read_num=2000000, read_time=60,
                 options=None):
        """Init the master.

        Args:
            max_task_size: Max task size in master. 
            read_num: Max number of task to read into master.
            read_time: Period to read task.
        """
        self.task_obj = task_mongo.Task()
        self.task_scheduler = task_scheduler.TaskScheduler(max_task_size) #最多在内存中保存task的数量
        self.PER_READ_NUM = read_num #每次最多读入TASK的数量
        self.task_obj.clear_status()
        self.last_read_num = 0
        self.read_time = read_time
        self.client_scheduler = client_scheduler.ClientScheduler(
            max_task_num=max_task_size, options=options)
        self.scheduler_timer = timer.Timer(read_time, self.update_scheduler)
        self.reader_timer = timer.Timer(read_time, self.read_task)
        self.reader_timer.start()
        self.scheduler_timer.start()

    def read_task(self):
        """Read task into memory of master."""
        cursor = self.task_obj.find_task()
        add_num = 0
        cur_time = int(time.time())
        while add_num < self.PER_READ_NUM:
            task = self.task_obj.get_task(cursor)
            if not task:
                break
            if task['exec_time'] - 2 * self.read_time > cur_time:
                continue
            ret = self.task_scheduler.put(task['site_name'], task)
            if ret == 1:
                logging.warning("queue full!")
                break
            if ret == 2:
                logging.warning("add queue failed")
                continue
            if ret == 3:
                logging.warning("priority error, not in [1, 16]")
                continue
            self.task_obj.get_by_master(task)
            add_num += 1
        cursor.close()
        self.last_read_num = add_num
        logging.info("read %d tasks" % add_num)

    def get_task(self, ip, pid):
        """Get task from memory"""
        task = self.task_scheduler.get()
        self.client_scheduler.update_client_access_time(ip, pid)
        if not task:
            logging.info(json.dumps({'time': int(time.time()), 'data': 'null'}))
            return 'null'

        try:
            ret_task = {'_id': str(task['_id']),
                    'task_type': task['task_type'], 
                    'site_name': task['site_name'], 
                    'batch_id': task['batch_id'],
                    'country_code': task['country_code'],
                    'url': task['url'],
                    'retry': task['retry'],
                    'uid': str(task['uid']),
                    'depth': task['depth'],
                    'exec_time': task['exec_time']}
            task_str = json.dumps(ret_task, ensure_ascii=False).encode("utf-8")
        except:
            logging.error("seriliaze task failed")
            logging.error(json.dumps({'time': int(time.time()), 'data': 'null'}))
            return "null"
        self.task_obj.get_by_client(task)
        return task_str

    def add_clients(self, number):
        """Add clients by client scheduler"""
        self.client_scheduler.add_clients(number)

    def delete_clients(self, number):
        """Delete clients by client scheduler"""
        self.client_scheduler.delete_clients(number)

    def update_scheduler(self):
        """Update scheduler info"""
        self.client_scheduler.set_total_tasknum(self.task_scheduler.size())
        self.client_scheduler.update_clients()

    def status(self):
        """Get status of crawler"""
        status = {
                "task_scheduler": self.task_scheduler.status(),
                "clients": self.client_scheduler.status(),
                "is_reader_alive": self.reader_timer.is_alive()
                }
        return json.dumps(status, ensure_ascii=False).encode("utf-8")

    def stop(self, *args):
        """Stop spider master"""
        self.reader_timer.stop()
        logging.info("Reader timer exit.")
        self.scheduler_timer.stop()
        logging.info("scheduler timer exit.")
        self.client_scheduler.stop()
        logging.info("Client scheduler exit.")
        self.task_scheduler.stop()
        logging.info("Task scheduler exit.")

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
    master = SpiderMaster() 
    import signal
    signal.signal(signal.SIGINT, master.stop)
    signal.signal(signal.SIGTERM, master.stop)
    signal.pause()
