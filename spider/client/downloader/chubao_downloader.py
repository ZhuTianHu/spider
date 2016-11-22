#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import time

from downloader.base_downloader import *
import requests

LOG = logging.getLogger(__name__)

class Downloader(BaseDownloader):

    def __init__(self):
        BaseDownloader.__init__(self)

    def download(self, request_info):
        proxies = None
        sess = requests.Session()
        for i in xrange(self.retry):
            self._wait_for_retry(i)

            if request_info.use_proxy:
                proxy_type = request_info.url[:request_info.url.find(':')]
                proxies = self.get_proxy(proxy_type)

            # set header
            if request_info.platform:
                headers = self.get_default_header(request_info.platform)
            else:
                headers = self.get_default_header(['Android', 'iOS'])

            post_data = {
                "need_advertisement": "true",
                "need_promotion": "true",
                "need_slots": "true",
                "phone": request_info.data,
                "survey": "false"
            }
            sess.cookies['auth_token'] = 'a253f849-c27f-4de7-bb78-28203ed24bc2'

            try:
                resp = sess.post(request_info.url, json=post_data, proxies=proxies, timeout=self.timeout, headers=headers)
                if not resp or resp.status_code != 200:
                    continue
                p = page_from_resp(resp)
                #p.elapsed = elapsed
                #p.proxy = proxy
                p.req_url = request_info.url
                return p
            except Exception, e:
                import traceback
                print traceback.format_exc()
                LOG.info(str(e))
        return None









