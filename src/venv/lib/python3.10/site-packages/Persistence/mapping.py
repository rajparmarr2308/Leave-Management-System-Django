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

from abc import ABCMeta

from ExtensionClass import ExtensionClass
from persistent.mapping import PersistentMapping as _BasePersistentMapping

from Persistence import Persistent


class _Meta(ExtensionClass, ABCMeta):
    # persistent.mapping is based on collections.UserDict,
    # which has an ABCMeta class. Reconcile this with the
    # ExtensionClass meta class, by ignoring the ABCMeta registration.

    def __new__(cls, *args, **kw):
        # Ignore ABCMeta.
        return ExtensionClass.__new__(cls, *args, **kw)

    __instancecheck__ = ExtensionClass.__instancecheck__
    __subclasscheck__ = ExtensionClass.__subclasscheck__


class PersistentMapping(Persistent, _BasePersistentMapping, metaclass=_Meta):
    """Legacy persistent mapping class

        This class mixes in :class:`ExtensionClass.Base` if it is present.

        Unless you actually want ExtensionClass semantics, use
        :class:`persistent.mapping.PersistentMapping` instead.
        """

    def __setstate__(self, state):
        if 'data' not in state:
            state['data'] = state['_container']
            del state['_container']
        self.__dict__.update(state)
