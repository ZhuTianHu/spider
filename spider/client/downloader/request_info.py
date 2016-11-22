#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class RequestInfo(object):

    def __init__(self, url, **kwargs):
        self.url = url
        for key, value in kwargs.iteritems():
            self.__setattr__(key, value)

    def __getattr__(self, key):
        return None

if __name__ == '__main__':
    r = RequestInfo('http://www.baidu.com', task_type='baidu', use_proxy=0)
    print r.url
    print r.task_type
    print r.use_proxy
    print r.noexists
