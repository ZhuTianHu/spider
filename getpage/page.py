#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from time import time
from chardet import detect
from utils import guess_response_encoding as guess_enc

def page_from_resp(resp, content, encoding = None):
    '''
    Create a Page object form a requests.Responce object.
    '''
    enc = encoding or guess_enc(resp.headers, content)
    return Page(
        resp.url,
        content,
        enc,
        resp.headers,
        resp.elapsed,
    )

class Page(object):
    '''
    The :class:`Page <Page>` object, which contains the
    contents of a requested page.
    '''
    def __init__(
        self,
        url,
        content,
        encoding,
        headers = None,
        elapsed = None,
        timestamp = None,
        proxy = None,
        req_url = None):

        super(Page, self).__init__()
        self.url = url
        self.content = content
        self.headers = headers
        self.encoding = encoding
        self.elapsed = elapsed
        self.timestamp = timestamp or time()
        self.proxy = proxy
        self.req_url = req_url

    @property
    def text(self):
        if not self.content:
            return u''
        enc = self.encoding or detect(self.content)['encoding']
        try:
            text = self.content.decode(enc, 'replace')
        except (LookupError, TypeError):
            text = self.content.decode('latin1', 'replace')
        return text

if __name__ == '__main__':
    import requests
    r = requests.get('http://cnbeta.com')
    print page_from_resp(r)
