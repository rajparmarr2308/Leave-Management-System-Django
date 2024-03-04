##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Stack-based test `doctest` ``setUp`` and `tearDown`

See :doc:`../setupstack`
"""

import os
import stat
import tempfile
import unittest


key = '__' + __name__


def globs(test):
    """
    Return the globals for *test*, which can be a `doctest`
    or a regular `unittest.TestCase`.
    """
    try:
        return test.globs
    except AttributeError:
        return test.__dict__


def register(test, function, *args, **kw):
    """
    Add a clean up *function* to be called with
    *args* and *kw* when *test* is torn down.

    Clean up functions are called in the reverse order
    of registration.
    """
    tglobs = globs(test)
    stack = tglobs.get(key)
    if stack is None:
        stack = tglobs[key] = []
    stack.append((function, args, kw))


def tearDown(test):
    """
    Call all the clean up functions registered for *test*,
    in the reverse of their registration order.
    """
    tglobs = globs(test)
    stack = tglobs.get(key)
    while stack:
        f, p, k = stack.pop()
        f(*p, **k)


def setUpDirectory(test):
    """
    Create and change to a temporary directory, and `register`
    `rmtree` to clean it up. Returns to the starting directory
    when finished.
    """
    tmp = tempfile.mkdtemp()
    register(test, rmtree, tmp)
    here = os.getcwd()
    register(test, os.chdir, here)
    os.chdir(tmp)


def rmtree(path):
    """
    Remove all the files and directories
    found in *path*.

    Intended to be used as a clean up function with *register*.
    """
    for path, dirs, files in os.walk(path, False):
        for fname in files:
            fname = os.path.join(path, fname)
            if not os.path.islink(fname):
                os.chmod(fname, stat.S_IWUSR)
            os.remove(fname)
        for dname in dirs:
            dname = os.path.join(path, dname)
            os.rmdir(dname)
    os.rmdir(path)


def context_manager(test, manager):
    """
    A stack-based version of the **with** statement.

    The context manager *manager* is entered when this
    method is called, and it is exited when the *test*
    is torn down.
    """
    result = manager.__enter__()
    register(test, manager.__exit__, None, None, None)
    return result


def _get_mock():
    # A hook for the setupstack.txt doctest :
    from unittest import mock as mock_module

    return mock_module


def mock(test, *args, **kw):
    """
    Patch an object by calling `unittest.mock.patch`
    with the *args* and *kw* given, and returns the result.

    This will be torn down when the *test* is torn down.
    """
    mock_module = _get_mock()
    return context_manager(test, mock_module.patch(*args, **kw))


class TestCase(unittest.TestCase):
    """
    A ``TestCase`` base class that overrides `tearDown`
    to use the function from this module.

    In addition, it provides other methods using the
    functions in this module:

    - `register`
    - `setUpDirectory`
    - `context_manager`
    - `mock`

    """

    tearDown = tearDown
    register = register
    setUpDirectory = setUpDirectory
    context_manager = context_manager
    mock = mock
