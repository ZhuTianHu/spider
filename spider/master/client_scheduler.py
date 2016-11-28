#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on

import os
import sys
import time
import logging
import random
import threading
import subprocess
import copy

from tornado.options import options

sys.path.append("..")
from conf import ip_list
from conf import log_conf
from lib import timer


class ClientScheduler(object):
    """Client scheduler.

    This module will adjust the number of clients automatically, and delete the
    client which may be dead according to the last access time.
    """
    def __init__(self, max_task_num, options,
                 client_expired_time=1200):
        """Create client scheduler.

        Args:
            max_task_num: Max task number of tasks.
            options: options contains client path and log parameters.
            max_client_num: Max client number.
            client_expired_time: Expired time in seconds, used to decide whether
                the client is dead.
        """
        self.cur_path = '/search/article_spider/spider'
        self.client_expired_time = client_expired_time 
        self.client_check_period = 300 
        self.max_task_num = max_task_num
        self.max_client_num = options.max_client_num
        self.cur_client_num = 0
        self.client_dict = {}
        self.task_num_list = []
        self.client_dict_lock = threading.Lock()
        self.client_check_timer = timer.Timer(self.client_check_period,
                                              self._check_client_alive)
        self.client_check_timer.start()
        self._init_client_info()

    def _get_free_mem(self, ip):
        """Get free memory of machine

        Args:
            ip: ip to get free memory.

        Returns:
            An integer of free memory in MB, return 0 if can not get the free
            memory.
        """
        free_mem = 0
        try:
            child = subprocess.Popen(
                ["ssh", "-o BatchMode=yes", "-o ConnectTimeout=10", ip, "free -m|awk 'NR==3 {print $4}'"], 
                stdout=subprocess.PIPE)
            child.wait()
            free_mem = float(child.stdout.read().strip())
        except Exception, e:
            logging.info("Failed to get free mem of %s, %s" % (ip, e))
            return 0
        return free_mem
    
    def _get_total_mem(self, ip):
        """ Get total memory of machine
        Args:
            ip: ip to get free memory
        Returns:
            An integer of free memory in MB, return 1 if can not get the free memory.
        """
        total_mem = 1
        try:
            child = subprocess.Popen(
                    ["ssh", "-o BatchMode=yes", "-o ConnectTimeout=10", ip, "free -m|awk 'NR==2 {print $2}'"], 
                    stdout=subprocess.PIPE)
            child.wait()
            total_mem = float(child.stdout.read().strip())
        except Exception, e:
            logging.info("Failed to get total mem of %s, %s" % (ip, e))
        return total_mem

    def _init_client_info(self):
        """Init client info"""
        client_dict = {}
        for ip in ip_list.ip_list:
            free_mem = self._get_free_mem(ip)
            client_dict[ip] = {
                'free_mem': self._get_free_mem(ip), 
                'total_mem': self._get_total_mem(ip), 
                'clients': {} 
            }
        with self.client_dict_lock:
            self.client_dict = client_dict

    def _check_client_alive(self):
        """Find the dead clients, and kill them."""
        logging.info('Start to check client alive process, cur_time: %s'
                     % int(time.time()))
        with self.client_dict_lock:
            client_dict = copy.deepcopy(self.client_dict)
        try:
            for ip, machine_info in client_dict.iteritems():
                for pid, access_time in machine_info['clients'].iteritems():
                    if access_time + self.client_expired_time > int(time.time()):
                        continue
                    with self.client_dict_lock:
                        try:
                            logging.info("Try to delete client %s:%s" % (ip,
                                         pid))
                            del self.client_dict[ip]['clients'][pid]
                        except KeyError as e:
                            logging.error("Client %s:%s not in client dict, "
                                          "may be deleted by others." 
                                          % (ip, pid))
                            continue
                        self.cur_client_num -= 1
                    self._delete_client_by_pid(ip, pid)
        except Exception, e:
            logging.error("Failed to check client alive, msg: %s" % e)

    # def _get_machine_ip(self):
    #     """Get a machine when schedule the clients.
        
    #     Returns:
    #         A string indicates the machine's ip, or None if can not get a
    #         machine.
    #     """
    #     try:
    #         machine_index =  random.randint(0, len(self.client_dict) - 1)
    #     except ValueError as e:
    #         logging.error("Failed to get machine, msg: %s" % e)
    #         return None
    #     return self.client_dict.keys()[machine_index]

    def _get_machine_ip(self):
        """Get a machine when schedule the clients.
        
        Returns:
            A string indicates the machine's ip, or None if can not get a
            machine.
        """
        try:
            top_list = sorted(self.client_dict.iteritems(), key = lambda d : 
                d[1]['free_mem'] / d[1]['total_mem'], reverse = True)[:15]
        except ValueError as e:
            logging.error("Failed to get machine, msg: %s" % e)
            return None
        return random.choice(top_list)[0]


    def _add_client(self):
        """Add a client"""
        ip = self._get_machine_ip()
        if not ip:
            logging.info("ip is no exists")
            return
        if self.client_dict[ip]['total_mem'] == 1:
            logging.info("the machine %s is running unhealthy" % ip)
            return
        if self.client_dict[ip]['free_mem'] / self.client_dict[ip]['total_mem'] < 0.1:
            logging.info("the percent of used memory of this machine: %s is too high" % ip) 
            return
        #clients = self.client_dict[ip]['clients']
        cmd = ("cd %s/client; nohup python runner.py --log_file_max_size=%s " 
               "--log_file_num_backups=%s "
               "--log_file_prefix=%s "
               ">/dev/null 2>&1 &" % (self.cur_path, options.log_file_max_size,
               options.log_file_num_backups, options.client_log_file_prefix))
        try:
            child = subprocess.Popen(["ssh", "-o BatchMode=yes", ip, cmd])
            logging.info("Success to add the client: %s" % ip)
        except Exception, e:
            logging.error("Failed to add client, msg: %s" % e)
            return
        self.client_dict[ip]['free_mem'] = self._get_free_mem(ip)

    def _delete_client_by_pid(self, ip, pid):
        """Delete client by ip and pid"""
        try:
            child = subprocess.Popen(["ssh", "-o BatchMode=yes", "-o ConnectTimeout=10", 
                                      ip, "ps -fp %s | grep 'python runner.py' && kill %s" 
                                      % (pid, pid)])
            child.wait()
        except Exception, e:
            logging.error("Failed to delete client %s:%s, msg: %s" 
                          % (ip, pid, e))
        return

    def _delete_client(self):
        """Delete a client"""
        for i in range(3):
            ip = self._get_machine_ip()
            if len(self.client_dict[ip]['clients']) == 0:
                continue
        clients = self.client_dict[ip]['clients']
        if len(clients) <= 0:
            return
        try:
            client_index = random.randint(0, len(clients) -1)
            client_pid = clients.keys()[client_index]
            self._delete_client_by_pid(ip, client_pid)
        except ValueError as e:
            logging.error("Failed to get client from %s to delete, msg: %s"
                          % (ip, e))
            return
        except IndexError as e:
            logging.error("Failed to get client from %s to delete, msg: %s"
                          % (ip, e))
            return
        with self.client_dict_lock:
            self.cur_client_num -= 1
            del self.client_dict[ip]['clients'][client_pid]
        self.client_dict[ip]['free_mem'] = self._get_free_mem(ip)

    def _delete_all_clients(self):
        """Delete all clients"""
        for ip, machine_info in self.client_dict.iteritems():
            for client_pid in machine_info['clients'].keys():
                self._delete_client_by_pid(ip, client_pid)
        self._init_client_info()
        self.cur_client_num = 0

    def _get_update_status(self):
        """Caculate the scheduler's status according to the total task number
        and client number
        
        Returns:
            A tuple contains status and client number to add or delete.
            Status:
                0: Not change client number
                1: Add cient
                2: Delete client
                3: Delete all client
        """
        if not self.task_num_list or len(self.task_num_list) < 3:
            return (1, 50)
        if reduce((lambda x, y: x + y), self.task_num_list) == 0:
            if self.cur_client_num > 0:
                return (3, self.cur_client_num)
            else:
                return (0, 0)

        min_task_num = int(self.task_num_list[-1] ** 0.33) + 1
        if self.cur_client_num <= min_task_num:
            return (1, (((min_task_num - self.cur_client_num) >> 1) + 1))

        overflow_times = 0
        for task_num in self.task_num_list:
            if task_num > self.max_task_num - self.max_task_num / 10:
                overflow_times += 1
                continue
        if overflow_times == 3 and self.cur_client_num < self.max_client_num:
            return (1, 
                    int((self.max_client_num - self.cur_client_num) ** 0.5) + 1)

        if (self.task_num_list[1] >= self.task_num_list[0] and
            self.task_num_list[2] - self.task_num_list[1] > self.cur_client_num * 3 and 
            self.task_num_list[2] - self.task_num_list[1] >
            (self.task_num_list[1] - self.task_num_list[0]) / 2):
            return (1, 10)

        if self.task_num_list[1] < self.task_num_list[0] and \
                self.task_num_list[1] - self.task_num_list[2] > self.cur_client_num * 5 and \
                self.task_num_list[2] - self.task_num_list[1] < (self.task_num_list[1] - self.task_num_list[0]) * 2:
            return (2, 1)
        return (0, 0)

    def update_client_access_time(self, ip, pid):
        """Update client access time
        
        When client get task from master, update the access time.

        Args:
            ip: Client ip.
            pid: Client pid from.
        """
        ip = str(ip)
        pid = str(pid)
        with self.client_dict_lock:
            if ip not in self.client_dict:
                self.client_dict[ip] = {
                    'free_mem': self._get_free_mem(ip),
                    'clients': {}
                }
            if pid not in self.client_dict[ip]['clients']:
                self.cur_client_num += 1
            self.client_dict[ip]['clients'][pid] = int(time.time())

    def set_total_tasknum(self, task_size):
        """Set total task number in master
        
        Args:
            cur_size: Task number in master.
        """
        if len(self.task_num_list) == 3:
            self.task_num_list.pop(0)
        self.task_num_list.append(task_size)
    
    def add_clients(self, number):
        """Add clients.

        Args:
            number: Number of clients to add.
        """
        for i in xrange(number):
            self._add_client()

    def delete_clients(self, number):
        """Delete clients.

        Args:
            number: Number of clients to delete.
        """
        for i in xrange(number):
            self._delete_client()

    def update_clients(self):
        """Scheduler clients by the status and number"""
        update_status, update_client_num = self._get_update_status()
        if update_status == 1:
            self.add_clients(update_client_num)
        elif update_status == 2:
            self.delete_clients(update_client_num)
        elif update_status == 3:
            self._delete_all_clients() 
        else:
            return

    def status(self):
        """Status of clients"""
        return {'size': self.cur_client_num, 'data': self.client_dict}

    def stop(self):
        """Delete all clients and stop check client timer when delete scheduler"""
        self._delete_all_clients()
        self.client_check_timer.stop()


if __name__ == '__main__':
    client_scheduler = ClientScheduler(1000, None)
    print client_scheduler._get_total_mem('10.142.41.174')
    #client_scheduler.add_clients(20)
    #client_scheduler.delete_clients(20)
    print client_scheduler.status()
    client_scheduler.stop()

