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
"""Test mapply() function
"""
import unittest

from zope.publisher.publish import mapply


class MapplyTests(unittest.TestCase):
    def testMethod(self):
        def compute(a, b, c=4):
            return '%d%d%d' % (a, b, c)
        values = {'a': 2, 'b': 3, 'c': 5}
        v = mapply(compute, (), values)
        self.assertEqual(v, '235')

        v = mapply(compute, (7,), values)
        self.assertEqual(v, '735')

    def testClass(self):
        values = {'a': 2, 'b': 3, 'c': 5}

        class c:
            a = 3

            def __call__(self, b, c=4):
                return '%d%d%d' % (self.a, b, c)
            compute = __call__
        cc = c()
        v = mapply(cc, (), values)
        self.assertEqual(v, '335')

        del values['c']
        v = mapply(cc.compute, (), values)
        self.assertEqual(v, '334')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(MapplyTests)
