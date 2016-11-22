#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import threading
import signal
import tornado
import os
from tornado.options import define, options


"""Start to run client by shell command.

Args:
    client: Choose a client module, default base_client.
    retry: Retry times for crawling.
    log_file_prefix: File path for log.
    log_file_num_backups: Number of backup log file.
    log_file_max_size: Max size per log file.
"""
define("retry", default=1, help="crawl times", type=int)
define("client", default="base_client", help="client module", type=str)

tornado.options.parse_command_line(final=False)
if options.log_file_prefix:
    options.log_file_prefix += "_"+str(os.getpid())
tornado.options.parse_command_line([])

client_module = __import__(options.client)
client = client_module.Client()

params = {
        'retry': options.retry
        }
t = threading.Thread(target = client.start, kwargs=params)

t.start()
signal.signal(signal.SIGINT, client.shutdown)
signal.signal(signal.SIGTERM, client.shutdown)
signal.pause()
t.join()
