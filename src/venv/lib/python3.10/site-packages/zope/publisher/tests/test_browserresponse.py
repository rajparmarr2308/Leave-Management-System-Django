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
"""Browser response tests
"""

import sys
from unittest import TestCase

from zope.interface.verify import verifyObject

from zope.publisher.browser import BrowserResponse
from zope.publisher.interfaces import IResponse
from zope.publisher.interfaces.http import IHTTPApplicationResponse
from zope.publisher.interfaces.http import IHTTPResponse


# TODO: Waaa need more tests

class TestBrowserResponse(TestCase):

    def test_contentType_DWIM_in_setResult(self):
        response = BrowserResponse()
        response.setResult(
            """<html>
            <blah>
            </html>
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/html"))

        response = BrowserResponse()
        response.setResult(
            """<html foo="1"
            bar="x">
            <blah>
            </html>
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/html"))

        response = BrowserResponse()
        response.setResult(
            """<html foo="1"
            bar="x">
            <blah>
            </html>
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/html"))

        response = BrowserResponse()
        response.setResult(
            """<!doctype html>
            <html foo="1"
            bar="x">
            <blah>
            </html>
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/html"))

        response = BrowserResponse()
        response.setResult(
            """Hello world
            """)
        self.assertTrue(response.getHeader('content-type').startswith(
            "text/plain")
        )

        response = BrowserResponse()
        response.setResult(
            """<p>Hello world
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/plain")
        )

        response = BrowserResponse()
        response.setResult(
            b"""Hello world
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/plain")
        )

        response = BrowserResponse()
        response.setResult(
            b"""\xff
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/plain")
        )

    def test_not_DWIM_for_304_response(self):
        # Don't guess the content type with 304 responses which MUST NOT /
        # SHOULD NOT include it.
        #
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5
        #
        # NOTE: The content type is sill guessed if status us set after
        #       the result :(
        response = BrowserResponse()
        response.setStatus(304)
        response.setResult(b'')
        self.assertEqual(response.getHeader('content-type'), None)

    def testInsertBase(self):
        response = BrowserResponse()
        response.setHeader('content-type', 'text/html')

        insertBase = response._BrowserResponse__insertBase

        # Make sure that bases are inserted
        response.setBase('http://localhost/folder/')
        self.assertIn(
            b'<base href="http://localhost/folder/" />',
            insertBase(b'<html><head></head><body>Page</body></html>'))

        # Ensure that unicode bases work as well
        response.setBase('http://localhost/folder/')
        body = insertBase(b'<html><head></head><body>Page</body></html>')
        self.assertIsInstance(body, bytes)
        self.assertIn(b'<base href="http://localhost/folder/" />', body)

        # Ensure that encoded bodies work, when a base is inserted.
        response.setBase('http://localhost/folder')
        result = insertBase(
            b'<html><head></head><body>\xc3\x9bung</body></html>')
        self.assertIsInstance(body, bytes)
        self.assertIn(b'<base href="http://localhost/folder" />', result)

    def testInsertBaseInSetResultUpdatesContentLength(self):
        # Make sure that the Content-Length header is updated to account
        # for an inserted <base> tag.
        response = BrowserResponse()
        response.setHeader('content-type', 'text/html')
        base = 'http://localhost/folder/'
        response.setBase(base)
        inserted_text = '\n<base href="%s" />\n' % base
        html_page = b"""<html>
            <head></head>
            <blah>
            </html>
            """
        response.setResult(html_page)
        self.assertEqual(
            int(response.getHeader('content-length')),
            len(html_page) + len(inserted_text))

    def test_interface(self):
        rp = BrowserResponse()
        verifyObject(IHTTPResponse, rp)
        verifyObject(IHTTPApplicationResponse, rp)
        verifyObject(IResponse, rp)

    def test_handleException(self):
        response = BrowserResponse()
        try:
            raise ValueError(1)
        except:  # noqa: E722 do not use bare 'except'
            exc_info = sys.exc_info()

        response.handleException(exc_info)
        self.assertEqual(response.getHeader("content-type"),
                         "text/html;charset=utf-8")
        self.assertEqual(response.getStatus(), 500)
        self.assertIn(
            response.consumeBody(),
            [b"<html><head>"
             b"<title>&lt;type 'exceptions.ValueError'&gt;</title></head>\n"
             b"<body><h2>&lt;type 'exceptions.ValueError'&gt;</h2>\n"
             b"A server error occurred.\n"
             b"</body></html>\n",
             b"<html><head><title>ValueError</title></head>\n"
             b"<body><h2>ValueError</h2>\n"
             b"A server error occurred.\n"
             b"</body></html>\n"]
        )
