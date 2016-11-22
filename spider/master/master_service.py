#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 

import sys
import signal
import json

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.log
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.options import define
from tornado.options import options

import master
import task_filter_master
sys.path.append('..')
from conf import log_conf


sys.path.append("../client")
import test_parser

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 5


def shutdown():
    """Shut down master service"""
    tornado.log.app_log.info("stop server...")
    http_server.stop()
    spider_master.stop()

    tornado.log.app_log.info("server will stop in %d seconds" % MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()

    import time
    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
 
    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
    stop_loop()


def sig_handler(sig, frame):
    """
    graceful shutdown tornado web server
    
    reference:
    https://gist.github.com/mywaiting/4643396
    """

    tornado.log.app_log.warning('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


class TaskHandler(tornado.web.RequestHandler):
    def get(self):
        """Get task from master

        Args:
            ip: Client ip to get the task.
            pid: Client pid to get the task.
        """
        ip = self.get_argument('ip')
        pid = self.get_argument('pid')
        task_str = spider_master.get_task(ip, pid)
        self.write(task_str)


class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        """Get staus of crawler"""
        self.write(spider_master.status())


class ClientHandler(tornado.web.RequestHandler):
    def post(self):
        """Add clients manually.

        Args:
            num: Number of clients to add
        """
        client_num = int(self.get_body_argument('num', 1))
        spider_master.add_clients(client_num)

    def delete(self):
        """Delete clients manually.

        Args:
            num: Number of clients to delete.
        """
        client_num = int(self.get_body_argument('num', 1))
        spider_master.delete_clients(client_num)


class TaskFilterTaskHandler(tornado.web.RequestHandler):
    def get(self):
        """Test whether task has been crawled.

        Args:
            site_name: Site name of task.
            task_sign: A string indicates the task.

        Returns:
            A string indicates whether the task has been crawled. If crawled
            , returns '1', else '0'.
        """
        site_name = self.get_argument('site_name')
        task_sign = self.get_argument('task_sign')
        task_crawled = task_filter.task_in_filter(site_name, task_sign)
        self.write(task_crawled)

    def post(self):
        """Add task to bloom filter if task has not been crawled before.

        Args:
            site_name: Site name of task.
            task_sign: A string indicates the task.

        Returns:
            A string indicates whether the task has been crawled. If crawled
            , returns '1', else '0'.
        """
        site_name = self.get_body_argument('site_name')
        task_sign = self.get_body_argument('task_sign')
        task_crawled = task_filter.add_task_to_filter(site_name, task_sign)
        self.write(task_crawled)


class TaskFilterBloomFilterHandler(tornado.web.RequestHandler):
    def post(self):
        """Add a bloom filter manually.

        Args:
            site_name: Site name of task.
            capacity: Size of bloom filter.
        """
        site_name = self.get_body_argument('site_name')
        capacity = int(self.get_body_argument('capacity'))
        task_filter.init_bloom_filter(site_name, capacity)


    def delete(self):
        """Delete a bloom filter manually.

        Args:
            site_name: Site name of task.
        """
        site_name = self.get_argument('site_name')
        task_filter.delete_bloom_filter(site_name)


class TestParserHandler(tornado.web.RequestHandler):
    """Call test parser by webui.

    Args:
        url: url to be tested.
        task_type: initial task type.
        client: client module to use, default base_client.
        test_recurse: whether to test recursively.
    """
    executor = ThreadPoolExecutor(max_workers=5)

    @run_on_executor
    def test_parser_async(self, options, recursive=False):
        if recursive:
            res = test_parser.test_parser_recursively(options)
        else:
            res = test_parser.test_parser(options)
        res = {'data': res}
        return res

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        try:
            args = json.loads(self.request.body)
            url = args.get('url')
            task_type = args.get('task_type')
            client = args.get('client', 'base_client')
            test_recursive = args.get('test_recurse', 1)
            options = {
                'task_type': task_type,
                'url': url,
                'client': client,
            }
            res = yield self.test_parser_async(test_recursive, options)
            self.write(res)
            self.finish()
        except:
            self.write({'data': []})
            self.finish()

define("port", default=8899, help="server port", type=int)
define("max_task_size", default=3000000, help="the max size of tasks to be"
       " stored in master", type=int)
define("read_num", default=2000000, help="the number of task loading from database", type=int)
define("read_time", default=60, help="reading interval", type=int)
define("client_log_file_prefix", default='', help="log file prefix for client", type=str)
define("max_client_num", default=600,help="the max num of client", type=int)
tornado.options.parse_command_line()

spider_master = master.SpiderMaster(max_task_size=options.max_task_size,
        read_num=options.read_num, read_time=options.read_time, options=options)

task_filter = task_filter_master.TaskFilterMaster()
application = tornado.web.Application([
    (r"/tasks", TaskHandler),
    (r"/status", StatusHandler),
    (r"/test_parser", TestParserHandler),
    (r"/clients", ClientHandler),
    (r"/task_filter/tasks", TaskFilterTaskHandler),
    (r"/task_filter/bloom_filters", TaskFilterBloomFilterHandler)])

http_server =tornado.httpserver.HTTPServer(application)
http_server.listen(options.port)

signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

tornado.ioloop.IOLoop.instance().start()
tornado.log.app_log.info("Exit...")

