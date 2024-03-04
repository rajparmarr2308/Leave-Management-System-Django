#############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
import os
import platform

import persistent
from ExtensionClass import Base
from ExtensionClass import Base_getattro
from persistent.persistence import _SPECIAL_NAMES


IS_PYPY = getattr(platform, 'python_implementation', lambda: None)() == 'PyPy'
IS_PURE = int(os.environ.get('PURE_PYTHON', '0'))

CAPI = not (IS_PYPY or IS_PURE)
if CAPI:  # pragma: no cover
    # Both of our dependencies need to have working C extensions
    import persistent.cPersistence
    from ExtensionClass import _ExtensionClass  # NOQA


class Persistent(persistent.Persistent, Base):
    """Legacy persistent class

    This class mixes in :class:`ExtensionClass.Base` if it is present.

    Unless you actually want ExtensionClass semantics, use
    :class:`persistent.mapping.Persistent` instead.
    """
    __slots__ = ()

    def __getattribute__(self, name):
        """ See IPersistent.
        """
        oga = Base_getattro
        if (not name.startswith('_p_') and
                name not in _SPECIAL_NAMES):
            if oga(self, '_Persistent__flags') is None:
                oga(self, '_p_activate')()
            oga(self, '_p_accessed')()
        return oga(self, name)


if CAPI:  # pragma: no cover
    # Override the Python implementation with the C one
    from Persistence._Persistence import Persistent  # NOQA

Overridable = Persistent

# API Import after setting up the base class
from Persistence.mapping import PersistentMapping  # NOQA
