##############################################################################
#
# Copyright (c) 2001-2008 Zope Foundation and Contributors.
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
"""This module tests the regular persistent Translation Domain.
"""
import os
import unittest

import zope.component
from zope.i18nmessageid import MessageFactory

from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.testing import compile_po
from zope.i18n.tests.test_itranslationdomain import Environment
from zope.i18n.tests.test_itranslationdomain import TestITranslationDomain
from zope.i18n.translationdomain import TranslationDomain


testdir = os.path.dirname(__file__)
default_dir = os.path.join(testdir, 'locale-default')

en_file = os.path.join(default_dir, 'en', 'LC_MESSAGES', 'default.mo')
de_file = os.path.join(default_dir, 'de', 'LC_MESSAGES', 'default.mo')


class TestGlobalTranslationDomain(TestITranslationDomain, unittest.TestCase):

    def _getTranslationDomain(self):
        domain = TranslationDomain('default')
        compile_po(en_file)
        en_catalog = GettextMessageCatalog('en', 'default', en_file)
        compile_po(de_file)
        de_catalog = GettextMessageCatalog('de', 'default', de_file)
        domain.addCatalog(en_catalog)
        domain.addCatalog(de_catalog)
        return domain

    def testNoTargetLanguage(self):
        # Having a fallback would interfere with this test
        self._domain.setLanguageFallbacks([])
        TestITranslationDomain.testNoTargetLanguage(self)

    def testSimpleNoTranslate(self):
        translate = self._domain.translate
        eq = self.assertEqual
        # Unset fallback translation languages
        self._domain.setLanguageFallbacks([])

        # Test that a translation in an unsupported language returns the
        # default, if there is no fallback language
        eq(translate('short_greeting', target_language='es'), 'short_greeting')
        eq(translate('short_greeting', target_language='es',
                     default='short_greeting'), 'short_greeting')

        # Same test, but use the context argument instead of target_language
        context = Environment()
        eq(translate('short_greeting', context=context), 'short_greeting')
        eq(translate('short_greeting', context=context,
                     default='short_greeting'), 'short_greeting')

    def testEmptyStringTranslate(self):
        translate = self._domain.translate
        self.assertEqual(translate("", target_language='en'), "")
        self.assertEqual(translate("", target_language='foo'), "")

    def testStringTranslate(self):
        self.assertEqual(
            self._domain.translate("short_greeting", target_language='en'),
            "Hello!")

    def testMessageIDTranslate(self):
        factory = MessageFactory('default')
        translate = self._domain.translate
        msgid = factory("short_greeting", 'default')
        self.assertEqual(translate(msgid, target_language='en'), "Hello!")
        # MessageID attributes override arguments
        msgid = factory('43-not-there', 'this ${that} the other',
                        mapping={'that': 'THAT'})
        self.assertEqual(
            translate(msgid, target_language='en', default="default",
                      mapping={"that": "that"}), "this THAT the other")

    def testMessageIDRecursiveTranslate(self):
        factory = MessageFactory('default')
        translate = self._domain.translate
        msgid_sub1 = factory("44-not-there", '${blue}',
                             mapping={'blue': 'BLUE'})
        msgid_sub2 = factory("45-not-there", '${yellow}',
                             mapping={'yellow': 'YELLOW'})
        mapping = {'color1': msgid_sub1,
                   'color2': msgid_sub2}
        msgid = factory("46-not-there", 'Color: ${color1}/${color2}',
                        mapping=mapping)
        self.assertEqual(
            translate(msgid, target_language='en', default="default"),
            "Color: BLUE/YELLOW")
        # The recursive translation must not change the mappings
        self.assertEqual(msgid.mapping, {'color1': msgid_sub1,
                                         'color2': msgid_sub2})
        # A circular reference should not lead to crashes
        msgid1 = factory("47-not-there", 'Message 1 and $msg2',
                         mapping={})
        msgid2 = factory("48-not-there", 'Message 2 and $msg1',
                         mapping={})
        msgid1.mapping['msg2'] = msgid2
        msgid2.mapping['msg1'] = msgid1
        self.assertRaises(ValueError,
                          translate, msgid1, None, None, 'en', "default")
        # Recursive translations also work if the original message id wasn't a
        # message id but a Unicode with a directly passed mapping
        self.assertEqual(
            "Color: BLUE/YELLOW",
            translate("Color: ${color1}/${color2}", mapping=mapping,
                      target_language='en'))

        # If we have mapping with a message id from a different
        # domain, make sure we use that domain, not ours. If the
        # message domain is not registered yet, we should return a
        # default translation.
        alt_factory = MessageFactory('alt')
        msgid_sub = alt_factory("special", default="oohhh")
        mapping = {'message': msgid_sub}
        msgid = factory("46-not-there", 'Message: ${message}',
                        mapping=mapping)
        # test we get a default with no domain registered
        self.assertEqual(
            translate(msgid, target_language='en', default="default"),
            "Message: oohhh")
        # provide the domain
        domain = TranslationDomain('alt')
        path = testdir
        en_alt_path = os.path.join(
            path, 'locale-alt', 'en', 'LC_MESSAGES', 'alt.mo')
        compile_po(en_alt_path)
        en_catalog = GettextMessageCatalog('en', 'alt', en_alt_path)
        domain.addCatalog(en_catalog)
        # test that we get the right translation
        zope.component.provideUtility(domain, ITranslationDomain, 'alt')
        self.assertEqual(
            translate(msgid, target_language='en', default="default"),
            "Message: Wow")

    def testMessageIDTranslateForDifferentDomain(self):
        domain = TranslationDomain('alt')
        path = testdir
        en_alt_path = os.path.join(
            path, 'locale-alt', 'en', 'LC_MESSAGES', 'alt.mo')
        compile_po(en_alt_path)
        en_catalog = GettextMessageCatalog('en', 'alt', en_alt_path)
        domain.addCatalog(en_catalog)

        zope.component.provideUtility(domain, ITranslationDomain, 'alt')

        factory = MessageFactory('alt')
        msgid = factory("special", 'default')
        self.assertEqual(
            self._domain.translate(msgid, target_language='en'), "Wow")

    def testSimpleFallbackTranslation(self):
        translate = self._domain.translate
        eq = self.assertEqual
        # Test that a translation in an unsupported language returns a
        # translation in the fallback language (by default, English)
        eq(translate('short_greeting', target_language='es'),
           "Hello!")
        # Same test, but use the context argument instead of target_language
        context = Environment()
        eq(translate('short_greeting', context=context),
           "Hello!")

    def testInterpolationWithoutTranslation(self):
        translate = self._domain.translate
        self.assertEqual(
            translate('42-not-there', target_language="en",
                      default="this ${that} the other",
                      mapping={"that": "THAT"}),
            "this THAT the other")

    def test_getCatalogInfos(self):
        cats = self._domain.getCatalogsInfo()
        self.assertEqual(
            cats,
            {'en': [en_file],
             'de': [de_file]})

    def test_releoadCatalogs(self):
        # It uses the keys we pass
        # so this does nothing
        self._domain.reloadCatalogs(())

        # The catalogNames, somewhat confusingly, are
        # the paths to the files.
        self._domain.reloadCatalogs((en_file, de_file))

        with self.assertRaises(KeyError):
            self._domain.reloadCatalogs(('dne',))

    def test_character_sets(self):
        """Test two character sets for the same language.

        Serbian can be written in Latin or Cyrillic,
        where Latin is currently most used.
        Interestingly, every Latin character can actually be mapped to
        one Cyrillic character, and the other way around,
        so you could write a script to turn one po-file into the other.

        But most practical is to have two locales with names
        sr@Latn and sr@Cyrl.  These are then two character sets
        for the same language.  So they should end up together
        under the same language in a translation domain.

        The best way for an integrator to choose which one to use,
        is to add an environment variable 'zope_i18n_allowed_languages'
        and let this contain either sr@Latn or sr@Cyrl.

        See https://github.com/collective/plone.app.locales/issues/326
        """
        standard_file = os.path.join(
            default_dir, 'sr', 'LC_MESSAGES', 'default.mo')
        latin_file = os.path.join(
            default_dir, 'sr@Latn', 'LC_MESSAGES', 'default.mo')
        cyrillic_file = os.path.join(
            default_dir, 'sr@Cyrl', 'LC_MESSAGES', 'default.mo')
        compile_po(standard_file)
        standard_catalog = GettextMessageCatalog('sr', 'char', standard_file)
        compile_po(latin_file)
        latin_catalog = GettextMessageCatalog('sr@Latn', 'char', latin_file)
        compile_po(cyrillic_file)
        cyrillic_catalog = GettextMessageCatalog(
            'sr@Cyrl', 'char', cyrillic_file)

        # Test the standard file.
        domain = TranslationDomain('char')
        domain.addCatalog(standard_catalog)
        self.assertEqual(
            domain.translate('short_greeting', target_language='sr'),
            "Hello in Serbian Standard!",
        )

        # Test the Latin file.
        domain = TranslationDomain('char')
        domain.addCatalog(latin_catalog)
        self.assertEqual(
            domain.translate('short_greeting', target_language='sr'),
            "Hello in Serbian Latin!",
        )
        # Note that sr@Latn is not recognizes as language id.
        self.assertEqual(
            domain.translate('short_greeting', target_language='sr@Latn'),
            "short_greeting",
        )

        # Test the Cyrillic file.
        domain = TranslationDomain('char')
        domain.addCatalog(cyrillic_catalog)
        self.assertEqual(
            domain.translate('short_greeting', target_language='sr'),
            "Hello in српски!",
        )

        # When I have all three locales, this is the order that
        # os.listdir gives them in:
        domain = TranslationDomain('char')
        domain.addCatalog(latin_catalog)
        domain.addCatalog(cyrillic_catalog)
        domain.addCatalog(standard_catalog)
        # The Latin one is first, so it wins.
        self.assertEqual(
            domain.translate('short_greeting', target_language='sr'),
            "Hello in Serbian Latin!",
        )
