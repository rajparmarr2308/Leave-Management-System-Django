##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Tests standard date parsing
"""
import datetime
import unittest

from zope.datetime import time


class FakeDateTime:
    """A class which mimics a DateTime class which can be converted to int.

    It behaves like the Zope DateTime class in the DateTime package.
    """

    time = time("2000-01-01T01:01:01.234Z")

    def __int__(self):
        return int(self.time)


class Test(unittest.TestCase):

    def testiso8601_date(self):
        from zope.datetime import iso8601_date
        self.assertEqual(iso8601_date(time("2000-01-01T01:01:01.234Z")),
                         "2000-01-01T01:01:01Z")

    def testiso8601_date__2(self):
        """It converts its parameter to an int."""
        from zope.datetime import iso8601_date
        self.assertEqual(iso8601_date(FakeDateTime()), "2000-01-01T01:01:01Z")

    def testiso8601_date__3(self):
        """It uses the current time if no parameter is given."""
        from zope.datetime import iso8601_date
        self.assertTrue(
            iso8601_date().startswith(str(datetime.date.today())))

    def testrfc850_date(self):
        from zope.datetime import rfc850_date
        self.assertEqual(rfc850_date(time("2002-01-12T01:01:01.234Z")),
                         "Saturday, 12-Jan-02 01:01:01 GMT")

    def testrfc850_date__2(self):
        """It converts its parameter to an int."""
        from zope.datetime import rfc850_date
        self.assertEqual(rfc850_date(FakeDateTime()),
                         "Saturday, 01-Jan-00 01:01:01 GMT")

    def testrfc850_date__3(self):
        """It uses the current time if no parameter is given."""
        from zope.datetime import rfc850_date
        self.assertIn(datetime.date.today().strftime('%d-%b-%y'),
                      rfc850_date())

    def testrfc1123_date(self):
        from zope.datetime import rfc1123_date
        self.assertEqual(rfc1123_date(time("2002-01-12T01:01:01.234Z")),
                         "Sat, 12 Jan 2002 01:01:01 GMT")

    def testrfc1123_date__2(self):
        """It converts its parameter to an int."""
        from zope.datetime import rfc1123_date
        self.assertEqual(rfc1123_date(FakeDateTime()),
                         "Sat, 01 Jan 2000 01:01:01 GMT")

    def testrfc1123_date__3(self):
        """It uses the current time if no parameter is given."""
        from zope.datetime import rfc1123_date
        self.assertIn(datetime.date.today().strftime('%d %b %Y'),
                      rfc1123_date())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
