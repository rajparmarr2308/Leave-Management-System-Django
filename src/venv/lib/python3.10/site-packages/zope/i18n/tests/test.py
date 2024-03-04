##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Misc tests
"""
import doctest
import unittest

from zope.component.testing import setUp
from zope.component.testing import tearDown


def test_suite():
    options = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

    def suite(name):
        return doctest.DocTestSuite(
            name,
            setUp=setUp, tearDown=tearDown,
            optionflags=options)

    return unittest.TestSuite([
        suite('zope.i18n'),
        suite("zope.i18n.config"),
        suite("zope.i18n.testing"),
    ])
