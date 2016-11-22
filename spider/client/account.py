#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import logging
import json
import requests


class Account:
    """Account for login"""

    def __init__(self):
        self.account_host_addr = 'http://10.136.122.157:9999'

    def get_account(self, site_name):
        """Get account from account service.
        
        Get account from account service, account service is a http service
        which offers accounts for the site.

        Args:
            site_name: A string of site name that need to login.

        Returns:
            Tuple which contains account id and account http header.
        """
        if not site_name:
            return None, None
        req_url = self.account_host_addr + '/get?site_name=' + site_name
        for i in range(3):
            try:
                time.sleep(3)
                resp = requests.get(req_url, timeout=3)
                if resp.status_code != 200:
                    logging.error('Failed to get account header. '
                                  'Response status code %d.' % resp.status_code)
                    continue
                if not resp.text:
                    logging.info('Failed to get valid account header')
                    continue
                else:
                    account_header = json.loads(resp.text)
                    break
            except requests.exceptions.ConnectionError as e:
                logging.critical("Failed to connect to address %s, msg: %s"
                                 % (req_url, e))
                return None, None
            except requests.exceptions.ConnectTimeout as e:
                logging.error("Connect to address %s timeout"
                              % req_url)
                return None, None
        try:
            return account_header['id'], account_header['headers']
        except KeyError as e:
            logging.error("Get invalid account info from %s, msg: %s"
                          % (req_url, e))
            return None, None

    def valid_account(self, id):
        """Report account to be valid.

        Args:
            id: A string get by function get_account, which indicates 
                the account to be report valid.
        """
        req_url = self.account_host_addr + '/report'
        data = {'id': id, 'status': 'valid'}
        try:
            requests.post(req_url, data)
        except requests.exceptions.ConnectionError as e:
            logging.critical("Failed to connect to address %s, msg: %s"
                             % (req_url, e))
            return
        except requests.exceptions.ConnectTimeout as e:
            logging.error("Connect to address %s timeout"
                          % req_url)
            return

    def invalid_account(self, id):
        """Report account to be invalid.

        Args:
            id: A string get by function get_account, which indicates 
                the account to be report invalid.
        """
        req_url = self.account_host_addr + '/report'
        data = {'id': id, 'status': 'invalid'}
        try:
            requests.post(req_url, data)
        except requests.exceptions.ConnectionError as e:
            logging.critical("Failed to connect to address %s, msg: %s"
                             % (req_url, e))
            return
        except requests.exceptions.ConnectTimeout as e:
            logging.error("Connect to address %s timeout"
                          % req_url)
            return
