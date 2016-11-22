#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
import lxml.html
import urllib2
import re


"""Parse page by task config.

The function call sequence is:
    parse -> _parse_dom -> _parse_dom_rule

    parse: Parse the page.

    _parse_dom: Parse the DOM node.

    _parse_dom_rule: Parse the DOM node by a rule of task config.
"""


def _parse_regex(string, pattern):
    """Parse a strig by regex."""
    ret = []
    try:
        ret += re.findall(pattern, string)
    except:
        return []
    return ret


def _urlencode(uri, page_encoding):
    """Encode uri in case of character which is not ascii encoding"""
    ret = ''
    for t_char in uri:
        if ord(t_char) < 128:
            ret += t_char.encode(page_encoding)
        else:
            ret += urllib2.quote(t_char.encode(page_encoding))
    return ret 


def _parse_dom_rule(dom_node, conf_rule):
    """Parse the DOM node by a rule of task config.

    Args:
        dom_node: DOM node to be parsed.
        conf_rule: Rule of task config.

    Returns:
        A list of url or item or DOM node parsed by the config rule.
    """
    try:
        xpath_ret = dom_node.xpath(conf_rule["xpath"])
    except:
        return []
    if type(xpath_ret) is not list:
        x = [xpath_ret]
    else:
        x = xpath_ret
    ret = []

    for val in x:
        if conf_rule["type"] == "dom" and type(val) is lxml.html.HtmlElement:
            ret.append(val)
        else:
            if type(val) is lxml.etree._ElementStringResult:
                t_val = str(val).strip()
            elif type(val) is lxml.etree._ElementUnicodeResult:
                t_val = unicode(val).strip()
            else:
                continue
            if not t_val:
                continue
            ret.append(t_val)
    return ret


def _parse_dom(dom_node, dom_conf, source=''):
    """Parse the DOM node.

    Args:
        dom_node: DOM node to be parsed.
        dom_conf: List of rules for the DOM node which is from task config.

    Returns:
        A tuple contains DOM nodes, urls and items.
    """

    ret_item = {}
    ret_urls = []
    ret_doms = []
    for conf_rule in dom_conf:
        vals = _parse_dom_rule(dom_node, conf_rule)
        if not vals:
            continue
        if conf_rule["type"] in  ["string", "html"] and "regex" in conf_rule and  conf_rule["regex"]:
            val_reg = []
            for v in vals:
                val_reg += _parse_regex(v, conf_rule["regex"])
            vals = val_reg
        if conf_rule["type"] == "url":
            if "regex" in conf_rule and conf_rule["regex"]:
                vals = [v for v in vals if re.match(conf_rule["regex"], v) != None]
        name = conf_rule["name"]
        if conf_rule["type"] == "dom":
            for val in vals:
                ret_doms.append((name, val, ret_item))
        if conf_rule["type"] == "url":
            for val in vals:
                ret_urls.append((name, val))
        if conf_rule["type"] == "string" or conf_rule["type"] == "html":
            if conf_rule["is_list"]:
                if name in ret_item:
                    ret_item[name] += vals
                else:
                    ret_item[name] = vals
            else:
                ret_item[name] = vals[0] if len(vals) == 1 else vals
    return (ret_doms, ret_urls, ret_item)


def parse(page, raw_page, url, parse_conf, page_encoding=None, source=''):
    """Parse the page.

    Args:
        page: Page get by getpage with unicode encoding.
        raw_page: Raw page get by getpage with original encoding.
        url: Url of the page.
        parse_conf: Task config of task which is used to parse page.
        page_encoding: Page encoding get by getpage.

    Returns:
        A tuple contains urls and items parsed from the page.
    """
    # List of dom node.
    dom_list = []
    # list of tuple (task_type, url) as tasks parsed by parser.
    ret_urls = []
    # list of dict contains items as results parsed by parser.
    ret_items = {}

    if not page or not parse_conf:
        return (ret_urls, ret_items)

    # Convert html string to dom tree
    try:
        root = lxml.html.document_fromstring(page)
        root.make_links_absolute(url)
    except Exception, e:
        logging.error("Failed to convert html string to dom tree "
                      "of url %s, msg: %s" % (url, e))
        return (ret_urls, ret_items)

    # Init dom list with root node
    dom_list.append(("root", root, ret_items))

    # Parse every dom node in dom list
    while True:
        try:
            dom_name, dom_node, parent_items = dom_list.pop(0)
        except IndexError:
            break
        if dom_name not in parse_conf:
            continue
        
        dom_conf = parse_conf[dom_name]
        parse_dom_list, url_list, item = _parse_dom(dom_node, dom_conf, source)
        dom_list += parse_dom_list
        
        ret_urls += url_list
        if dom_name not in parent_items:
            parent_items[dom_name] = item
        else:
            if type(parent_items[dom_name]) is dict:
                parent_items[dom_name] = [parent_items[dom_name], item]
            elif type(parent_items[dom_name]) is list:
                parent_items[dom_name].append(item)

    if ret_items and ret_items['root'] and type(ret_items['root']) is dict:
        ret_items = [ret_items['root']]
    else:
        ret_items = []
    if not page_encoding:
        return (ret_urls, ret_items)

    # encoding url in case that url contains character not ascii.
    for i, (task_type, url) in enumerate(ret_urls):
        if type(url) is unicode:
            ret_urls[i] = (task_type, _urlencode(url, page_encoding))
    return (ret_urls, ret_items)
