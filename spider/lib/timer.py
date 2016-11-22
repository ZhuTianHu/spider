#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import threading


class Timer(threading.Thread):
    """A timer to run task regularly"""
    def __init__(self, seconds, fun, **kwargs):
        """Init a timer.
        
        Args:
            seconds: Peroid of running task.
            fun: Function to run.
            kwargs: Parameters of function.
        """
        self.sleep_time = seconds
        threading.Thread.__init__(self)
        self.fun = fun
        self.kwargs = kwargs
        self.is_stop = threading.Event()

    def run(self):
        while not self.is_stop.is_set():
            self.fun(**self.kwargs)
            self.is_stop.wait(timeout=self.sleep_time)

    def stop(self, *args):
        self.is_stop.set()

class CountDownTimer(Timer):
    """A timer to run task specified times regularly"""
    def __init__(self, seconds, total_times, fun, **kwargs):
        """Init a timer

        Args:
            seconds: Period of running task.
            total_times: Number of times to run the task.
            fun: Function to run.
            kwargs: Parameters of function.
        """
        self.total_times = total_times
        Timer.__init__(self, seconds, fun, args)
    
    def run(self):
        counter = 0
        while counter < self.total_times and self.is_run:
            time.sleep(self.sleep_time)
            self.fun(**self.args)
            counter += 1


if __name__ == "__main__":
    def test(s):
        print s
    timer = Timer(2, test, s="a")
    timer.start()
    import signal
    signal.signal(signal.SIGINT, timer.stop)
    signal.signal(signal.SIGTERM, timer.stop)
    signal.pause()
