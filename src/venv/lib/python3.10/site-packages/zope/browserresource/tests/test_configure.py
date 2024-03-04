import doctest
import unittest

from zope.component.testing import setUp
from zope.component.testing import tearDown


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'configure.txt', setUp=setUp, tearDown=tearDown))
    return suite
