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
"""
Convenience functions for traversing the object tree.

This module provides :class:`zope.traversing.interfaces.ITraversalAPI`
"""
from zope.interface import moduleProvides
from zope.location.interfaces import ILocationInfo
from zope.location.interfaces import IRoot

from zope.traversing.adapters import traversePathElement
from zope.traversing.interfaces import ITraversalAPI
from zope.traversing.interfaces import ITraverser


# The authoritative documentation for these functions
# is in this interface. Later, we replace all our docstrings
# with those defined in the interface.
moduleProvides(ITraversalAPI)
__all__ = tuple(ITraversalAPI)

_marker = object()


def joinPath(path, *args):
    """
    Join the given relative paths to the given path.

    See `ITraversalAPI` for details.
    """

    if not args:
        return path
    if path != '/' and path.endswith('/'):
        raise ValueError('path must not end with a "/": %s' % path)
    if path != '/':
        path += '/'
    for arg in args:
        if arg.startswith('/') or arg.endswith('/'):
            raise ValueError("Leading or trailing slashes in path elements")
    return _normalizePath(path + '/'.join(args))


def getPath(obj):
    """
    Returns a string representing the physical path to the object.

    See `ITraversalAPI` for details.
    """
    return ILocationInfo(obj).getPath()


def getRoot(obj):
    """
    Returns the root of the traversal for the given object.

    See `ITraversalAPI` for details.
    """
    return ILocationInfo(obj).getRoot()


def traverse(object, path, default=_marker, request=None):
    """
    Traverse *path* relative to the given object.

    See `ITraversalAPI` for details.
    """
    traverser = ITraverser(object)
    if default is _marker:
        return traverser.traverse(path, request=request)
    return traverser.traverse(path, default=default, request=request)


def traverseName(obj, name, default=_marker, traversable=None, request=None):
    """
    Traverse a single step 'name' relative to the given object.

    See `ITraversalAPI` for details.
    """
    further_path = []
    if default is _marker:
        obj = traversePathElement(obj, name, further_path,
                                  traversable=traversable, request=request)
    else:
        obj = traversePathElement(obj, name, further_path, default=default,
                                  traversable=traversable, request=request)
    if further_path:
        raise NotImplementedError('further_path returned from traverse')

    return obj


def getName(obj):
    """
    Get the name an object was traversed via.

    See `ITraversalAPI` for details.
    """
    return ILocationInfo(obj).getName()


def getParent(obj):
    """
    Returns the container the object was traversed via.

    See `ITraversalAPI` for details.
    """
    try:
        location_info = ILocationInfo(obj)
    except TypeError:
        pass
    else:
        return location_info.getParent()

    # XXX Keep the old implementation as the fallback behaviour in the case
    # that obj doesn't have a location parent. This seems advisable as the
    # 'parent' is sometimes taken to mean the traversal parent, and the
    # __parent__ attribute is used for both.

    if IRoot.providedBy(obj):
        return None

    parent = getattr(obj, '__parent__', None)
    if parent is not None:
        return parent

    raise TypeError("Not enough context information to get parent", obj)


def getParents(obj):
    """
    Returns a list starting with the given object's parent followed by
    each of its parents.

    See `ITraversalAPI` for details.
    """
    return ILocationInfo(obj).getParents()


def _normalizePath(path):
    """Normalize a path by resolving '.' and '..' path elements."""

    # Special case for the root path.
    if path == '/':
        return path

    new_segments = []
    prefix = ''
    if path.startswith('/'):
        prefix = '/'
        path = path[1:]

    for segment in path.split('/'):
        if segment == '.':
            continue
        if segment == '..':
            new_segments.pop()  # raises IndexError if there is nothing to pop
            continue
        if not segment:
            raise ValueError('path must not contain empty segments: %s'
                             % path)
        new_segments.append(segment)

    return prefix + '/'.join(new_segments)


def canonicalPath(path_or_object):
    """
    Returns a canonical absolute unicode path for the given path or
    object.

    See `ITraversalAPI` for details.
    """
    if isinstance(path_or_object, str):
        path = path_or_object
        if not path:
            raise ValueError("path must be non-empty: %s" % path)
    else:
        path = getPath(path_or_object)

    path = '' + path

    # Special case for the root path.
    if path == '/':
        return path

    if path[0] != '/':
        raise ValueError('canonical path must start with a "/": %s' % path)
    if path[-1] == '/':
        raise ValueError('path must not end with a "/": %s' % path)

    # Break path into segments. Process '.' and '..' segments.
    return _normalizePath(path)


# Synchronize the documentation.
for name in ITraversalAPI.names():
    if name in globals():
        globals()[name].__doc__ = ITraversalAPI[name].__doc__
del name
