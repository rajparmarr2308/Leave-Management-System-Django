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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Test skin traversal.
"""
import unittest

import zope.component
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.testing.cleanup import CleanUp


class FauxRequest:
    def shiftNameToApplication(self):
        self.shifted = 1


class IFoo(Interface):
    pass


directlyProvides(IFoo, IBrowserSkinType)


class Test(CleanUp, unittest.TestCase):

    def setUp(self):
        super().setUp()
        zope.component.provideUtility(IFoo, IBrowserSkinType, name='foo')

    def test(self):
        from zope.traversing.namespace import skin

        request = FauxRequest()
        ob = object()
        ob2 = skin(ob, request).traverse('foo', ())
        self.assertEqual(ob, ob2)
        self.assertTrue(IFoo.providedBy(request))
        self.assertEqual(request.shifted, 1)

    def test_missing_skin(self):
        from zope.location.interfaces import LocationError

        from zope.traversing.namespace import skin
        request = FauxRequest()
        ob = object()
        traverser = skin(ob, request)
        self.assertRaises(LocationError, traverser.traverse, 'bar', ())
