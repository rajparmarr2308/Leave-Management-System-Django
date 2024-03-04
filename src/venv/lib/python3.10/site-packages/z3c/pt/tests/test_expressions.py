"""
Tests for expressions.py

"""
import functools
import unittest

from zope.testing.cleanup import CleanUp

from z3c.pt import expressions


# pylint:disable=protected-access


class TestRenderContentProvider(CleanUp, unittest.TestCase):
    def test_not_found(self):
        from zope.contentprovider.interfaces import ContentProviderLookupError

        context = object()
        request = object()
        view = object()
        name = "a provider"
        econtext = {"context": context, "request": request, "view": view}

        with self.assertRaises(ContentProviderLookupError) as exc:
            expressions.render_content_provider(econtext, name)

        e = exc.exception
        self.assertEqual(e.args, (name, (context, request, view)))

    def test_sets_ilocation_name(self):
        from zope import component
        from zope import interface
        from zope.contentprovider.interfaces import IContentProvider
        from zope.location.interfaces import ILocation

        attrs = {}

        @interface.implementer(ILocation, IContentProvider)
        class Provider:
            def __init__(self, *args):
                pass

            def __setattr__(self, name, value):
                attrs[name] = value

            update = render = lambda s: None

        component.provideAdapter(
            Provider,
            adapts=(object, object, object),
            provides=IContentProvider,
            name="a provider",
        )

        context = object()
        request = object()
        view = object()
        econtext = {"context": context, "request": request, "view": view}

        expressions.render_content_provider(econtext, "a provider")

        self.assertEqual(attrs, {"__name__": "a provider"})


class TestPathExpr(CleanUp, unittest.TestCase):
    def test_translate_empty_string(self):
        import ast

        expr = expressions.PathExpr("")
        result = expr.translate("", "foo")

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ast.Assign)

    def test_translate_invalid_path(self):
        from chameleon.exc import ExpressionError

        expr = expressions.PathExpr("")
        with self.assertRaises(ExpressionError):
            expr.translate("not valid", None)

    def test_translate_components(self):
        from chameleon.compiler import ExpressionEngine
        from chameleon.compiler import ExpressionEvaluator
        from chameleon.tales import ExpressionParser
        from chameleon.utils import Scope

        parser = ExpressionParser({'path': expressions.PathExpr}, 'path')
        engine = functools.partial(ExpressionEngine, parser)

        from zope.traversing.interfaces import ITraversable

        class Context(str):
            def traverse(self, name, rest):
                return Context(name)

        from zope.interface import classImplements
        classImplements(Context, ITraversable)

        evaluator = ExpressionEvaluator(engine, {'a': Context('a')})

        def evaluate(expression, **context):
            return evaluator(Scope(context), {}, 'path', expression)

        self.assertEqual(evaluate("a"), Context('a'))

        # Single literal
        self.assertEqual(evaluate("a/b"), Context('b'))

        # Multiple literals
        self.assertEqual(evaluate("a/b/c"), Context('c'))

        # Single interpolation---must be longer than one character
        self.assertEqual(evaluate("a/?b"), Context('?b'))

        # Single interpolation
        self.assertEqual(evaluate("a/?t1", t1='b'), Context('b'))

        # Multiple interpolations
        self.assertEqual(evaluate("a/?t1/?t2", t1='b', t2='c'), Context('c'))
