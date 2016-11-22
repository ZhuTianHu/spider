#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import logging
import time
import json
import threading
import requests 
import zlib
import socket
import base64

from imp import load_source

import conf_parser
from downloader import default_get_downloader
from downloader import RequestInfo
#from downloader import default_post_downloader
from account import Account
sys.path.append("..")
from task import task_mongo
sys.path.append("../../")


class Client:
    """Client of crawler"""
    def __init__(self):
        self.task_db = task_mongo.Task()
        self.stop_flag = threading.Event()
        self.master_host = self.task_db.get_master_host()
        self.account_obj = Account()
        self.ip = socket.gethostbyname(socket.gethostname())
        self.pid = os.getpid()
        self.cur_path = os.path.abspath('./')

    def parse(self, page_obj, task, task_conf):
        """Parse page by parser.

        This function will choose parser by task_type, if specified parser for 
        task_type exists, it will use it, or use conf_parser.py by default.

        Args:
            page_obj: Page object returned by getpage module.
            task: task object returned by get_task function.
            task_conf: task config object returned by get_task function.

        Returns:
            status: Parse status.
            tasks: Task urls.
            items: Final results.
        """
        if not page_obj:
            return (1, None, None)
        if os.path.isfile("%s/parser_module/%s/%s_parser.py" % (self.cur_path, task['uid'], task['task_type'])):
            try:
                parser = load_source("%s_%s_parser" % (task['uid'], task['task_type']), 
                                     "%s/parser_module/%s/%s_parser.py" 
                                     % (self.cur_path, task['uid'], task['task_type']))
            except Exception, e:
                logging.error("Failed to import %s %s parser, msg: %s"
                              % (task['uid'], task['task_type'], e))
                return (2, None, None)
        else:
            parser = conf_parser
        tasks, items = parser.parse(page_obj.text, page_obj.content,
                                    task['url'], task_conf, 
                                    page_obj.encoding)
        
        if not tasks and not items:
            return (2, None, None)
        return (0, tasks, items)

    def download(self, uid, task_type, url, method, data, use_proxy, render_js, headers, content_length_limit):
        if data:
            try:
                data = json.loads(data)
            except Exception, e:
                print e
                data = data
        request_info = RequestInfo(url, data=data, use_proxy=use_proxy, render_js=render_js, header=headers, content_length_limit=content_length_limit)
        if os.path.isfile("%s/downloader/%s/%s_downloader.py" % (self.cur_path, uid, task_type)):
            try:
                downloader = load_source("%s_%s_downloader" % (uid, task_type),
                                         "%s/downloader/%s/%s_downloader.py"
                                         % (self.cur_path, uid, task_type))
            except Exception, e:
                logging.error("Failed to import %s %s downloader, msg: %s"
                              % (uid, task_type, e))
                return (2, None)
        else:
            if method == 'GET':
                downloader = default_get_downloader
            #if method == 'POST':
            #    downloader = default_post_downloader
        page_obj = downloader.Downloader().download(request_info)
        if not page_obj:
            return (1, None)
        return (0, page_obj)

    def get_task(self):
        """Get task object from master service

        Returns:
            task: Json object of task.
        """
        url = "%s/tasks?ip=%s&pid=%s" % (self.master_host,
                                       self.ip, self.pid)

        try:
            task_str = requests.get(url).text
        except Exception, e:
            logging.error("Failed to get task, msg: %s" % e)
            return None
        if task_str == "null":
            logging.warning("Get no task")
            return None
        logging.info("Get task %s" % task_str)
        try:
            task = json.loads(task_str)
        except Exception, e:
            logging.error("Failed to parse task content, msg: %s" % e)
            return None
        return task

    def retry_task(self, status, task):
        """Retry task.

        When parse task failed, try to retry several times.

        Args:
            status: Parse status, it will decide how many times to retry.
            task: Task to retry.

        Raises:
            KeyError: An error occurred when key field not in task dict.
        """
        if status == 1 and task['retry'] + 1 < 3:
            self.task_db.add_task(task['uid'], task['site_name'], task['task_type'],
                                  task['url'], task['batch_id'],
                                  task['retry']+1,
                                  country_code=task['country_code'],
                                  depth=task.get('depth', 0))
        if status == 2 and task['retry'] + 1 < 3:
            self.task_db.add_task(task['uid'], task['site_name'], task['task_type'],
                                  task['url'], task['batch_id'], 
                                  task['retry']+1,
                                  country_code=task['country_code'],
                                  depth=task.get('depth', 0))

    def add_task(self, status, uid, site_name, country_code, batch_id, parse_tasks, depth=0, max_depth=0):
        """Add tasks parsed by parser.

        Args:
            status: Parse status, parse_tasks will be added 
                when status is 0. 
            site_name: Site name of parse tasks.
            country_code: Country code of site.
            batch_id: Batch id of parse tasks.
            parse_tasks: Tasks parsed by parser.

        Returns:
            An int of task number that has been add to task collection
            successfully.
        """
        if status != 0:
            return
        parse_task_num = 0
        if max_depth > 0 and depth > max_depth:
            return 0
        for task_type, task_url in parse_tasks:
            if self.task_db.task_in_filter(uid, site_name, task_url, task_type,
                                           batch_id) != 0:
                continue
            ret = self.task_db.add_task(uid, site_name, task_type,
                                        task_url, batch_id,
                                        country_code=country_code,
                                        depth=depth)
            if ret == 0:
                parse_task_num += 1
        return parse_task_num

    def _process_task(self, status, task, task_conf):
        """Process task by crawl type of site, if task has been parserd successfully.

        Args:
            status: Parse status.
            task: Task that has been parserd.
            task_conf: Task config.
        """
        if status != 0:
            return 

        crawl_interval = task_conf.get('crawl_interval', 0)
        crawl_type = task_conf.get('crawl_type', 0)
        country_code = task.get('country_code', '')

        if crawl_type == 1:
            self.task_db.add_task(
                task['uid'], task['site_name'], task['task_type'], task['url'],
                task['batch_id'], 0, crawl_interval, country_code, task.get('depth', 0))

        if crawl_type == 2:
            if self.task_db.task_in_filter(task['uid'],
                                           task['site_name'], 
                                           task['url'],
                                           task['task_type'], 
                                           task['batch_id'] + 1) == 0:
                self.task_db.add_task(
                    task['uid'], task['site_name'], task['task_type'], task['url'],
                    task['batch_id'] + 1, country_code=country_code, depth=task.get('depth', 0))

    def update_crawl_statistics(self, status, uid, task_type, site_name, 
                                batch_id, parse_task_num, parse_item_num):
        """Update crawl statistics if parse succeeded.

        Args:
            status: Parse status, update crawl statistics when status is 0.
            task_type: Task type of task.
            site_name: Site name of task.
            batch_id: Batch id of task.
            parse_task_num: Task number add to collection by add_task.
            parse_item_num: Item number parsed by parser.
        """
        if status != 0:
            return
        self.task_db.update_crawl_statistics(
                uid, task_type, site_name, batch_id, parse_task_num, parse_item_num)

    def report_account_status(self, status, account_id):
        """Report account status when parser succeeded or failed.

        Args:
            status: Parse status.
            account_id: Account id returned by get_account.        
        """
        if status == 0:
            self.account_obj.valid_account(account_id)
        if status == 2:
            self.account_obj.invalid_account(account_id)

    def init_record(self, status, country_code, task, parse_tasks, parse_items,
                   page_content=None, page_encoding=None):
        """Construct record by parse results.

        Args:
            status: Parse status.
            country_code: Country code of site.
            task: Task parsed by parser.
            parse_tasks: Tasks returned by parser.
            parse_items: Items returned by parser.
            page_content: Original page content, default None.
            page_encoding: Original page encoding, default None.

        Returns:
            A dict to be add to collection as record. 

        Raises:
            KeyError: An error occurred when key field not in task dict.
        """
        record = {
            'url' : task['url'],
            'task_type' : task['task_type'],
            'site_name': task['site_name'],
            'batch_id' : task['batch_id'],
            'country_code': country_code,
            'status' : status,
            'retry': task['retry']
            }
        if page_content:
            record['zip_content'] = base64.b64encode(zlib.compress(page_content))
        if page_encoding:
            record['page_encoding'] = page_encoding
        if parse_tasks:
            record['tasks'] = parse_tasks
        if parse_items:
            record['items'] = parse_items
        return record

    def start(self, retry=3):
        """Start to run client"""
        if not self.master_host:
            logging.critical("get master host failed")
            return
        logging.info(self.master_host)
        while True:
            if self.stop_flag.is_set():
                break

            task = self.get_task()
            if not task or type(task) is not dict:
                time.sleep(10)
                continue
            
            self.task_db.get_by_client(task)
            logging.info("task was get by client")
            task_conf = self.task_db.get_task_conf(task['uid'], task['task_type'])
            if not task_conf or type(task_conf) is not dict:
                logging.critical("Failed to get task config of %s"
                                 % task['task_type'])
                continue
            task_in_filter = self.task_db.task_in_filter(
                task['uid'], task['site_name'], task['url'], task['task_type'],
                task['batch_id'])
            logging.info("task_in_filter result: %s" % task_in_filter)
            if (task_conf.get('crawl_type', 0) != 1 and 
                task_in_filter != 0):
                # del task if task crawled before and crawl type is not 1
                self.task_db.del_by_client(task['_id'])
                continue
            # parse task_conf
            use_proxy = task_conf.get('use_proxy', False)
            render_js = task_conf.get('render_js', False)
            headers = task_conf.get('headers', {})
            need_login = task_conf.get('need_login', False)
            content_length_limit = task_conf.get('content_length_limit', None)
            if need_login:
                account_id, account_header = self.account_obj.get_account(
                    task['site_name'])
                headers.update(account_header)

            status, page_obj = self.download(task['uid'], task['task_type'], task['url'],
                                             task_conf.get('method', 'GET'), task.get('data', None),
                                             use_proxy=use_proxy, render_js=render_js,
                                             headers=headers,
                                             content_length_limit=content_length_limit)
            if status != 0:
                logging.error("Failed to download page, status: %s, task_type: %s, url: %s, data: %s" 
                              % (status, task['task_type'], task['url'], task.get('data', '')))
                continue
            # parse page
            status, tasks, items = self.parse(
                page_obj, task, task_conf['task_conf'])

            country_code = task.get('country_code', '')
            if status == 0:
                # Process task by crawl type
                # Crawl type:
                #       0: Crawl just once.
                #       1: Repeat crawling in one batch id.
                #       2: Repeat crawling, increasing batch id by itself
                #       3: Don't use filter to process task
                if task_conf.get('crawl_type', 0) == 3:
                    self.task_db.del_by_client(task['_id'])
                else:
                    task_in_filter = self.task_db.add_task_to_filter(
                        task['uid'], task['site_name'], task['url'], task['task_type'],
                        task['batch_id'])
                    if (task_conf.get('crawl_type', 0) != 1 and 
                        task_in_filter != 0):
                        # del task if task crawled before and crawl type is not 1
                        self.task_db.del_by_client(task['_id'])
                        continue
                self._process_task(status, task, task_conf)
                parse_task_num = self.add_task(
                    status, task['uid'], task['site_name'], country_code,task['batch_id'],
                    tasks, task.get('depth', 0) + 1, task_conf.get('max_depth', 0))
                self.update_crawl_statistics(
                    status, task['uid'], task['task_type'], task['site_name'],
                    task['batch_id'], parse_task_num, len(items))
            elif status != 0:
                #self.retry_task(status, task)
                pass

            if need_login:
                self.report_account_status(status, account_id)

            page_content = (page_obj.content if page_obj and page_obj.content
                            else None)
            page_encoding = (page_obj.encoding.lower() if page_obj and page_obj.encoding
                             else None)
            record = self.init_record(status, country_code, task, tasks, items, 
                                      page_content, page_encoding)

            self.task_db.finish_task(task['uid'], task, record)

            time.sleep(1)

    def shutdown(self, *args):
        """Stop client by send stop signal"""
        logging.info("waiting client to shutdown...")
        self.stop_flag.set()
