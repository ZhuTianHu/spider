#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on

import sys
import time
import random
import threading
import logging
sys.path.append("../")
from task import task_mongo
from lib import timer


class _TaskCollection(object):
    """A collection of tasks."""
    def __init__(self):
        self.task_list = []
        self.task_size = {}
        self.cur_size = 0

    def size(self):
        """Get size of tasks."""
        return self.cur_size

    def get(self):
        """Get task, return None if empty."""
        if self.cur_size == 0:
            return None

        index = random.randint(0, self.cur_size - 1)
        self.cur_size -= 1
        item = self.task_list[index]
        task_type = item['task_type']
        self.task_size[task_type] -= 1
        if self.task_size[task_type] <= 0:
            del self.task_size[task_type]
        # swap item, as list.pop() is O(1)
        last_item = self.task_list.pop()
        if last_item == item:
            return last_item
        self.task_list[index] = last_item
        return item

    def put(self, item):
        """Add task."""
        task_type = item['task_type']
        if task_type not in self.task_size:
            self.task_size[task_type] = 0
        self.task_size[task_type] += 1
        self.cur_size += 1
        self.task_list.append(item)

    def status(self):
        """Get detail info of the collection."""
        return {'total': self.size(), 'detail': self.task_size}


class _SiteCollection(object):
    """Task collection grouped by site."""
    def __init__(self):
        self.site_dict = {}
        self.cur_size = 0
        self.site_lock = threading.Lock()

    def get(self):
        """Get task, return None if empty."""
        if self.cur_size == 0:
            return None

        with self.site_lock:
            site_name = random.choice(self.site_dict.keys())
            task_collection = self.site_dict[site_name]
            task = task_collection.get()
            self.cur_size -= 1
            if task_collection.size() <= 0:
                del self.site_dict[site_name]
        return task

    def put(self, site_name, task):
        """Add task."""
        with self.site_lock:
            if site_name not in self.site_dict:
                self.site_dict[site_name] = _TaskCollection()
            self.site_dict[site_name].put(task)
            self.cur_size += 1

    def status(self):
        """Get detail info of the collection."""
        ret = {}
        for site_name, task_collection in self.site_dict.iteritems():
            try:
                ret[site_name] = task_collection.status()
            except Exception, e:
                logging.error("Failed to get status of site %s, msg: %s"
                              % (site_name, e))
                continue
        return ret

    def size(self):
        """Get size of tasks."""
        return self.cur_size

    def is_alive(self):
        """Whether if the size is 0. Return 0 if collection is empty, else 1"""
        return 1 if self.cur_size > 0 else 0

class TaskScheduler(object):
    """Task scheduler."""
    def __init__(self, max_size):
        """Init the object.

        Args:
            max_size: Max number of tasks to be stored.
        """
        self.priority = [16,8,4,2,1]
        self.priority_collection_dict = {
                1:  _SiteCollection(),
                2:  _SiteCollection(),
                4:  _SiteCollection(),
                8:  _SiteCollection(),
                16: _SiteCollection()
                }
        self.max_size = max_size
        self.cur_size = 0
        self.size_lock = threading.Lock()
        self.task_obj = task_mongo.Task()
        self.priority_dict = self._get_priority_dict()
        self.priority_read_timer = timer.Timer(600, self._get_priority_dict)
        self.priority_read_timer.start()

    def _get_priority_dict(self):
        """Get priority dict, update it regularly in case the priority has been
        updated."""
        priority_dict = {}
        if not self.task_obj:
            priority_dict = {}
        else:
            priority_dict = self.task_obj.get_all_priority()
        return priority_dict

    def _random_priority(self):
        """Get a random priority to choose one site collection."""
        collection_status = 0
        for priority, site_collection in self.priority_collection_dict.iteritems():
            collection_status += priority * site_collection.is_alive()
        if collection_status == 0:
            return 0
        sel_val = random.randint(1, collection_status)
        ret_priority = 1
        while True:
            sel_val -= ret_priority & collection_status
            if sel_val <= 0:
                break
            ret_priority <<= 1
        return ret_priority

    def get_priority(self):
        """ Get task, return the highest priority task collection"""
        for priority in self.priority:
            if priority_collection_dict[priority].is_alive():
                return priority 
            else:
                continue
        return

    def get(self):
        """Get task, return None if failed."""
        priority = self.get_priority()
        if not priority:
            return None
        site_collection = self.priority_collection_dict[priority]
        task = site_collection.get()
        if not task:
            return None
        with self.size_lock:
            self.cur_size -= 1
        logging.info(self.cur_size)
        return task

    def put(self, site_name, task):
        """Put task."""
        # Check the size of tasks, in case overflow
        with self.size_lock:
            if self.cur_size >= self.max_size:
                return 1
            else:
                self.cur_size += 1

        if site_name not in self.priority_dict:
            site_priority = self.task_obj.get_site_priority(site_name) 
            if not site_priority:
                return 2
            self.priority_dict.update(site_priority)
        priority = self.priority_dict[site_name]
        if priority < 1 or priority > 16 or priority & (priority - 1) != 0:
            # Priority of site is wrong
            return 3

        site_collection = self.priority_collection_dict[priority]
        site_collection.put(site_name, task)
        return 0

    def size(self):
        """Get size of tasks."""
        return self.cur_size

    def status(self):
        """Get detail info of the scheduler."""
        ret = {
                'size': self.cur_size,
                'data': []
                } 
        for priority, site_collection in self.priority_collection_dict.iteritems():
            ret['data'].append({
                'priority': priority,
                'size': site_collection.status()
                })
        return ret

    def stop(self):
        """Stop priority read timer."""
        self.priority_read_timer.stop()


if __name__ == '__main__':
    task_scheduler = TaskScheduler(1000)
    for i in range(3):
        print task_scheduler.put(u'article_detail_depth_paar', {'task_type': 'test_task%s' % i})
    import signal
    signal.signal(signal.SIGINT, task_scheduler.stop)
    signal.signal(signal.SIGTERM, task_scheduler.stop)
    #task_scheduler.stop()

