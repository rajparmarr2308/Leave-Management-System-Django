##############################################################################
#
# Copyright (c) 2018 Zope Foundation and Contributors.
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
Tests for the documentation.
"""

import doctest
import unittest


optionflags = (
    doctest.NORMALIZE_WHITESPACE
    | doctest.ELLIPSIS
    | doctest.IGNORE_EXCEPTION_DETAIL
)


def test_suite():
    suite = unittest.TestSuite()
    api_to_test = (
        'config',
        'docutils',
        'fields',
        'interfaces',
        'name',
        'xmlconfig',
        'zopeconfigure',
    )

    for mod_name in api_to_test:
        mod_name = 'zope.configuration.' + mod_name
        suite.addTest(
            doctest.DocTestSuite(
                mod_name,
                optionflags=optionflags
            )
        )

    return suite
