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
"""'browser' namespace directive tests
"""

import os
import sys
import unittest
from io import StringIO

import zope.security.management
from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.xmlconfig import xmlconfig
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.testing import cleanup
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable

import zope.browsermenu
from zope import component
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IMenuItemType
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import getFirstMenuItem


class IV(Interface):

    def index():
        """Return index text"""


class IC(Interface):
    """An interface"""


@implementer(IV)
class V1:
    pass


tests_path = os.path.join(
    os.path.dirname(zope.browsermenu.__file__),
    'tests')


template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


request = TestRequest()


class M1(BrowserMenu):
    pass


class V2(V1):
    pass


class VT(V1):
    pass


@implementer(IC)
class Ob:
    pass


ob = Ob()


class NCV:
    """non callable view"""


class CV(NCV):
    """callable view"""

    def __call__(self):
        raise AssertionError("Not called")


@implementer(Interface)
class C_w_implements(NCV):

    def index(self):
        raise AssertionError("Not called")


class ITestMenu(Interface):
    """Test menu."""


directlyProvides(ITestMenu, IMenuItemType)


class ITestLayer(IBrowserRequest):
    """Test Layer."""


class ITestSkin(ITestLayer):
    """Test Skin."""


class MyResource:
    pass


class Test(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super().setUp()
        XMLConfig('meta.zcml', zope.browsermenu)()
        component.provideAdapter(DefaultTraversable, (None,), ITraversable)

    def tearDown(self):
        if 'test_menu' in dir(sys.modules['zope.app.menus']):
            delattr(sys.modules['zope.app.menus'], 'test_menu')
        super().tearDown()

    def testMenuOverride(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='test'),
            None)

        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu" />
            <browser:menuItem
                action="@@test"
                for="zope.component.testfiles.views.IC"
                permission="zope.Public"
                menu="test_menu"
                title="Test View"
                />
            '''
        )))
        menu1 = component.getUtility(IBrowserMenu, 'test_menu')
        menuItem1 = getFirstMenuItem('test_menu', ob, TestRequest())
        xmlconfig(StringIO(template % (
            '''
            <browser:menu
                id="test_menu" title="Test menu"
                class="zope.browsermenu.tests.test_directives.M1" />
            '''
        )))
        menu2 = component.getUtility(IBrowserMenu, 'test_menu')
        menuItem2 = getFirstMenuItem('test_menu', ob, TestRequest())
        self.assertNotEqual(menu1, menu2)
        self.assertEqual(menuItem1, menuItem2)

    def testMenuItemNeedsFor(self):
        # <browser:menuItem> directive fails if no 'for' argument was provided
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(
                template %
                '''
                <browser:menu
                    id="test_menu" title="Test menu" />
                <browser:menuItem
                    title="Test Entry"
                    menu="test_menu"
                    action="@@test"
                />
                '''
            ))

        # it works, when the argument is there and a valid interface
        xmlconfig(StringIO(
            template %
            '''
            <browser:menuItem
                for="zope.component.testfiles.views.IC"
                title="Test Entry"
                menu="test_menu"
                action="@@test"
            />
            '''
        ))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
