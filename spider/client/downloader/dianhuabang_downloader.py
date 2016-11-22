#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import hashlib
import urllib

from downloader.base_downloader import *
import requests

LOG = logging.getLogger(__name__)

def calc_sig(apikey, secret, imei, phone_numbers):
    sig = secret[27:53]

    pos = 6
    sig = sig[:pos] + imei + sig[pos:]

    pos = len(imei) + 13
    sig = sig[:pos] + apikey + sig[pos:]

    pos = len(imei) + 17 + len(apikey)
    sig = sig[:pos] + imei + sig[pos:]

    phones = ""
    for phone in phone_numbers:
        phones += phone
    pos = len(imei)*2 + 21 + len(apikey)
    sig = sig[:pos] + phones + sig[pos:]

    sig += apikey

    sig = calc_sha1(sig)

    sig = sig[7:39]

    return sig

def calc_sha1(str1):
    sha1obj = hashlib.sha1()
    sha1obj.update(str1)
    sha1str = sha1obj.hexdigest()
    return sha1str

class Downloader(BaseDownloader):

    def __init__(self):
        BaseDownloader.__init__(self)

    def download(self, request_info):
        proxies = None
        sess = requests.Session()
        phone_numbers = request_info.data
        apikey = "kq49MtFgDyNwuWtBxeyQqzfJhqOyW92k"
        secret = "d5BaQm0Pi0hK5bgLYyxj2utLGXQb8prcxfYJn97auhorpfdhymvXt2SbUzlk0llrukboftjPm5V3ayq9x3nguwwP0v8Eipsn6TrqqfhqVllgvpWYn9njbYmqgcUfqJcPtAb05sduGz5qggZQa1RphEugceNs6Au7nL4zt"

        if request_info.use_proxy:
            proxy_type = request_info.url[:request_info.url.find(':')]
            proxies = self.get_proxy(proxy_type)

        # set header
        if request_info.platform:
            headers = self.get_default_header(request_info.platform)
        else:
            headers = self.get_default_header(['Android', 'iOS'])

        for i in xrange(self.retry):
            self._wait_for_retry(i)

            sess.cookies = requests.utils.cookiejar_from_dict({
                "auth_id":"5114486bd406cc530550e8e3561102775045e170a79ba1dea3d213410cc1589d"
            })

            apikey = "kq49MtFgDyNwuWtBxeyQqzfJhqOyW92k"
            secret = "d5BaQm0Pi0hK5bgLYyxj2utLGXQb8prcxfYJn97auhorpfdhymvXt2SbUzlk0llrukboftjPm5V3ayq9x3nguwwP0v8Eipsn6TrqqfhqVllgvpWYn9njbYmqgcUfqJcPtAb05sduGz5qggZQa1RphEugceNs6Au7nL4zt"

            imei = ""
            for i in range(0, 15):
                imei += str(random.randint(0,9))

            sig = calc_sig(apikey, secret, imei, phone_numbers)

            original_data = '{"apikey":"%s","auth_id":"5114486bd406cc530550e8e3561102775045e170a79ba1dea3d213410cc1589d","uid":"%s","localtel":"%%2B8615888888888","sig":"%s","calltype":[' % (apikey, imei, sig)

            for i in range(0, len(phone_numbers)):
                original_data += '"%d"' % (random.randint(1,2))
                if i < len(phone_numbers) - 1:
                    original_data += ','

            original_data += '],"tels":['

            for i in range(0, len(phone_numbers)):
                original_data += '"%s"' % phone_numbers[i]
                if i < len(phone_numbers) - 1:
                    original_data += ','

            original_data += ']}'

            post_data = "i=" + urllib.quote(original_data)

            sess.headers["Cookie2"] = "$Version=1"
            sess.headers["Content-Type"] = "application/x-www-form-urlencoded"

            sess.headers["User-Agent"] = "Dalvik/2.1.0 (Linux; U; Android 5.0.2; MI 2S MIUI/5.11.12)"
            sess.headers["Accept-Encoding"] = "gzip"
            sess.headers["Content-Length"] = len(post_data)
            sess.headers["Connection"] = "Keep-Alive"

            try:
                resp = sess.post(request_info.url, data=post_data, proxies=proxies, timeout=self.timeout)
                if not resp or resp.status_code != 200:
                    continue
                p = page_from_resp(resp)
                #p.elapsed = elapsed
                #p.proxy = proxy
                p.req_url = request_info.url
                return p
            except Exception, e:
                LOG.info(str(e))
        return None









