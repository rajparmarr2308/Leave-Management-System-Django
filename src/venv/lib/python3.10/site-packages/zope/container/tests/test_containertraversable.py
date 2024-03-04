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
"""Container Traverser tests.
"""

import unittest

from zope.interface import implementer
from zope.testing.cleanup import CleanUp
from zope.traversing.interfaces import TraversalError

from zope.container.interfaces import IContainer
from zope.container.traversal import ContainerTraversable


@implementer(IContainer)
class Container:

    def __init__(self, attrs=None, objs=None):
        for attr, value in (attrs or {}).items():
            setattr(self, attr, value)

        self.__objs = {}
        for name, value in (objs or {}).items():
            self.__objs[name] = value

    def get(self, name, default=None):
        return self.__objs.get(name, default)


class Test(CleanUp, unittest.TestCase):
    def testAttr(self):
        # test container path traversal
        foo = Container()
        bar = Container()
        baz = Container()
        c = Container({'foo': foo}, {'bar': bar, 'foo': baz})

        T = ContainerTraversable(c)
        self.assertTrue(T.traverse('foo', []) is baz)
        self.assertTrue(T.traverse('bar', []) is bar)
        self.assertRaises(TraversalError, T.traverse, 'morebar', [])

    def test_unicode_obj(self):
        # test traversal with unicode
        voila = Container()
        c = Container({}, {'voil\xe0': voila})
        self.assertIs(ContainerTraversable(c).traverse('voil\xe0', []),
                      voila)

    def test_unicode_attr(self):
        c = Container()
        with self.assertRaises(TraversalError):
            ContainerTraversable(c).traverse('voil\xe0', [])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main()
