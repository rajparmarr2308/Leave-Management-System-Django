##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

import unittest

from zope.tales.engine import Engine
from zope.tales.pythonexpr import ExprTypeProxy
from zope.tales.pythonexpr import PythonExpr
from zope.tales.tales import Context


class TestPythonExpr(unittest.TestCase):

    def setUp(self):
        self.context = Context(Engine, {})
        self.engine = Engine

    def test_init(self):
        expr = PythonExpr(None, 'a', None)
        self.assertEqual(expr._varnames, ('a',))

    def test_init_listcomp(self):
        expr = PythonExpr(None, '[f for f in foo if exists(f)]', None)
        self.assertEqual(expr._varnames, ('foo', 'exists'))

    def test_repr_str(self):
        expr = PythonExpr(None, 'a', None)
        self.assertEqual('Python expression "(a)"', str(expr))
        self.assertEqual('<PythonExpr (a)>', repr(expr))

    def test_bind_not_dict(self):
        expr = PythonExpr(None, 'test_bind_not_dict', None)
        names = expr._bind_used_names(self.context, type(self))

        # It found it in type(self).__dict__, so it only added
        # __builtins__ to the names
        self.assertEqual(names,
                         {'__builtins__': type(self).__dict__})

    def test_bind_as_expression(self):
        expr = PythonExpr(None, 'string("abc")', None)
        names = expr._bind_used_names(self.context, {})

        string = names['string']
        self.assertIsInstance(string, ExprTypeProxy)

        self.assertEqual(expr(self.context), "abc")

    def test_call(self):
        expr = PythonExpr(None, 'x == 1', None)
        self.context.setLocal('x', 1)
        self.assertTrue(expr(self.context))

    def test_call_listcomp(self):
        expr = PythonExpr(None, '[fmt(x) for x in foo if fmt(x)]', None)
        self.context.setLocal('foo', [0, 1, 2])
        self.context.setLocal('fmt', bool)
        self.assertEqual(expr(self.context), [True, True])
