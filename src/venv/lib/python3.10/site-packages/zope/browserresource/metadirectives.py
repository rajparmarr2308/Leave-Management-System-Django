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
"""ZCML directives for defining browser resources
"""
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.interface import Interface
from zope.schema import Int
from zope.schema import TextLine
from zope.security.zcml import Permission


class IBasicResourceInformation(Interface):
    """
    This is the basic information for all browser resources.
    """

    layer = GlobalInterface(
        title="The layer the resource should be found in",
        description="""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False
    )

    permission = Permission(
        title="The permission needed to access the resource.",
        description="""
        If a permission isn't specified, the resource will always be
        accessible.""",
        required=False
    )


class IResourceDirective(IBasicResourceInformation):
    """
    Defines a browser resource.

    .. seealso:: `.FileResourceFactory`
    """

    name = TextLine(
        title="The name of the resource",
        description="""
        This is the name used in resource urls. Resource urls are of
        the form ``<site>/@@/resourcename``, where ``<site>`` is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True
    )

    factory = GlobalObject(
        title="Resource Factory",
        description="The factory used to create the resource. The factory "
                    "should only expect to get the request passed when "
                    "called.",
        required=False
    )

    file = Path(
        title="File",
        description="The file containing the resource data. The resource "
                    "type that will be created depends on file extension. "
                    "The named IResourceFactoryFactory utilities are "
                    "registered per extension. If no factory is registered "
                    "for given file extension, the default FileResource "
                    "factory will be used.",
        required=False
    )

    image = Path(
        title="Image",
        description="""
        If the image attribute is used, then an image resource, rather
        than a file resource will be created.

        This attribute is deprecated in favor of pluggable resource types,
        registered per extension. Use the "file" attribute instead.
        """,
        required=False
    )

    template = Path(
        title="Template",
        description="""
        If the template attribute is used, then a page template resource,
        rather than a file resource will be created.

        This attribute is deprecated in favor of pluggable resource types,
        registered per extension. Use the "file" attribute instead. To
        use page template resources, you need to install zope.ptresource
        package.
        """,
        required=False
    )


class II18nResourceDirective(IBasicResourceInformation):
    """
    Defines an i18n'd resource.
    """

    name = TextLine(
        title="The name of the resource",
        description="""
        This is the name used in resource urls. Resource urls are of
        the form ``<site>/@@/resourcename``, where ``<site>`` is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True
    )

    defaultLanguage = TextLine(
        title="Default language",
        description="Defines the default language",
        required=False
    )


class II18nResourceTranslationSubdirective(IBasicResourceInformation):
    """
    Subdirective to `II18nResourceDirective`.
    """

    language = TextLine(
        title="Language",
        description="Language of this translation of the resource",
        required=True
    )

    file = Path(
        title="File",
        description="The file containing the resource data.",
        required=False
    )

    image = Path(
        title="Image",
        description="""
        If the image attribute is used, then an image resource, rather
        than a file resource will be created.

        This attribute is deprecated, as images are now simply files.
        Use the "file" attribute instead.
        """,
        required=False
    )


class IResourceDirectoryDirective(IBasicResourceInformation):
    """
    Defines a directory containing browser resources.

    .. seealso:: `.DirectoryResource`
    """

    name = TextLine(
        title="The name of the resource",
        description="""
        This is the name used in resource urls. Resource urls are of
        the form ``<site>/@@/resourcename``, where ``<site>`` is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True
    )

    directory = Path(
        title="Directory",
        description="The directory containing the resource data.",
        required=True
    )


class IIconDirective(Interface):
    """
    Define an icon for an interface.
    """

    name = TextLine(
        title="The name of the icon.",
        description="The name shows up in URLs/paths. For example 'foo'.",
        required=True
    )

    for_ = GlobalInterface(
        title="The interface this icon is for.",
        description="""
        The icon will be for all objects that implement this
        interface.""",
        required=True
    )

    file = Path(
        title="File",
        description="The file containing the icon.",
        required=False
    )

    resource = TextLine(
        title="Resource",
        description="A resource containing the icon.",
        required=False
    )

    title = MessageID(
        title="Title",
        description="Descriptive title",
        required=False
    )

    layer = GlobalInterface(
        title="The layer the icon should be found in",
        description="""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False
    )

    width = Int(
        title="The width of the icon.",
        description="""
        The width will be used for the <img width="..." />
        attribute. Defaults to 16.""",
        required=False,
        default=16
    )

    height = Int(
        title="The height of the icon.",
        description="""
        The height will be used for the <img height="..." />
        attribute. Defaults to 16.""",
        required=False,
        default=16
    )
