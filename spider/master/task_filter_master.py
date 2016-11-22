#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys
import threading
import logging

from pybloomfilter import BloomFilter

sys.path.append('..')
from conf import bloom_filter_conf


class TaskFilterMaster(object):
    """Bloom filter to filter the duplicated tasks."""
    def __init__(self):
        """Init the bloom filter environment."""
        self.bf_file_path = bloom_filter_conf.bloom_filter_dir
        self.bf_dict = {}
        self.capacity = bloom_filter_conf.default_capacity
        self.error_rate = bloom_filter_conf.error_rate
        self.bf_dict_lock = threading.Lock()
        if not os.path.isdir(self.bf_file_path):
            os.makedirs(self.bf_file_path)

    def init_bloom_filter(self, site_name, capacity):
        """Create a bloom filter with specified site name and capacity."""
        with self.bf_dict_lock:
            try:
                bf = BloomFilter(capacity, self.error_rate, self.bf_file_path + site_name +
                                 '.bf') 
            except Exception, e:
                logging.error('Failed to init bloom filter: %s, msg: %s' % (site_name, e))
                return False
            self.bf_dict[site_name] = bf
            return True

    def add_task_to_filter(self, site_name, task_sign):
        """Try to add task to bloom filter.

        If task has not been crawled before, it will be added into bloom filter.

        Args:
            site_name: Site name of the task.
            task_sign: A string indicates the task to be tested.

        Returns:
            A string indicates whether the task has been crawled. If task has
            been crawled, it can not be added, then returns '1', else '0'.
        """
        with self.bf_dict_lock:
            try:
                if site_name not in self.bf_dict:
                    if os.path.isfile(self.bf_file_path + site_name + '.bf'):
                        self.bf_dict[site_name] = BloomFilter.open(
                            self.bf_file_path + site_name + '.bf')
                    else:
                        self.bf_dict[site_name] = BloomFilter(
                            self.capacity, self.error_rate, self.bf_file_path +
                            site_name + '.bf')
                bf = self.bf_dict[site_name]
                if not bf.add(task_sign):
                    # not crawled
                    return '0'
                else:
                    return '1'
            except Exception, e:
                logging.error("Failed to add filter task %s, msg: %s" 
                              % (task_sign, e))
                return '1'

    def task_in_filter(self, site_name, task_sign):
        """Test whether task has been crawled before.

        Test whether a task has been crawled, this will not add task to bloom
        filter, just test.

        Args:
            site_name: Site name of the task.
            task_sign: A string indicates the task to be tested.

        Returns:
            A string indicates whether the task has been crawled. If task has
            been crawled, it can not be added, then returns '1', else '0'.
        """
        with self.bf_dict_lock:
            try:
                if site_name not in self.bf_dict:
                    if os.path.isfile(self.bf_file_path + site_name + '.bf'):
                        self.bf_dict[site_name] = BloomFilter.open(
                            self.bf_file_path + site_name + '.bf')
                    else:
                        self.bf_dict[site_name] = BloomFilter(
                            self.capacity, self.error_rate, self.bf_file_path +
                            site_name + '.bf')
                bf = self.bf_dict[site_name]
                if task_sign not in bf:
                    # not crawled
                    return '0'
                else:
                    return '1'
            except Exception, e:
                logging.error("Failed to test task %s, msg: %s" 
                              % (task_sign, e))
                return '1'

    def delete_bloom_filter(self, site_name):
        with self.bf_dict_lock:
            try:
                if site_name in self.bf_dict:
                    self.bf_dict[site_name].close()
                    del self.bf_dict[site_name]
            except Exception, e:
                logging.error("Failed close bloom filter %s, msg: %s" 
                              % (site_name, e))
                return False
        try:
            if os.path.isfile(self.bf_file_path + site_name + '.bf'):
                os.remove(self.bf_file_path + site_name + '.bf')
        except Exception, e:
            logging.error("Failed delete bloom filter file %s, msg: %s" 
                          % (self.bf_file_path + site_name + '.bf', e))
            return False
        logging.error("Delete bloom filter %s successfully" % site_name)
        return True


if __name__ == '__main__':
    task_filter = TaskFilterMaster()
    print task_filter.task_in_filter('118118',
                                     '101b3e2c6df97b8d1a7587dc4b276822')
    print task_filter.add_task_to_filter('118118', 
                                         '101b3e2c6df97b8d1a7587dc4b276822')
    print task_filter.task_in_filter('118118',
                                     '101b3e2c6df97b8d1a7587dc4b276822')
    print task_filter.task_in_filter('118118',
                                     '101b3e2c68wwefe')
    print task_filter.task_in_filter('118118',
                                     '101b3e2c68wwefe')


