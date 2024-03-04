#############################################################################
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
"""ZCML directives for defining browser pages
"""
from zope.component.zcml import IBasicViewInformation
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.interface import Interface
from zope.schema import TextLine
from zope.security.zcml import Permission


try:
    from zope.browsermenu.field import MenuField
except ImportError:  # pragma: no cover
    # avoid hard dependency on zope.browsermenu
    MenuField = TextLine


class IPagesDirective(IBasicViewInformation):
    """
    Define multiple pages without repeating all of the parameters.

    The pages directive allows multiple page views to be defined
    without repeating the 'for', 'permission', 'class', 'layer',
    'allowed_attributes', and 'allowed_interface' attributes.
    """

    for_ = GlobalObject(
        title="The interface or class this view is for.",
        required=False
    )

    layer = GlobalObject(
        title="The request interface or class this view is for.",
        description="Defaults to "
                    "zope.publisher.interfaces.browser.IDefaultBrowserLayer.",
        required=False
    )

    permission = Permission(
        title="Permission",
        description="The permission needed to use the view.",
        required=True
    )


class IViewDirective(IPagesDirective):
    """
    The view directive defines a view that has subpages.

    The pages provided by the defined view are accessed by first
    traversing to the view name and then traversing to the page name.
    """

    for_ = GlobalInterface(
        title="The interface this view is for.",
        required=False
    )

    name = TextLine(
        title="The name of the view.",
        description="The name shows up in URLs/paths. For example 'foo'.",
        required=False,
        default='',
    )

    menu = MenuField(
        title="The browser menu to include the page (view) in.",
        description="""
          Many views are included in menus. It's convenient to name
          the menu in the page directive, rather than having to give a
          separate menuItem directive.  'zmi_views' is the menu most often
          used in the Zope management interface.

          This attribute will only work if zope.browsermenu is installed.
          """,
        required=False
    )

    title = MessageID(
        title="The browser menu label for the page (view)",
        description="""
          This attribute must be supplied if a menu attribute is
          supplied.

          This attribute will only work if zope.browsermenu is installed.
          """,
        required=False
    )

    provides = GlobalInterface(
        title="The interface this view provides.",
        description="""
        A view can provide an interface.  This would be used for
        views that support other views.""",
        required=False,
        default=Interface,
    )


class IViewPageSubdirective(Interface):
    """
    Subdirective to IViewDirective.
    """

    name = TextLine(
        title="The name of the page (view)",
        description="""
        The name shows up in URLs/paths. For example 'foo' or
        'foo.html'. This attribute is required unless you use the
        subdirective 'page' to create sub views. If you do not have
        sub pages, it is common to use an extension for the view name
        such as '.html'. If you do have sub pages and you want to
        provide a view name, you shouldn't use extensions.""",
        required=True
    )

    attribute = PythonIdentifier(
        title="The name of the view attribute implementing the page.",
        description="""
        This refers to the attribute (method) on the view that is
        implementing a specific sub page.""",
        required=False
    )

    template = Path(
        title="The name of a template that implements the page.",
        description="""
        Refers to a file containing a page template (should end in
        extension '.pt' or '.html').""",
        required=False
    )


class IViewDefaultPageSubdirective(Interface):
    """
    Subdirective to IViewDirective.
    """

    name = TextLine(
        title="The name of the page that is the default.",
        description="""
        The named page will be used as the default if no name is
        specified explicitly in the path. If no defaultPage directive
        is supplied, the default page will be the first page
        listed.""",
        required=True
    )


class IPagesPageSubdirective(IViewPageSubdirective):
    """
    Subdirective to IPagesDirective
    """

    menu = MenuField(
        title="The browser menu to include the page (view) in.",
        description="""
        Many views are included in menus. It's convenient to name the
        menu in the page directive, rather than having to give a
        separate menuItem directive.

        This attribute will only work if zope.browsermenu is installed.
        """,
        required=False
    )

    title = MessageID(
        title="The browser menu label for the page (view)",
        description="""
        This attribute must be supplied if a menu attribute is
        supplied.

        This attribute will only work if zope.browsermenu is installed.
        """,
        required=False
    )


class IPageDirective(IPagesDirective, IPagesPageSubdirective):
    """
    The page directive is used to create views that provide a single
    url or page.

    The page directive creates a new view class from a given template
    and/or class and registers it.
    """


class IExpressionTypeDirective(Interface):
    """Register a new TALES expression type"""

    name = TextLine(
        title="Name",
        description="""Name of the expression. This will also be used
        as the prefix in actual TALES expressions.""",
        required=True
    )

    handler = GlobalObject(
        title="Handler",
        description="""Handler is class that implements
        zope.tales.interfaces.ITALESExpression.""",
        required=True
    )
