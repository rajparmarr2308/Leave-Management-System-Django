##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Unit tests for Resource
"""
import unittest

import zope.component.interfaces
from zope.publisher.browser import TestRequest
from zope.testing import cleanup
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL

from zope import component
from zope.browserresource.resource import Resource
from zope.browserresource.tests import support


class TestResource(support.SiteHandler, cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super().setUp()
        component.provideAdapter(AbsoluteURL, (None, None), IAbsoluteURL)

    def testGlobal(self):
        req = TestRequest()
        r = Resource(req)
        req._vh_root = support.site
        r.__parent__ = support.site
        r.__name__ = 'foo'
        self.assertEqual(r(), 'http://127.0.0.1/@@/foo')
        r.__name__ = '++resource++foo'
        self.assertEqual(r(), 'http://127.0.0.1/@@/foo')

    def testGlobalInVirtualHost(self):
        req = TestRequest()
        req.setVirtualHostRoot(['x', 'y'])
        r = Resource(req)
        req._vh_root = support.site
        r.__parent__ = support.site
        r.__name__ = 'foo'
        self.assertEqual(r(), 'http://127.0.0.1/x/y/@@/foo')

    def testResourceUrl(self):
        # fake IAbsoluteURL adapter
        def resourceBase(site, request):
            return 'http://cdn.example.com'
        component.provideAdapter(
            resourceBase,
            (zope.component.interfaces.ISite, TestRequest),
            IAbsoluteURL, 'resource')

        req = TestRequest()
        r = Resource(req)
        req._vh_root = support.site
        r.__parent__ = support.site
        r.__name__ = 'foo'
        self.assertEqual(r(), 'http://cdn.example.com/@@/foo')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestResource)
