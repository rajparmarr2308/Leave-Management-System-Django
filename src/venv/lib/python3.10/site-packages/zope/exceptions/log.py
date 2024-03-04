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
"""Log formatter that enhances tracebacks with extra information.
"""

import io
import logging

from zope.exceptions.exceptionformatter import print_exception


class Formatter(logging.Formatter):

    def formatException(self, ei):
        """Format and return the specified exception information as a string.

        Uses zope.exceptions.exceptionformatter to generate the traceback.
        """
        sio = io.StringIO()
        print_exception(ei[0], ei[1], ei[2], file=sio, with_filenames=True)
        s = sio.getvalue()
        s = s[:-1] if s.endswith("\n") else s
        return s
