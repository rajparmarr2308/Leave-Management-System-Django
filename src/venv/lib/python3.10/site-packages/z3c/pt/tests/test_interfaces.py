##############################################################################
#
# Copyright (c) 2023 Zope Foundation and Contributors.
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
import unittest

import zope.component.testing
import zope.configuration.xmlconfig
from chameleon.tal import ErrorInfo
from chameleon.tal import RepeatItem

import z3c.pt
from z3c.pt.interfaces import ITALESIterator
from z3c.pt.interfaces import ITALExpressionErrorInfo


def setUp(suite):
    zope.component.testing.setUp(suite)
    zope.configuration.xmlconfig.XMLConfig("configure.zcml", z3c.pt)()


class TestRenderContentProvider(unittest.TestCase):
    setUp = setUp
    tearDown = zope.component.testing.tearDown

    def test_implements(self):
        self.assertTrue(ITALExpressionErrorInfo.implementedBy(ErrorInfo))
        self.assertTrue(ITALESIterator.implementedBy(RepeatItem))
