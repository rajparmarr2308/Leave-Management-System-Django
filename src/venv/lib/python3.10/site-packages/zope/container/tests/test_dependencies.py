import unittest

from zope.configuration.xmlconfig import XMLConfig
from zope.interface import implementer
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.container.interfaces import IItemContainer
from zope.container.interfaces import ISimpleReadContainer
from zope.container.testing import ContainerPlacelessSetup
from zope.container.traversal import ItemTraverser


class ZCMLDependencies(ContainerPlacelessSetup, unittest.TestCase):

    def test_zcml_can_load(self):
        # this is just an example.  It is supposed to show that the
        # configure.zcml file has loaded successfully.

        import zope.container
        XMLConfig('configure.zcml', zope.container)()

        request = TestRequest()

        @implementer(IItemContainer)
        class SampleItemContainer:
            pass

        sampleitemcontainer = SampleItemContainer()
        res = zope.component.getMultiAdapter(
            (sampleitemcontainer, request), IBrowserPublisher)
        self.assertTrue(isinstance(res, ItemTraverser))
        self.assertTrue(res.context is sampleitemcontainer)

        @implementer(ISimpleReadContainer)
        class SampleSimpleReadContainer:
            pass

        samplesimplereadcontainer = SampleSimpleReadContainer()
        res = zope.component.getMultiAdapter(
            (samplesimplereadcontainer, request), IBrowserPublisher)
        self.assertTrue(isinstance(res, ItemTraverser))
        self.assertTrue(res.context is samplesimplereadcontainer)
