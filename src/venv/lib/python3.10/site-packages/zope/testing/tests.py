##############################################################################
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
"""Tests for the testing framework.
"""
import doctest
import re
import sys
import unittest

from zope.testing import renormalizing


def print_(*args):
    sys.stdout.write(' '.join(map(str, args))+'\n')


def setUp(test):
    test.globs['print_'] = print_


def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite('module.txt'),
        doctest.DocFileSuite('loggingsupport.txt', setUp=setUp),
        doctest.DocFileSuite('renormalizing.txt', setUp=setUp),
        doctest.DocFileSuite('setupstack.txt', setUp=setUp),
        doctest.DocFileSuite('wait.txt', setUp=setUp)
    ))

    suite.addTests(
        doctest.DocFileSuite(
            'doctestcase.txt',
            checker=renormalizing.RENormalizing([
                # for Python 3.11+
                (re.compile(r'\(tests\.MyTest\.test.?\)'), '(tests.MyTest)'),
                (re.compile(r'\(tests.MoreTests.test_.*\)'),
                 '(tests.MoreTests)')
                ])))
    suite.addTests(doctest.DocFileSuite('cleanup.txt'))
    suite.addTests(doctest.DocFileSuite('formparser.txt', setUp=setUp))
    return suite
