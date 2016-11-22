#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import requests
import random

from utils import *
from traceback import format_exc
from page import page_from_resp, Page
from proxy import get_proxy, report_proxy_status
from request_info import RequestInfo


class BaseDownloader(object):

    def __init__(self):
        self.retry = 3
        self.timeout = 60
        self.proxy = None

    def _wait_for_retry(self, retry):
        time.sleep(random.randint(2 ** retry, 2 ** (retry + 1)))

    def get_default_header(self, platforms=None):
        '''
        Get headers of corresponding platform.

        Args:
            platform: List of platform, must be one of ["Linux", "Mac", "Windows", "Android", "iOS"].

        Returns:
            headers: Map of headers.
        '''
        if not platforms:
            return None
        platform = random.choice(platforms)
        return req_headers(platforms)

    def get_proxy(self, proxy_type):
        ret = {}
        if 'http' in proxy_type: 
            proxy = get_proxy()
            if proxy:
                ret['http'] = "http://" + proxy
        if 'https' in proxy_type: 
            proxy = get_proxy()
            if proxy:
                ret['https'] = "https://" + proxy
        return ret

    def report_proxy(self, proxies, status):
        for k, v in proxies:
            proxy = v[v.rfind('/') + 1:]
            print proxy
            report_proxy_status(proxy, status)

    def download(self, request_info):
        raise NotImplementedError
    

