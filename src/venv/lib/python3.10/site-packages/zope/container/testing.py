##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Unit test logic for setting up and tearing down basic infrastructure
"""
import zope.interface
import zope.traversing.testing
from zope.component.eventtesting import PlacelessSetup as EventPlacelessSetup
from zope.component.testing import PlacelessSetup as CAPlacelessSetup
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.interfaces import ITraversable

from zope import component
from zope.container.contained import NameChooser
from zope.container.interfaces import INameChooser
from zope.container.interfaces import ISimpleReadContainer
from zope.container.interfaces import IWriteContainer
from zope.container.sample import SampleContainer
from zope.container.traversal import ContainerTraversable


# XXX we would like to swap the names of the *PlacelessSetup classes
# in here as that would seem to follow the convention better, but
# unfortunately that would break compatibility with zope.app.testing
# (which expects this PlacelessSetup) so it will have to wait.

class PlacelessSetup:

    def setUp(self):
        component.provideAdapter(NameChooser, (IWriteContainer,), INameChooser)


class ContainerPlacelessSetup(CAPlacelessSetup,
                              EventPlacelessSetup,
                              PlacelessSetup):

    def setUp(self, doctesttest=None):
        CAPlacelessSetup.setUp(self)
        EventPlacelessSetup.setUp(self)
        PlacelessSetup.setUp(self)


ps = ContainerPlacelessSetup()
setUp = ps.setUp


def tearDown():
    # `ps` is actually defined at the time this function is executed:
    tearDown_ = ps.tearDown  # noqa: F821 undefined name 'ps'

    def tearDown(doctesttest=None):
        tearDown_()
    return tearDown


tearDown = tearDown()

del ps


class ContainerPlacefulSetup(ContainerPlacelessSetup):
    def setUp(self, doctesttest=None):
        ContainerPlacelessSetup.setUp(self, doctesttest)
        zope.traversing.testing.setUp()
        component.provideAdapter(ContainerTraversable,
                                 (ISimpleReadContainer,), ITraversable)

    def tearDown(self, docttesttest=None):
        ContainerPlacelessSetup.tearDown(self)

    def buildFolders(self):
        root = self.rootFolder = SampleContainer()
        zope.interface.directlyProvides(root, IContainmentRoot)
        root['folder1'] = SampleContainer()
        root['folder1']['folder1_1'] = SampleContainer()
        root['folder1']['folder1_1']['folder1_1_1'] = SampleContainer()
        root['folder2'] = SampleContainer()
        root['folder2']['folder2_1'] = SampleContainer()
        root['folder2']['folder2_1']['folder2_1_1'] = SampleContainer()
