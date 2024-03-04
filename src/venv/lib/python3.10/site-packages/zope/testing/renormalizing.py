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
"""
Support for advanced normalization of output in doctests.

See :doc:`../renormalizing` for documentation.
"""
import doctest


class OutputChecker(doctest.OutputChecker):
    """Pattern-normalizing output checker
    """

    def __init__(self, patterns=None):
        if patterns is None:
            patterns = []
        self.transformers = list(map(self._cook, patterns))

    def __add__(self, other):
        if not isinstance(other, RENormalizing):
            return NotImplemented
        return RENormalizing(self.transformers + other.transformers)

    def _cook(self, pattern):
        if hasattr(pattern, '__call__'):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def check_output(self, want, got, optionflags):
        if got == want:
            return True

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        if doctest.OutputChecker.check_output(self, want, got, optionflags):
            return True
        return False

    def output_difference(self, example, got, optionflags):
        want = example.want

        # If want is empty, use original outputter. This is useful
        # when setting up tests for the first time.  In that case, we
        # generally use the differencer to display output, which we evaluate
        # by hand.
        if not want.strip():
            return doctest.OutputChecker.output_difference(
                self, example, got, optionflags)

        # Dang, this isn't as easy to override as we might wish
        original = want

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        # temporarily hack example with normalized want:
        example.want = want

        result = doctest.OutputChecker.output_difference(
            self, example, got, optionflags)
        example.want = original

        return result


RENormalizing = OutputChecker
