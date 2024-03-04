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
"""Site and Local Site Manager implementation

A local site manager has a number of roles:

  - A local site manager, that provides a local adapter and utility registry.

  - A place to do TTW development and/or to manage database-based code.

  - A registry for persistent modules.  The Zope 3 import hook uses the
    SiteManager to search for modules.
"""

import zope.component
import zope.component.hooks
import zope.component.interfaces
import zope.event
import zope.interface
import zope.lifecycleevent.interfaces
import zope.location
import zope.location.interfaces
from zope.component.hooks import setSite
from zope.component.interfaces import ISite
from zope.component.persistentregistry import PersistentAdapterRegistry
from zope.component.persistentregistry import PersistentComponents
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.deprecation import deprecated
from zope.filerepresentation.interfaces import IDirectoryFactory
from zope.interface.interfaces import ComponentLookupError
from zope.interface.interfaces import IComponentLookup
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location.interfaces import ILocationInfo
from zope.location.interfaces import IRoot

from zope.site import interfaces


# BBB. Remove in Version 5.0 including imports
setSite = deprecated(
    setSite,
    '``zope.site.site.setSite`` is deprecated '
    'and will be removed in zope.site Version 5.0. '
    'Use it from ``zope.component.hooks`` instead.')  # noqa


@zope.interface.implementer(interfaces.ISiteManagementFolder)
class SiteManagementFolder(BTreeContainer):
    """Implementation of a :class:`~.ISiteManagementFolder`"""


@zope.interface.implementer(IDirectoryFactory)
class SMFolderFactory:
    """
    Implementation of a :class:`~.IDirectoryFactory` that creates
    :class:`SiteManagementFolder`
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return SiteManagementFolder()


@zope.interface.implementer(zope.component.interfaces.IPossibleSite)
class SiteManagerContainer(Contained):
    """Implement access to the site manager (++etc++site).

    This is a mix-in that implements the :class:`~.IPossibleSite`
    interface; for example, it is used by the Folder implementation.
    """

    _sm = None

    def getSiteManager(self):
        if self._sm is not None:
            return self._sm
        raise ComponentLookupError('no site manager defined')

    def setSiteManager(self, sm):
        # pylint:disable=no-value-for-parameter
        if ISite.providedBy(self):
            raise TypeError("Already a site")

        if IComponentLookup.providedBy(sm):
            self._sm = sm
        else:
            raise ValueError('setSiteManager requires an IComponentLookup')

        zope.interface.directlyProvides(
            self, zope.component.interfaces.ISite,
            zope.interface.directlyProvidedBy(self))
        zope.event.notify(interfaces.NewLocalSite(sm))


def _findNextSiteManager(site):
    while True:
        if IRoot.providedBy(site):   # pylint:disable=no-value-for-parameter
            # we're the root site, return None
            return None

        try:
            # pylint:disable=no-value-for-parameter, too-many-function-args
            # pylint:disable=assignment-from-no-return
            site = ILocationInfo(site).getParent()
        except TypeError:
            # there was not enough context; probably run from a test
            return None

        if ISite.providedBy(site):  # pylint:disable=no-value-for-parameter
            return site.getSiteManager()


class _LocalAdapterRegistry(
        PersistentAdapterRegistry,
        zope.location.Location,
):
    pass


@zope.interface.implementer(interfaces.ILocalSiteManager)
class LocalSiteManager(BTreeContainer,
                       PersistentComponents):
    """Local Site Manager (:class:`~.ILocalSiteManager`) implementation"""

    subs = ()

    def _setBases(self, bases):

        # Update base subs
        for base in self.__bases__:
            if ((base not in bases)  # pragma: no cover
                    # pylint:disable=no-value-for-parameter
                    and interfaces.ILocalSiteManager.providedBy(base)):
                base.removeSub(self)

        for base in bases:
            if ((base not in self.__bases__)
                    # pylint:disable=no-value-for-parameter
                    and interfaces.ILocalSiteManager.providedBy(base)):
                base.addSub(self)

        super()._setBases(bases)

    def __init__(self, site, default_folder=True):
        BTreeContainer.__init__(self)
        PersistentComponents.__init__(self)

        # Locate the site manager
        self.__parent__ = site
        self.__name__ = '++etc++site'

        # Set base site manager
        next_sm = _findNextSiteManager(site)
        if next_sm is None:
            next_sm = zope.component.getGlobalSiteManager()
        self.__bases__ = (next_sm, )

        # Setup default site management folder if requested
        if default_folder:
            folder = SiteManagementFolder()
            zope.event.notify(ObjectCreatedEvent(folder))
            self['default'] = folder

    def _init_registries(self):
        self.adapters = _LocalAdapterRegistry()
        self.utilities = _LocalAdapterRegistry()
        self.adapters.__parent__ = self.utilities.__parent__ = self
        self.adapters.__name__ = 'adapters'
        self.utilities.__name__ = 'utilities'

    def _p_repr(self):
        return PersistentComponents.__repr__(self)

    def addSub(self, sub):
        """See :meth:`zope.site.interfaces.ILocalSiteManager.addSub`"""
        self.subs += (sub, )

    def removeSub(self, sub):
        """See :meth:`zope.site.interfaces.ILocalSiteManager.removeSub`"""
        self.subs = tuple(
            [s for s in self.subs if s is not sub])


def threadSiteSubscriber(ob, event):
    """A multi-subscriber to `zope.component.interfaces.ISite` and
    `zope.traversing.interfaces.BeforeTraverseEvent`.

    Sets the 'site' thread global if the object traversed is a site.

    .. note::

       The ``configure.zcml`` included in this package does
       *not* install this subscriber. That must be configured separately.
       ``zope.app.publication`` includes such configuration.
    """
    zope.component.hooks.setSite(ob)


def clearThreadSiteSubscriber(event):
    """A subscriber to `zope.publisher.interfaces.EndRequestEvent`

    Cleans up the site thread global after the request is processed.

    .. note::

        The ``configure.zcml`` included in this package does *not*
        install this subscriber. That must be configured separately.
        ``zope.app.publication`` includes such configuration.
    """
    clearSite()


# Clear the site thread global
clearSite = zope.component.hooks.setSite
try:
    from zope.testing.cleanup import addCleanUp
except ImportError:  # pragma: no cover
    pass
else:
    addCleanUp(clearSite)


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(IComponentLookup)
def SiteManagerAdapter(ob):
    """An adapter from :class:`~.ILocation` to :class:`~.IComponentLookup`.

    The ILocation is interpreted flexibly, we just check for
    ``__parent__``.
    """
    current = ob
    while True:
        if ISite.providedBy(current):  # pylint:disable=no-value-for-parameter
            return current.getSiteManager()
        current = getattr(current, '__parent__', None)
        if current is None:
            # It is not a location or has no parent, so we return the global
            # site manager
            return zope.component.getGlobalSiteManager()


def changeSiteConfigurationAfterMove(site, event):
    """
    After a site is (re-)moved, its site manager links have to be
    updated.

    Subscriber to :class:`~.ISite` objects in a :class:`~.IObjectMovedEvent`.
    """
    local_sm = site.getSiteManager()
    if event.newParent is not None:
        next_sm = _findNextSiteManager(site)
        if next_sm is None:
            next_sm = zope.component.getGlobalSiteManager()
        local_sm.__bases__ = (next_sm, )
    else:
        local_sm.__bases__ = ()


@zope.component.adapter(
    SiteManagerContainer,
    zope.lifecycleevent.interfaces.IObjectMovedEvent)
def siteManagerContainerRemoved(container, event):
    # The relation between SiteManagerContainer and LocalSiteManager is a
    # kind of containment hierarchy, but it is not expressed via containment,
    # but rather via an attribute (_sm).
    #
    # When the parent is deleted, this needs to be propagated to the children,
    # and since we don't have "real" containment, we need to do that manually.

    try:
        sm = container.getSiteManager()
    except ComponentLookupError:
        pass
    else:
        zope.component.handle(sm, event)
