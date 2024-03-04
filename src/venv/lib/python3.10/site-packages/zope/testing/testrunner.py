import warnings


warnings.warn('zope.testing.testrunner is deprecated in favour of '
              'zope.testrunner', DeprecationWarning, stacklevel=2)

try:
    import zope.testing
    from zope import testrunner

    # Now replace this module with the right one:
    zope.testing.testrunner = testrunner
except ImportError:
    pass
