##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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

class implementer_if_needed:
    # Helper to make sure we don't redundantly implement
    # interfaces already inherited. Doing so tends to produce
    # problems with the C3 order. In this package, we could easily
    # statically determine to elide the relevant interfaces, but
    # this is a defense against changes in parent classes and lessens
    # the testing burden.
    def __init__(self, *ifaces):
        self._ifaces = ifaces

    def __call__(self, cls):
        from zope.interface import implementedBy
        from zope.interface import implementer

        ifaces_needed = []
        implemented = implementedBy(cls)
        ifaces_needed = [
            iface
            for iface in self._ifaces
            if not implemented.isOrExtends(iface)
        ]
        return implementer(*ifaces_needed)(cls)
