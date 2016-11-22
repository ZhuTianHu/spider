#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
import time

from traceback import format_exc
import requests
from requests.exceptions import *
from downloader.base_downloader import *
from request_info import RequestInfo

LOG = logging.getLogger(__name__)

class Downloader(BaseDownloader):

    def __init__(self):
        BaseDownloader.__init__(self)

    def _get_page_requests(self, request_info):
        proxies = None
        for i in xrange(self.retry):
            self._wait_for_retry(i)
            # set proxy
            if request_info.use_proxy:
                proxy_type = request_info.url[:request_info.url.find(':')]
                proxies = get_proxy(proxy_type)

            # set header
            if request_info.platform:
                headers = self.get_default_header(request_info.platform)
            else:
                headers = self.get_default_header(['Windows', 'Mac'])

            if request_info.headers:
                if not self.headers:
                    self.headers = request_info.headers
                else:
                    self.headers.update(request_info.headers)
            try:
                start_ts = time.time()
                resp = requests.get(request_info.url, proxies=proxies, headers=headers, timeout=self.timeout)
                if not resp and proxies:
                    LOG.warning('Proxy failed while getting page %s. Proxies: %s' % (request_info.url, proxies))
                    report_proxy_status(proxies, False)
                elif resp and proxies:
                    report_proxy_status(proxies, True)
                status = resp.status_code / 100
                if status == 4:
                    LOG.info('Page not found or request error (%d) while getting page %s.' % (resp.status_code, request_info.url))
                    LOG.info('Time elapsed: %gs. Returning nothing.' % (time.time() - start_ts))
                    continue
                elif status == 5:
                    LOG.info('Server error (%d) while getting page %s.' % (resp.status_code, request_info.url))
                    LOG.info('Time elapsed: %gs. Returning nothing.' % (time.time() - start_ts))
                    continue
                elif status != 2:
                    LOG.info('Got response with status code %d while getting page %s.' % (resp.status_code, request_info.url))
                    continue

                elapsed = time.time() - start_ts
                LOG.info('Successfully got page %s in %gs.' % (request_info.url, elapsed))
                p = page_from_resp(resp)
                p.elapsed = elapsed
                p.proxy = proxies
                p.req_url = request_info.url
                return p
            except RequestException, e:
                LOG.info(str(e))
            except Exception, e:
                LOG.critical('Unexpected exceptions encountered.')
                LOG.critical(str(e))
                LOG.debug(format_exc())
        return None


    def _get_page_phantomjs(self, request_info):
        proxy = None
        proxies = None
        for i in xrange(self.retry):
            self._wait_for_retry(i)
            if request_info.use_proxy:
                proxy_type = request_info.url[:request_info.url.find(':')]
                proxies = get_proxy(proxy_type)
                for k, v in proxies:
                    proxy = v[v.rfind('/') + 1:]
                    break
            LOG.info('Trying to get page %s via PhantomJS, proxy %s.' % (request_info.url, proxy or 'N/A'))
            start_ts = time.time()
            import os
            jspath = os.path.join(os.path.dirname(__file__), 'get.js')
            content = check_output(['phantomjs', '--proxy='+proxy, jspath, request_info.url])
            elapsed = time.time() - start_ts

            if content:
                LOG.info('Successfully got page %s in %gs.' % (request_info.url, elapsed))
                if proxy:
                    report_proxy_status(proxies, True)
            else:
                LOG.warning('Failed to get page %s in %gs, yet we can\'t know what happened.' % (request_info.url, elapsed))
                if proxy:
                    report_proxy_status(proxies, False)
                continue

            enc = guess_content_encoding(content)
            p = Page(request_info.url, content, enc)
            p.elapsed = elapsed
            p.proxy = proxies
            return p
        return None

    def download(self, request_info):
        if request_info.render_js:
            return self._get_page_phantomjs(request_info)
        else:
            return self._get_page_requests(request_info)
