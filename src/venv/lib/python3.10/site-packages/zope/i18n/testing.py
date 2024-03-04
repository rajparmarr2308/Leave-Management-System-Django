##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
Unit test logic for setting up and tearing down basic infrastructure.

This relies on :mod:`zope.publisher` being available.
"""
import os.path

from pythongettext.msgfmt import Msgfmt


def setUp(test=None):
    import zope.component
    from zope.publisher.browser import BrowserLanguages
    from zope.publisher.http import HTTPCharsets
    zope.component.provideAdapter(HTTPCharsets)
    zope.component.provideAdapter(BrowserLanguages)


class PlacelessSetup:

    def setUp(self):
        """
        Install the language and charset negotiators.

        >>> PlacelessSetup().setUp()
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.i18n.interfaces import IUserPreferredCharsets
        >>> from zope.i18n.interfaces import IUserPreferredLanguages
        >>> from zope.component import getAdapter
        >>> getAdapter(TestRequest(), IUserPreferredCharsets)
        <zope.publisher.http.HTTPCharsets ...>
        >>> getAdapter(TestRequest(), IUserPreferredLanguages)
        <zope.publisher.browser.BrowserLanguages ...>

        """
        setUp()


def compile_po(mo_path):
    """If `mo_path` does not exist, compile its po file."""
    if not os.path.exists(mo_path):  # pragma: no cover
        po_path = mo_path.replace('.mo', '.po')
        mo_content = Msgfmt(po_path, name=po_path).get()
        with open(mo_path, "wb") as mo:
            mo.write(mo_content)
