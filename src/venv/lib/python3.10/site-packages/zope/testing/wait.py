##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Provides a class, `Wait`, and an instance, `wait`, that can be
used for polling for a condition to become true, or raise an exception
after a timeout.
"""


import time


class Wait:
    """
    A callable object that polls until *func* returns
    a true value, sleeping *wait* seconds between
    polling attempts.

    If *timeout* seconds elapse, *exception* will be raised.
    """

    class TimeOutWaitingFor(Exception):
        "The default exception raised when a test condition timed out."

    #: The default timeout value.
    timeout = 9
    #: The default amount of time to sleep between polls.
    wait = .01

    def __init__(self,
                 timeout=None, wait=None, exception=None,
                 getnow=lambda: time.time, getsleep=lambda: time.sleep):

        if timeout is not None:
            self.timeout = timeout

        if wait is not None:
            self.wait = wait

        if exception is not None:
            self.TimeOutWaitingFor = exception

        self.getnow = getnow
        self.getsleep = getsleep

    def __call__(self, func=None, timeout=None, wait=None, message=None):
        if func is None:
            return lambda func: self(func, timeout, wait, message)

        if func():
            return

        now = self.getnow()
        sleep = self.getsleep()
        if timeout is None:
            timeout = self.timeout
        if wait is None:
            wait = self.wait
        wait = float(wait)

        deadline = now() + timeout
        while 1:
            sleep(wait)
            if func():
                return
            if now() > deadline:
                raise self.TimeOutWaitingFor(
                    message or
                    getattr(func, '__doc__') or
                    getattr(func, '__name__')
                )


#: The default instance of `Wait`.
wait = Wait()
