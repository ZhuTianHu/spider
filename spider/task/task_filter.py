#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
import time
import logging


class TaskFilter(object):
    """Task filter for client.
    
    This module can be used to test whether a task has been crawled.
    """
    def __init__(self, master_host):
        self.master_host = master_host
        self.task_filter_path = self.master_host + '/task_filter/tasks'
        self.session = requests.Session()

    def add_task_to_filter(self, uid, site_name, task_sign):
        """Add task to filter.

        Try to add task sign to bloom filter. Test whether a task has been 
        crawled, if not, task will be added into the bloom filter.

        Args:
            uid: user id
            site_name: Site name of the task.
            task_sign: A string indicates the task to be tested.

        Returns:
            A bool variable indicates whether the task has been crawled. If task
            has been crawled, it can not be added, then returns False, else
            True.
        """
        try:
            #req_url = (self.task_filter_path + '?uid=' + uid + '&site_name=' + site_name +
            #          '&key=' + task_sign) 
            resp = self.session.post(self.task_filter_path, data={'site_name': site_name, 'task_sign': task_sign})
            if resp.text == '1':
                return False
            else:
                return True
        except Exception, e:
            logging.error("Failed to add filter task %s, msg: %s"
                          % (task_sign, e))
            return False 

    def task_in_filter(self, uid, site_name, task_sign):
        """Test whether task has been crawled by bloom filter.

        This will not add task sign into bloom filter, only test 
        when task has been crawled befroe.

        Args:
            site_name: Site name of the task.
            task_sign: A string indicates the task to be tested.

        Returns:
            A bool variable indicates whether the task has been crawled. If task
            has been crawled, return True, else return False.
        """
        try:
            req_url = (self.task_filter_path + '?uid=' + uid + '&site_name=' + site_name +
                       '&task_sign=' + task_sign) 
            resp = self.session.get(req_url)
            if resp.text == '1':
                return True 
            else:
                return False
        except Exception, e:
            logging.error("Failed to check filter task %s, msg: %s"
                          % (task_sign, e))
            return False 
