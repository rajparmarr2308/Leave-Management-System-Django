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
"""Helper functions for the test suite.
"""
import os
import sys
import unittest


mydir = os.path.abspath(os.path.dirname(__file__))
codedir = os.path.dirname(os.path.dirname(os.path.dirname(mydir)))

if codedir not in sys.path:
    sys.path.append(codedir)


# Set skipxml to true if an XML parser could not be found.
skipxml = 0
try:
    import xml.parsers.expat  # noqa: F401 imported but unused
except ImportError:
    skipxml = 1


def run_suite(suite, outf=None, errf=None):
    if outf is None:
        outf = sys.stdout
    runner = unittest.TextTestRunner(outf)
    result = runner.run(suite)

    newerrs = len(result.errors) + len(result.failures)
    if newerrs:
        print("'Errors' indicate exceptions other than AssertionError.")
        print("'Failures' indicate AssertionError")
        if errf is None:
            errf = sys.stderr
        errf.write("%d errors, %d failures\n"
                   % (len(result.errors), len(result.failures)))
    return newerrs


def print_error(info):
    testcase, (type, e, tb) = info
