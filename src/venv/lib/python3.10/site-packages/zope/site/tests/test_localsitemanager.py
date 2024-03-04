##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Local sitemanager tests.
"""
import unittest

from zope.interface import Interface

import zope.site.testing
from zope import site
from zope.site.folder import Folder


class I1(Interface):
    pass


class TestLocalSiteManager(unittest.TestCase):

    def setUp(self):
        zope.site.testing.siteSetUp()
        self.util = object()
        self.root = Folder()
        self.root['site'] = Folder()
        subfolder = self.root['site']
        subfolder.setSiteManager(site.LocalSiteManager(subfolder))
        subfolder.getSiteManager().registerUtility(self.util, I1)

    def tearDown(self):
        zope.site.testing.siteTearDown()

    def testPersistence(self):
        from pickle import dumps
        from pickle import loads
        self.assertTrue(
            self.root['site'].getSiteManager().getUtility(I1) is self.util)

        data = dumps(self.root['site'])
        self.root['copied_site'] = loads(data)

        self.assertIsNot(
            self.root['copied_site'].getSiteManager().getUtility(I1),
            self.util)


def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromTestCase(TestLocalSiteManager),
    ))
