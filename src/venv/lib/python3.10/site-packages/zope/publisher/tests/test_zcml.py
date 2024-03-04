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
"""Tests for browser:defaultSkin and browser:defaultView directives
"""
import doctest
import unittest
from io import BytesIO

from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.xmlconfig import xmlconfig
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.interface import providedBy
from zope.testing import cleanup

import zope.publisher
from zope import component
from zope.publisher.browser import BrowserView
from zope.publisher.browser import TestRequest
from zope.publisher.defaultview import getDefaultViewName
from zope.publisher.interfaces import IDefaultSkin
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserRequest


class IOb(Interface):
    pass


@implementer(IOb)
class Ob:
    pass


class ITestLayer(IBrowserRequest):
    """Test Layer."""


class ITestSkin(ITestLayer):
    """Test Skin."""


class V1(BrowserView):
    pass


class V2(BrowserView):
    pass


request = TestRequest()
ob = Ob()

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


def templated(contents):
    body = template % contents
    return BytesIO(body.encode('latin-1'))


class Test(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super().setUp()
        XMLConfig('meta.zcml', zope.publisher)()

    def testDefaultView(self):
        self.assertIsNone(
            component.queryMultiAdapter((ob, request), IDefaultViewName))
        xmlconfig(templated(
            '''
            <browser:defaultView
                name="test"
                for="zope.publisher.tests.test_zcml.IOb" />
            '''
        ))

        self.assertEqual(getDefaultViewName(ob, request), 'test')

    def testDefaultViewWithLayer(self):
        @implementer(ITestLayer)
        class FakeRequest(TestRequest):
            pass
        request2 = FakeRequest()

        self.assertEqual(
            component.queryMultiAdapter((ob, request2), IDefaultViewName),
            None)

        xmlconfig(templated(
            '''
            <browser:defaultView
                for="zope.publisher.tests.test_zcml.IOb"
                name="test"
                />
            <browser:defaultView
                for="zope.publisher.tests.test_zcml.IOb"
                layer="zope.publisher.tests.test_zcml.ITestLayer"
                name="test2"
                />
            '''
        ))

        self.assertEqual(
            zope.publisher.defaultview.getDefaultViewName(ob, request2),
            'test2')
        self.assertEqual(
            zope.publisher.defaultview.getDefaultViewName(ob, request),
            'test')

    def testDefaultViewForClass(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), IDefaultViewName),
            None)

        xmlconfig(templated(
            '''
            <browser:defaultView
                for="zope.publisher.tests.test_zcml.Ob"
                name="test"
                />
            '''
        ))

        self.assertEqual(
            zope.publisher.defaultview.getDefaultViewName(ob, request),
            'test')

    def testDefaultSkin(self):
        request = TestRequest()
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='test'),
            None)

        XMLConfig('meta.zcml', component)()
        xmlconfig(templated(
            '''
            <interface
                interface="
                  zope.publisher.tests.test_zcml.ITestSkin"
                type="zope.publisher.interfaces.browser.IBrowserSkinType"
                name="Test Skin"
                />
            <browser:defaultSkin name="Test Skin" />
            <view
                for="zope.publisher.tests.test_zcml.IOb"
                type="zope.publisher.interfaces.browser.IDefaultBrowserLayer"
                name="test"
                factory="zope.publisher.tests.test_zcml.V1"
                />
            <view
                for="zope.publisher.tests.test_zcml.IOb"
                type="zope.publisher.tests.test_zcml.ITestLayer"
                name="test"
                factory="zope.publisher.tests.test_zcml.V2"
                />
            '''
        ))

        # Simulate Zope Publication behavior in beforeTraversal()
        adapters = component.getSiteManager().adapters
        skin = adapters.lookup((providedBy(request),), IDefaultSkin, '')
        directlyProvides(request, skin)

        v = component.queryMultiAdapter((ob, request), name='test')
        self.assertTrue(isinstance(v, V2))


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromTestCase(Test),
        doctest.DocFileSuite('../configure.txt'),
    ))
