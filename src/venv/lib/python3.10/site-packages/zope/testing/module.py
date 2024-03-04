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
"""Fake module support.

See :doc:`../module` for documentation.
"""

import sys


__all__ = [
    'setUp',
    'tearDown',
]


class FakeModule:
    def __init__(self, dict):
        self.__dict = dict

    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)

    def __dir__(self):
        return self.__dict.keys()


def setUp(test, name='__main__'):
    """
    Replace the module named *name* with a fake version.
    """
    dict = test.globs
    dict['__name__'] = name
    module = FakeModule(dict)
    sys.modules[name] = module
    if '.' in name:
        name = name.split('.')
        parent = sys.modules['.'.join(name[:-1])]
        setattr(parent, name[-1], module)


def tearDown(test, name=None):
    """
    Remove the (fake) module named *name*.
    """
    if name is None:
        name = test.globs['__name__']
    del test.globs['__name__']
    del sys.modules[name]
    if '.' in name:
        name = name.split('.')
        parent = sys.modules['.'.join(name[:-1])]
        delattr(parent, name[-1])
