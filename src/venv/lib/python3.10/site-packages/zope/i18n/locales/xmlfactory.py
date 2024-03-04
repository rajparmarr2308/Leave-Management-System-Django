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
"""XML Locale-related objects and functions
"""
from datetime import date
from datetime import time
from xml.dom.minidom import parse as parseXML

from zope.i18n.locales import Locale
from zope.i18n.locales import LocaleCalendar
from zope.i18n.locales import LocaleCurrency
from zope.i18n.locales import LocaleDates
from zope.i18n.locales import LocaleDayContext
from zope.i18n.locales import LocaleDisplayNames
from zope.i18n.locales import LocaleFormat
from zope.i18n.locales import LocaleFormatLength
from zope.i18n.locales import LocaleIdentity
from zope.i18n.locales import LocaleMonthContext
from zope.i18n.locales import LocaleNumbers
from zope.i18n.locales import LocaleOrientation
from zope.i18n.locales import LocaleTimeZone
from zope.i18n.locales import LocaleVersion
from zope.i18n.locales import calendarAliases
from zope.i18n.locales import dayMapping
from zope.i18n.locales.inheritance import InheritingDictionary


class LocaleFactory:
    """This class creates a Locale object from an ICU XML file."""

    def __init__(self, path):
        """Initialize factory."""
        self._path = path
        # Mainly for testing
        if path:
            self._data = parseXML(path).documentElement

    def _getText(self, nodelist):
        rc = ''
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def _extractVersion(self, identity_node):
        """Extract the Locale's version info based on data from the DOM
        tree.

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <identity>
          ...   <version number="1.0">Some notes</version>
          ...   <generation date="2003-12-19" />
          ...   <language type="de" />
          ...   <territory type="DE" />
          ... </identity>'''
          >>> dom = parseString(xml)

          >>> version = factory._extractVersion(dom.documentElement)
          >>> version.number
          '1.0'
          >>> version.generationDate
          datetime.date(2003, 12, 19)
          >>> version.notes
          'Some notes'
        """
        number = generationDate = notes = None
        # Retrieve the version number and notes of the locale
        nodes = identity_node.getElementsByTagName('version')
        if nodes:
            number = nodes[0].getAttribute('number')
            notes = self._getText(nodes[0].childNodes)
        # Retrieve the generationDate of the locale
        nodes = identity_node.getElementsByTagName('generation')
        if nodes:
            year, month, day = nodes[0].getAttribute('date').split('-')
            generationDate = date(int(year), int(month), int(day))

        return LocaleVersion(number, generationDate, notes)

    def _extractIdentity(self):
        """Extract the Locale's identity object based on info from the DOM
        tree.

        Example::

          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <ldml>
          ...   <identity>
          ...     <version number="1.0"/>
          ...     <generation date="2003-12-19" />
          ...     <language type="en" />
          ...     <territory type="US" />
          ...     <variant type="POSIX" />
          ...   </identity>
          ... </ldml>'''
          >>> factory = LocaleFactory(None)
          >>> factory._data = parseString(xml).documentElement

          >>> id = factory._extractIdentity()
          >>> id.language
          'en'
          >>> id.script is None
          True
          >>> id.territory
          'US'
          >>> id.variant
          'POSIX'
          >>> id.version.number
          '1.0'
        """
        id = LocaleIdentity()
        identity = self._data.getElementsByTagName('identity')[0]
        # Retrieve the language of the locale
        nodes = identity.getElementsByTagName('language')
        if nodes != []:
            id.language = nodes[0].getAttribute('type') or None
        # Retrieve the territory of the locale
        nodes = identity.getElementsByTagName('territory')
        if nodes != []:
            id.territory = nodes[0].getAttribute('type') or None
        # Retrieve the varriant of the locale
        nodes = identity.getElementsByTagName('variant')
        if nodes != []:
            id.variant = nodes[0].getAttribute('type') or None

        id.version = self._extractVersion(identity)
        return id

    def _extractTypes(self, names_node):
        """Extract all types from the names_node.

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <displayNames>
          ...   <types>
          ...     <type type="Fallback" key="calendar"></type>
          ...     <type type="buddhist" key="calendar">BUDDHIST</type>
          ...     <type type="chinese" key="calendar">CHINESE</type>
          ...     <type type="gregorian" key="calendar">GREGORIAN</type>
          ...     <type type="stroke" key="collation">STROKE</type>
          ...     <type type="traditional" key="collation">TRADITIONAL</type>
          ...   </types>
          ... </displayNames>'''
          >>> dom = parseString(xml)

          >>> types = factory._extractTypes(dom.documentElement)
          >>> keys = types.keys()
          >>> keys.sort()
          >>> keys[:2]
          [('Fallback', 'calendar'), ('buddhist', 'calendar')]
          >>> keys[2:4]
          [('chinese', 'calendar'), ('gregorian', 'calendar')]
          >>> keys[4:]
          [('stroke', 'collation'), ('traditional', 'collation')]
          >>> types[('chinese', 'calendar')]
          'CHINESE'
          >>> types[('stroke', 'collation')]
          'STROKE'
        """
        # 'types' node has not to exist
        types_nodes = names_node.getElementsByTagName('types')
        if types_nodes == []:
            return
        # Retrieve all types
        types = InheritingDictionary()
        for type_node in types_nodes[0].getElementsByTagName('type'):
            type = type_node.getAttribute('type')
            key = type_node.getAttribute('key')
            types[(type, key)] = self._getText(type_node.childNodes)
        return types

    def _extractDisplayNames(self):
        """Extract all display names from the DOM tree.

        Example::

          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <ldml>
          ...   <localeDisplayNames>
          ...     <languages>
          ...       <language type="Fallback"></language>
          ...       <language type="aa">aa</language>
          ...       <language type="ab">ab</language>
          ...     </languages>
          ...     <scripts>
          ...       <script type="Arab">Arab</script>
          ...       <script type="Armn">Armn</script>
          ...     </scripts>
          ...     <territories>
          ...       <territory type="AD">AD</territory>
          ...       <territory type="AE">AE</territory>
          ...     </territories>
          ...     <variants>
          ...       <variant type="Fallback"></variant>
          ...       <variant type="POSIX">POSIX</variant>
          ...     </variants>
          ...     <keys>
          ...       <key type="calendar">CALENDAR</key>
          ...       <key type="collation">COLLATION</key>
          ...     </keys>
          ...     <types>
          ...       <type type="buddhist" key="calendar">BUDDHIST</type>
          ...       <type type="stroke" key="collation">STROKE</type>
          ...     </types>
          ...   </localeDisplayNames>
          ... </ldml>'''
          >>> factory = LocaleFactory(None)
          >>> factory._data = parseString(xml).documentElement

          >>> names = factory._extractDisplayNames()

          >>> keys = names.languages.keys()
          >>> keys.sort()
          >>> keys
          ['Fallback', 'aa', 'ab']
          >>> names.languages["aa"]
          'aa'

          >>> keys = names.scripts.keys()
          >>> keys.sort()
          >>> keys
          ['Arab', 'Armn']
          >>> names.scripts["Arab"]
          'Arab'

          >>> keys = names.territories.keys()
          >>> keys.sort()
          >>> keys
          ['AD', 'AE']
          >>> names.territories["AD"]
          'AD'

          >>> keys = names.variants.keys()
          >>> keys.sort()
          >>> keys
          ['Fallback', 'POSIX']
          >>> names.variants["Fallback"]
          ''

          >>> keys = names.keys.keys()
          >>> keys.sort()
          >>> keys
          ['calendar', 'collation']
          >>> names.keys["calendar"]
          'CALENDAR'

          >>> names.types[("stroke", "collation")]
          'STROKE'
        """
        displayNames = LocaleDisplayNames()
        # Neither the 'localeDisplayNames' or 'scripts' node has to exist
        names_nodes = self._data.getElementsByTagName('localeDisplayNames')
        if names_nodes == []:
            return displayNames

        for group_tag, single_tag in (('languages', 'language'),
                                      ('scripts', 'script'),
                                      ('territories', 'territory'),
                                      ('variants', 'variant'),
                                      ('keys', 'key')):
            group_nodes = names_nodes[0].getElementsByTagName(group_tag)
            if group_nodes == []:
                continue
            # Retrieve all children
            elements = InheritingDictionary()
            for element in group_nodes[0].getElementsByTagName(single_tag):
                type = element.getAttribute('type')
                elements[type] = self._getText(element.childNodes)
            setattr(displayNames, group_tag, elements)

        types = self._extractTypes(names_nodes[0])
        if types is not None:
            displayNames.types = types
        return displayNames

    def _extractMonths(self, months_node, calendar):
        """Extract all month entries from cal_node and store them in calendar.

        Example::

          >>> class CalendarStub(object):
          ...     months = None
          >>> calendar = CalendarStub()
          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <months>
          ...   <default type="format" />
          ...   <monthContext type="format">
          ...     <default type="wide" />
          ...     <monthWidth type="wide">
          ...       <month type="1">Januar</month>
          ...       <month type="2">Februar</month>
          ...       <month type="3">Maerz</month>
          ...       <month type="4">April</month>
          ...       <month type="5">Mai</month>
          ...       <month type="6">Juni</month>
          ...       <month type="7">Juli</month>
          ...       <month type="8">August</month>
          ...       <month type="9">September</month>
          ...       <month type="10">Oktober</month>
          ...       <month type="11">November</month>
          ...       <month type="12">Dezember</month>
          ...     </monthWidth>
          ...     <monthWidth type="abbreviated">
          ...       <month type="1">Jan</month>
          ...       <month type="2">Feb</month>
          ...       <month type="3">Mrz</month>
          ...       <month type="4">Apr</month>
          ...       <month type="5">Mai</month>
          ...       <month type="6">Jun</month>
          ...       <month type="7">Jul</month>
          ...       <month type="8">Aug</month>
          ...       <month type="9">Sep</month>
          ...       <month type="10">Okt</month>
          ...       <month type="11">Nov</month>
          ...       <month type="12">Dez</month>
          ...     </monthWidth>
          ...   </monthContext>
          ... </months>'''
          >>> dom = parseString(xml)
          >>> factory._extractMonths(dom.documentElement, calendar)

        The contexts and widths were introduced in CLDR 1.1, the way
        of getting month names is like this::

          >>> calendar.defaultMonthContext
          'format'

          >>> ctx = calendar.monthContexts["format"]
          >>> ctx.defaultWidth
          'wide'

          >>> names = [ctx.months["wide"][type] for type in range(1,13)]
          >>> names[:7]
          ['Januar', 'Februar', 'Maerz', 'April', 'Mai', 'Juni', 'Juli']
          >>> names[7:]
          ['August', 'September', 'Oktober', 'November', 'Dezember']

          >>> abbrs = [ctx.months["abbreviated"][type]
          ...     for type in range(1,13)]
          >>> abbrs[:6]
          ['Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun']
          >>> abbrs[6:]
          ['Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

        The old, CLDR 1.0 way of getting month names and abbreviations::

          >>> names = [calendar.months.get(type, (None, None))[0]
          ...          for type in range(1, 13)]
          >>> names[:7]
          ['Januar', 'Februar', 'Maerz', 'April', 'Mai', 'Juni', 'Juli']
          >>> names[7:]
          ['August', 'September', 'Oktober', 'November', 'Dezember']

          >>> abbrs = [calendar.months.get(type, (None, None))[1]
          ...          for type in range(1, 13)]
          >>> abbrs[:6]
          ['Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun']
          >>> abbrs[6:]
          ['Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

        If there are no months, nothing happens:

          >>> calendar = CalendarStub()
          >>> factory = LocaleFactory(None)
          >>> xml = '''<months><default type="format" /></months>'''
          >>> dom = parseString(xml)
          >>> factory._extractMonths(dom.documentElement, calendar)
          >>> calendar.months

        """

        defaultMonthContext_node = months_node.getElementsByTagName('default')
        if defaultMonthContext_node:
            calendar.defaultMonthContext = defaultMonthContext_node[
                0].getAttribute('type')

        monthContext_nodes = months_node.getElementsByTagName('monthContext')
        if not monthContext_nodes:
            return

        calendar.monthContexts = InheritingDictionary()
        names_node = abbrs_node = None  # BBB

        for node in monthContext_nodes:
            context_type = node.getAttribute('type')
            mctx = LocaleMonthContext(context_type)
            calendar.monthContexts[context_type] = mctx

            defaultWidth_node = node.getElementsByTagName('default')
            if defaultWidth_node:
                mctx.defaultWidth = defaultWidth_node[0].getAttribute('type')

            widths = InheritingDictionary()
            mctx.months = widths
            for width_node in node.getElementsByTagName('monthWidth'):
                width_type = width_node.getAttribute('type')
                width = InheritingDictionary()
                widths[width_type] = width

                for month_node in width_node.getElementsByTagName('month'):
                    mtype = int(month_node.getAttribute('type'))
                    width[mtype] = self._getText(month_node.childNodes)

                if context_type == 'format':
                    if width_type == 'abbreviated':
                        abbrs_node = width_node
                    elif width_type == 'wide':
                        names_node = width_node

        if not (names_node and abbrs_node):
            return

        # Get all month names
        names = {}
        for name_node in names_node.getElementsByTagName('month'):
            type = int(name_node.getAttribute('type'))
            names[type] = self._getText(name_node.childNodes)

        # Get all month abbrs
        abbrs = {}
        for abbr_node in abbrs_node.getElementsByTagName('month'):
            type = int(abbr_node.getAttribute('type'))
            abbrs[type] = self._getText(abbr_node.childNodes)

        # Put the info together
        calendar.months = InheritingDictionary()
        for type in range(1, 13):
            calendar.months[type] = (names.get(type, None),
                                     abbrs.get(type, None))

    def _extractDays(self, days_node, calendar):
        """Extract all day entries from cal_node and store them in
        calendar.

        Example::

          >>> class CalendarStub(object):
          ...     days = None
          >>> calendar = CalendarStub()
          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <days>
          ...   <default type="format" />
          ...   <dayContext type="format">
          ...     <default type="wide" />
          ...     <dayWidth type="wide">
          ...       <day type="sun">Sonntag</day>
          ...       <day type="mon">Montag</day>
          ...       <day type="tue">Dienstag</day>
          ...       <day type="wed">Mittwoch</day>
          ...       <day type="thu">Donnerstag</day>
          ...       <day type="fri">Freitag</day>
          ...       <day type="sat">Samstag</day>
          ...     </dayWidth>
          ...     <dayWidth type="abbreviated">
          ...       <day type="sun">So</day>
          ...       <day type="mon">Mo</day>
          ...       <day type="tue">Di</day>
          ...       <day type="wed">Mi</day>
          ...       <day type="thu">Do</day>
          ...       <day type="fri">Fr</day>
          ...       <day type="sat">Sa</day>
          ...     </dayWidth>
          ...   </dayContext>
          ... </days>'''
          >>> dom = parseString(xml)
          >>> factory._extractDays(dom.documentElement, calendar)

        Day contexts and widths were introduced in CLDR 1.1, here's
        how to use them::

          >>> calendar.defaultDayContext
          'format'

          >>> ctx = calendar.dayContexts["format"]
          >>> ctx.defaultWidth
          'wide'

          >>> names = [ctx.days["wide"][type] for type in range(1,8)]
          >>> names[:4]
          ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag']
          >>> names[4:]
          ['Freitag', 'Samstag', 'Sonntag']

          >>> abbrs = [ctx.days["abbreviated"][type] for type in range(1,8)]
          >>> abbrs
          ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

        And here's the old CLDR 1.0 way of getting day names and
        abbreviations::

          >>> names = [calendar.days.get(type, (None, None))[0]
          ...          for type in range(1, 8)]
          >>> names[:4]
          ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag']
          >>> names[4:]
          ['Freitag', 'Samstag', 'Sonntag']

          >>> abbrs = [calendar.days.get(type, (None, None))[1]
          ...          for type in range(1, 8)]
          >>> abbrs
          ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

        If there are no days, nothing happens:

          >>> calendar = CalendarStub()
          >>> factory = LocaleFactory(None)
          >>> xml = '''<days><default type="format" /></days>'''
          >>> dom = parseString(xml)
          >>> factory._extractDays(dom.documentElement, calendar)
          >>> calendar.days

        """

        defaultDayContext_node = days_node.getElementsByTagName('default')
        if defaultDayContext_node:
            calendar.defaultDayContext = defaultDayContext_node[
                0].getAttribute('type')

        dayContext_nodes = days_node.getElementsByTagName('dayContext')
        if not dayContext_nodes:
            return

        calendar.dayContexts = InheritingDictionary()
        names_node = abbrs_node = None  # BBB

        for node in dayContext_nodes:
            context_type = node.getAttribute('type')
            dctx = LocaleDayContext(context_type)
            calendar.dayContexts[context_type] = dctx

            defaultWidth_node = node.getElementsByTagName('default')
            if defaultWidth_node:
                dctx.defaultWidth = defaultWidth_node[0].getAttribute('type')

            widths = InheritingDictionary()
            dctx.days = widths
            for width_node in node.getElementsByTagName('dayWidth'):
                width_type = width_node.getAttribute('type')
                width = InheritingDictionary()
                widths[width_type] = width

                for day_node in width_node.getElementsByTagName('day'):
                    dtype = dayMapping[day_node.getAttribute('type')]
                    width[dtype] = self._getText(day_node.childNodes)

                if context_type == 'format':
                    if width_type == 'abbreviated':
                        abbrs_node = width_node
                    elif width_type == 'wide':
                        names_node = width_node

        if not (names_node and abbrs_node):
            return

        # Get all weekday names
        names = {}
        for name_node in names_node.getElementsByTagName('day'):
            type = dayMapping[name_node.getAttribute('type')]
            names[type] = self._getText(name_node.childNodes)
        # Get all weekday abbreviations
        abbrs = {}
        for abbr_node in abbrs_node.getElementsByTagName('day'):
            type = dayMapping[abbr_node.getAttribute('type')]
            abbrs[type] = self._getText(abbr_node.childNodes)

        # Put the info together
        calendar.days = InheritingDictionary()
        for type in range(1, 13):
            calendar.days[type] = (names.get(type, None),
                                   abbrs.get(type, None))

    def _extractWeek(self, cal_node, calendar):
        """Extract all week entries from cal_node and store them in
        calendar.

        Example::

          >>> class CalendarStub(object):
          ...     week = None
          >>> calendar = CalendarStub()
          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <calendar type="gregorian">
          ...   <week>
          ...     <minDays count="1"/>
          ...     <firstDay day="sun"/>
          ...     <weekendStart day="fri" time="18:00"/>
          ...     <weekendEnd day="sun" time="18:00"/>
          ...   </week>
          ... </calendar>'''
          >>> dom = parseString(xml)
          >>> factory._extractWeek(dom.documentElement, calendar)

          >>> calendar.week['minDays']
          1
          >>> calendar.week['firstDay']
          7
          >>> calendar.week['weekendStart']
          (5, datetime.time(18, 0))
          >>> calendar.week['weekendEnd']
          (7, datetime.time(18, 0))
        """
        # See whether we have week entries
        week_nodes = cal_node.getElementsByTagName('week')
        if not week_nodes:
            return

        calendar.week = InheritingDictionary()

        # Get the 'minDays' value if available
        for node in week_nodes[0].getElementsByTagName('minDays'):
            calendar.week['minDays'] = int(node.getAttribute('count'))

        # Get the 'firstDay' value if available
        for node in week_nodes[0].getElementsByTagName('firstDay'):
            calendar.week['firstDay'] = dayMapping[node.getAttribute('day')]

        # Get the 'weekendStart' value if available
        for node in week_nodes[0].getElementsByTagName('weekendStart'):
            day = dayMapping[node.getAttribute('day')]
            time_args = map(int, node.getAttribute('time').split(':'))
            calendar.week['weekendStart'] = (day, time(*time_args))

            # Get the 'weekendEnd' value if available
        for node in week_nodes[0].getElementsByTagName('weekendEnd'):
            day = dayMapping[node.getAttribute('day')]
            time_args = map(int, node.getAttribute('time').split(':'))
            calendar.week['weekendEnd'] = (day, time(*time_args))

    def _extractEras(self, cal_node, calendar):
        """Extract all era entries from cal_node and store them in
        calendar.

        Example::

          >>> class CalendarStub(object):
          ...     days = None
          >>> calendar = CalendarStub()
          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <calendar type="gregorian">
          ...   <eras>
          ...      <eraAbbr>
          ...       <era type="0">BC</era>
          ...       <era type="1">AD</era>
          ...      </eraAbbr>
          ...      <eraName>
          ...       <era type="0">Before Christ</era>
          ...      </eraName>
          ...   </eras>
          ... </calendar>'''
          >>> dom = parseString(xml)
          >>> factory._extractEras(dom.documentElement, calendar)

          >>> names = [calendar.eras.get(type, (None, None))[0]
          ...          for type in range(2)]
          >>> names
          ['Before Christ', None]

          >>> abbrs = [calendar.eras.get(type, (None, None))[1]
          ...          for type in range(2)]
          >>> abbrs
          ['BC', 'AD']
        """
        # See whether we have era names and abbreviations
        eras_nodes = cal_node.getElementsByTagName('eras')
        if not eras_nodes:
            return
        names_nodes = eras_nodes[0].getElementsByTagName('eraName')
        abbrs_nodes = eras_nodes[0].getElementsByTagName('eraAbbr')

        # Get all era names
        names = {}
        if names_nodes:
            for name_node in names_nodes[0].getElementsByTagName('era'):
                type = int(name_node.getAttribute('type'))
                names[type] = self._getText(name_node.childNodes)
        # Get all era abbreviations
        abbrs = {}
        if abbrs_nodes:
            for abbr_node in abbrs_nodes[0].getElementsByTagName('era'):
                type = int(abbr_node.getAttribute('type'))
                abbrs[type] = self._getText(abbr_node.childNodes)

        calendar.eras = InheritingDictionary()
        for type in abbrs.keys():
            calendar.eras[type] = (names.get(type, None),
                                   abbrs.get(type, None))

    def _extractFormats(self, formats_node, lengthNodeName, formatNodeName):
        """Extract all format entries from formats_node and return a
        tuple of the form (defaultFormatType, [LocaleFormatLength, ...]).

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <dateFormats>
          ...   <default type="medium"/>
          ...   <dateFormatLength type="full">
          ...     <dateFormat>
          ...       <pattern>EEEE, MMMM d, yyyy</pattern>
          ...     </dateFormat>
          ...   </dateFormatLength>
          ...   <dateFormatLength type="medium">
          ...     <default type="DateFormatsKey2"/>
          ...     <dateFormat type="DateFormatsKey2">
          ...       <displayName>Standard Date</displayName>
          ...       <pattern>MMM d, yyyy</pattern>
          ...     </dateFormat>
          ...     <dateFormat type="DateFormatsKey3">
          ...       <pattern>MMM dd, yyyy</pattern>
          ...     </dateFormat>
          ...   </dateFormatLength>
          ... </dateFormats>'''
          >>> dom = parseString(xml)

          >>> default, lengths = factory._extractFormats(
          ...     dom.documentElement, 'dateFormatLength', 'dateFormat')
          >>> default
          'medium'
          >>> lengths["full"].formats[None].pattern
          'EEEE, MMMM d, yyyy'
          >>> lengths["medium"].default
          'DateFormatsKey2'
          >>> lengths["medium"].formats['DateFormatsKey3'].pattern
          'MMM dd, yyyy'
          >>> lengths["medium"].formats['DateFormatsKey2'].displayName
          'Standard Date'
        """
        formats_default = None
        default_nodes = formats_node.getElementsByTagName('default')
        if default_nodes:
            formats_default = default_nodes[0].getAttribute('type')

        lengths = InheritingDictionary()
        for length_node in formats_node.getElementsByTagName(lengthNodeName):
            type = length_node.getAttribute('type') or None
            length = LocaleFormatLength(type)

            default_nodes = length_node.getElementsByTagName('default')
            if default_nodes:
                length.default = default_nodes[0].getAttribute('type')

            if length_node.getElementsByTagName(formatNodeName):
                length.formats = InheritingDictionary()

            for format_node in length_node.getElementsByTagName(
                    formatNodeName):
                format = LocaleFormat()
                format.type = format_node.getAttribute('type') or None
                pattern_node = format_node.getElementsByTagName('pattern')[0]
                format.pattern = self._getText(pattern_node.childNodes)
                name_nodes = format_node.getElementsByTagName('displayName')
                if name_nodes:
                    format.displayName = self._getText(
                        name_nodes[0].childNodes)
                length.formats[format.type] = format

            lengths[length.type] = length

        return (formats_default, lengths)

    def _extractCalendars(self, dates_node):
        """Extract all calendars and their specific information from the
        Locale's DOM tree.

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <dates>
          ...   <calendars>
          ...     <calendar type="gregorian">
          ...       <monthNames>
          ...         <month type="1">January</month>
          ...         <month type="12">December</month>
          ...       </monthNames>
          ...       <monthAbbr>
          ...         <month type="1">Jan</month>
          ...         <month type="12">Dec</month>
          ...       </monthAbbr>
          ...       <dayNames>
          ...         <day type="sun">Sunday</day>
          ...         <day type="sat">Saturday</day>
          ...       </dayNames>
          ...       <dayAbbr>
          ...         <day type="sun">Sun</day>
          ...         <day type="sat">Sat</day>
          ...       </dayAbbr>
          ...       <week>
          ...         <minDays count="1"/>
          ...         <firstDay day="sun"/>
          ...       </week>
          ...       <am>AM</am>
          ...       <pm>PM</pm>
          ...       <eras>
          ...         <eraAbbr>
          ...           <era type="0">BC</era>
          ...           <era type="1">AD</era>
          ...         </eraAbbr>
          ...       </eras>
          ...       <dateFormats>
          ...         <dateFormatLength type="full">
          ...           <dateFormat>
          ...             <pattern>EEEE, MMMM d, yyyy</pattern>
          ...           </dateFormat>
          ...         </dateFormatLength>
          ...       </dateFormats>
          ...       <timeFormats>
          ...         <default type="medium"/>
          ...         <timeFormatLength type="medium">
          ...           <timeFormat>
          ...             <pattern>h:mm:ss a</pattern>
          ...           </timeFormat>
          ...         </timeFormatLength>
          ...       </timeFormats>
          ...       <dateTimeFormats>
          ...         <dateTimeFormatLength>
          ...           <dateTimeFormat>
          ...             <pattern>{0} {1}</pattern>
          ...           </dateTimeFormat>
          ...         </dateTimeFormatLength>
          ...       </dateTimeFormats>
          ...     </calendar>
          ...     <calendar type="buddhist">
          ...       <eras>
          ...         <era type="0">BE</era>
          ...       </eras>
          ...     </calendar>
          ...   </calendars>
          ... </dates>'''
          >>> dom = parseString(xml)

          >>> calendars = factory._extractCalendars(dom.documentElement)
          >>> keys = calendars.keys()
          >>> keys.sort()
          >>> keys
          ['buddhist', 'gregorian', 'thai-buddhist']

        Note that "thai-buddhist" are added as an alias to "buddhist".

          >>> calendars['buddhist'] is calendars['thai-buddhist']
          True

        If there are no calendars, nothing happens:

           >>> xml = '''<dates />'''
           >>> dom = parseString(xml)
           >>> factory._extractCalendars(dom.documentElement)

        """
        cals_nodes = dates_node.getElementsByTagName('calendars')
        # no calendar node
        if cals_nodes == []:
            return None

        calendars = InheritingDictionary()
        for cal_node in cals_nodes[0].getElementsByTagName('calendar'):
            # get the calendar type
            type = cal_node.getAttribute('type')
            calendar = LocaleCalendar(type)

            # get month names and abbreviations
            months_nodes = cal_node.getElementsByTagName('months')
            if months_nodes:
                self._extractMonths(months_nodes[0], calendar)

            # get weekday names and abbreviations
            days_nodes = cal_node.getElementsByTagName('days')
            if days_nodes:
                self._extractDays(days_nodes[0], calendar)

            # get week information
            self._extractWeek(cal_node, calendar)

            # get am/pm designation values
            nodes = cal_node.getElementsByTagName('am')
            if nodes:
                calendar.am = self._getText(nodes[0].childNodes)
            nodes = cal_node.getElementsByTagName('pm')
            if nodes:
                calendar.pm = self._getText(nodes[0].childNodes)

            # get era names and abbreviations
            self._extractEras(cal_node, calendar)

            for formatsName, lengthName, formatName in (
                    ('dateFormats', 'dateFormatLength', 'dateFormat'),
                    ('timeFormats', 'timeFormatLength', 'timeFormat'),
                    ('dateTimeFormats', 'dateTimeFormatLength',
                     'dateTimeFormat')):

                formats_nodes = cal_node.getElementsByTagName(formatsName)
                if formats_nodes:
                    default, formats = self._extractFormats(
                        formats_nodes[0], lengthName, formatName)
                    setattr(calendar,
                            'default' + formatName[0].upper() + formatName[1:],
                            default)
                    setattr(calendar, formatsName, formats)

            calendars[calendar.type] = calendar
            if calendar.type in calendarAliases:
                for alias in calendarAliases[calendar.type]:
                    calendars[alias] = calendar

        return calendars

    def _extractTimeZones(self, dates_node):
        """Extract all timezone information for the locale from the DOM
        tree.

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <dates>
          ...   <timeZoneNames>
          ...     <zone type="America/Los_Angeles" >
          ...       <long>
          ...         <generic>Pacific Time</generic>
          ...         <standard>Pacific Standard Time</standard>
          ...         <daylight>Pacific Daylight Time</daylight>
          ...       </long>
          ...       <short>
          ...         <generic>PT</generic>
          ...         <standard>PST</standard>
          ...         <daylight>PDT</daylight>
          ...       </short>
          ...       <exemplarCity>San Francisco</exemplarCity>
          ...     </zone>
          ...     <zone type="Europe/London">
          ...       <long>
          ...         <generic>British Time</generic>
          ...         <standard>British Standard Time</standard>
          ...         <daylight>British Daylight Time</daylight>
          ...       </long>
          ...       <exemplarCity>York</exemplarCity>
          ...     </zone>
          ...   </timeZoneNames>
          ... </dates>'''
          >>> dom = parseString(xml)
          >>> zones = factory._extractTimeZones(dom.documentElement)

          >>> keys = zones.keys()
          >>> keys.sort()
          >>> keys
          ['America/Los_Angeles', 'Europe/London']
          >>> zones["Europe/London"].names["generic"]
          ('British Time', None)
          >>> zones["Europe/London"].cities
          ['York']
          >>> zones["America/Los_Angeles"].names["generic"]
          ('Pacific Time', 'PT')
        """
        tz_names = dates_node.getElementsByTagName('timeZoneNames')
        if not tz_names:
            return

        zones = InheritingDictionary()
        for node in tz_names[0].getElementsByTagName('zone'):
            type = node.getAttribute('type')
            zone = LocaleTimeZone(type)

            # get the short and long name node
            long = node.getElementsByTagName('long')
            short = node.getElementsByTagName('short')
            for type in ("generic", "standard", "daylight"):
                # get long name
                long_desc = None
                if long:
                    long_nodes = long[0].getElementsByTagName(type)
                    if long_nodes:
                        long_desc = self._getText(long_nodes[0].childNodes)
                # get short name
                short_desc = None
                if short:
                    short_nodes = short[0].getElementsByTagName(type)
                    if short_nodes:
                        short_desc = self._getText(short_nodes[0].childNodes)
                if long_desc is not None or short_desc is not None:
                    zone.names[type] = (long_desc, short_desc)

            for city in node.getElementsByTagName('exemplarCity'):
                zone.cities.append(self._getText(city.childNodes))

            zones[zone.type] = zone

        return zones

    def _extractDates(self):
        """Extract all date information from the DOM tree"""
        dates_nodes = self._data.getElementsByTagName('dates')
        if dates_nodes == []:
            return

        dates = LocaleDates()
        calendars = self._extractCalendars(dates_nodes[0])
        if calendars is not None:
            dates.calendars = calendars
        timezones = self._extractTimeZones(dates_nodes[0])
        if timezones is not None:
            dates.timezones = timezones
        return dates

    def _extractSymbols(self, numbers_node):
        """Extract all week entries from cal_node and store them in
        calendar.

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <numbers>
          ...   <symbols>
          ...     <decimal>.</decimal>
          ...     <group>,</group>
          ...     <list>;</list>
          ...     <percentSign>%</percentSign>
          ...     <nativeZeroDigit>0</nativeZeroDigit>
          ...     <patternDigit>#</patternDigit>
          ...     <plusSign>+</plusSign>
          ...     <minusSign>-</minusSign>
          ...     <exponential>E</exponential>
          ...     <perMille>o/oo</perMille>
          ...     <infinity>oo</infinity>
          ...     <nan>NaN</nan>
          ...   </symbols>
          ... </numbers>'''
          >>> dom = parseString(xml)
          >>> symbols = factory._extractSymbols(dom.documentElement)

          >>> symbols['list']
          ';'
          >>> keys = symbols.keys()
          >>> keys.sort()
          >>> keys[:5]
          ['decimal', 'exponential', 'group', 'infinity', 'list']
          >>> keys[5:9]
          ['minusSign', 'nan', 'nativeZeroDigit', 'patternDigit']
          >>> keys[9:]
          ['perMille', 'percentSign', 'plusSign']
        """
        # See whether we have symbols entries
        symbols_nodes = numbers_node.getElementsByTagName('symbols')
        if not symbols_nodes:
            return

        symbols = InheritingDictionary()
        for name in ("decimal", "group", "list", "percentSign",
                     "nativeZeroDigit", "patternDigit", "plusSign",
                     "minusSign", "exponential", "perMille",
                     "infinity", "nan"):
            nodes = symbols_nodes[0].getElementsByTagName(name)
            if nodes:
                symbols[name] = self._getText(nodes[0].childNodes)

        return symbols

    def _extractNumberFormats(self, numbers_node, numbers):
        """Extract all number formats from the numbers_node and save the data
        in numbers.

        Example::

          >>> class Numbers(object):
          ...     defaultDecimalFormat = None
          ...     decimalFormats = None
          ...     defaultScientificFormat = None
          ...     scientificFormats = None
          ...     defaultPercentFormat = None
          ...     percentFormats = None
          ...     defaultCurrencyFormat = None
          ...     currencyFormats = None
          >>> numbers = Numbers()
          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <numbers>
          ...   <decimalFormats>
          ...     <decimalFormatLength type="long">
          ...       <decimalFormat>
          ...         <pattern>#,##0.###</pattern>
          ...       </decimalFormat>
          ...     </decimalFormatLength>
          ...   </decimalFormats>
          ...   <scientificFormats>
          ...     <default type="long"/>
          ...     <scientificFormatLength type="long">
          ...       <scientificFormat>
          ...         <pattern>0.000###E+00</pattern>
          ...       </scientificFormat>
          ...     </scientificFormatLength>
          ...     <scientificFormatLength type="medium">
          ...       <scientificFormat>
          ...         <pattern>0.00##E+00</pattern>
          ...       </scientificFormat>
          ...     </scientificFormatLength>
          ...   </scientificFormats>
          ...   <percentFormats>
          ...     <percentFormatLength type="long">
          ...       <percentFormat>
          ...         <pattern>#,##0%</pattern>
          ...       </percentFormat>
          ...     </percentFormatLength>
          ...   </percentFormats>
          ...   <currencyFormats>
          ...     <currencyFormatLength type="long">
          ...       <currencyFormat>
          ...         <pattern>$ #,##0.00;($ #,##0.00)</pattern>
          ...       </currencyFormat>
          ...     </currencyFormatLength>
          ...   </currencyFormats>
          ... </numbers>'''
          >>> dom = parseString(xml)
          >>> factory._extractNumberFormats(dom.documentElement, numbers)

          >>> numbers.decimalFormats["long"].formats[None].pattern
          '#,##0.###'

          >>> numbers.defaultScientificFormat
          'long'
          >>> numbers.scientificFormats["long"].formats[None].pattern
          '0.000###E+00'
          >>> numbers.scientificFormats["medium"].formats[None].pattern
          '0.00##E+00'

          >>> numbers.percentFormats["long"].formats[None].pattern
          '#,##0%'
          >>> numbers.percentFormats.get("medium", None) is None
          True

          >>> numbers.currencyFormats["long"].formats[None].pattern
          '$ #,##0.00;($ #,##0.00)'
          >>> numbers.currencyFormats.get("medium", None) is None
          True
        """

        for category in ('decimal', 'scientific', 'percent', 'currency'):
            formatsName = category + 'Formats'
            lengthName = category + 'FormatLength'
            formatName = category + 'Format'
            defaultName = 'default' + formatName[0].upper() + formatName[1:]

            formats_nodes = numbers_node.getElementsByTagName(formatsName)
            if formats_nodes:
                default, formats = self._extractFormats(
                    formats_nodes[0], lengthName, formatName)
                setattr(numbers, defaultName, default)
                setattr(numbers, formatsName, formats)

    def _extractCurrencies(self, numbers_node):
        """Extract all currency definitions and their information from the
        Locale's DOM tree.

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <numbers>
          ...   <currencies>
          ...     <currency type="USD">
          ...       <displayName>Dollar</displayName>
          ...       <symbol>$</symbol>
          ...     </currency>
          ...     <currency type ="JPY">
          ...       <displayName>Yen</displayName>
          ...       <symbol>Y</symbol>
          ...     </currency>
          ...     <currency type ="INR">
          ...       <displayName>Rupee</displayName>
          ...       <symbol choice="true">0&lt;=Rf|1&lt;=Ru|1&lt;Rf</symbol>
          ...     </currency>
          ...     <currency type="PTE">
          ...       <displayName>Escudo</displayName>
          ...       <symbol>$</symbol>
          ...     </currency>
          ...   </currencies>
          ... </numbers>'''
          >>> dom = parseString(xml)
          >>> currencies = factory._extractCurrencies(dom.documentElement)

          >>> keys = currencies.keys()
          >>> keys.sort()
          >>> keys
          ['INR', 'JPY', 'PTE', 'USD']

          >>> currencies['USD'].symbol
          '$'
          >>> currencies['USD'].displayName
          'Dollar'
          >>> currencies['USD'].symbolChoice
          False
        """
        currs_nodes = numbers_node.getElementsByTagName('currencies')
        if not currs_nodes:
            return

        currencies = InheritingDictionary()
        for curr_node in currs_nodes[0].getElementsByTagName('currency'):
            type = curr_node.getAttribute('type')
            currency = LocaleCurrency(type)

            nodes = curr_node.getElementsByTagName('symbol')
            if nodes:
                currency.symbol = self._getText(nodes[0].childNodes)
                currency.symbolChoice = \
                    nodes[0].getAttribute('choice') == "true"

            nodes = curr_node.getElementsByTagName('displayName')
            if nodes:
                currency.displayName = self._getText(nodes[0].childNodes)

            currencies[type] = currency

        return currencies

    def _extractNumbers(self):
        """Extract all number information from the DOM tree"""
        numbers_nodes = self._data.getElementsByTagName('numbers')
        if not numbers_nodes:
            return

        numbers = LocaleNumbers()
        symbols = self._extractSymbols(numbers_nodes[0])
        if symbols is not None:
            numbers.symbols = symbols
        self._extractNumberFormats(numbers_nodes[0], numbers)
        currencies = self._extractCurrencies(numbers_nodes[0])
        if currencies is not None:
            numbers.currencies = currencies
        return numbers

    def _extractDelimiters(self):
        """Extract all delimiter entries from the DOM tree.

        Example::

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <ldml>
          ...   <delimiters>
          ...     <quotationStart>``</quotationStart>
          ...     <quotationEnd>''</quotationEnd>
          ...     <alternateQuotationStart>`</alternateQuotationStart>
          ...     <alternateQuotationEnd>'</alternateQuotationEnd>
          ...   </delimiters>
          ...   <identity>
          ...     <version number="1.0"/>
          ...     <generation date="2003-12-19" />
          ...     <language type="en" />
          ...     <territory type="US" />
          ...     <variant type="POSIX" />
          ...   </identity>
          ... </ldml>'''
          >>> dom = parseString(xml)
          >>> factory._data = parseString(xml).documentElement
          >>> delimiters = factory._extractDelimiters()

          >>> delimiters["quotationStart"]
          '``'
          >>> delimiters["quotationEnd"]
          "''"
          >>> delimiters["alternateQuotationStart"]
          '`'
          >>> delimiters["alternateQuotationEnd"]
          "'"

          Escape: "'"

          >>> factory().delimiters == delimiters
          True
        """
        # See whether we have symbols entries
        delimiters_nodes = self._data.getElementsByTagName('delimiters')
        if not delimiters_nodes:
            return

        delimiters = InheritingDictionary()
        for name in ('quotationStart', "quotationEnd",
                     "alternateQuotationStart", "alternateQuotationEnd"):
            nodes = delimiters_nodes[0].getElementsByTagName(name)
            if nodes:
                delimiters[name] = self._getText(nodes[0].childNodes)

        return delimiters

    def _extractOrientation(self):
        """Extract orientation information.

          >>> factory = LocaleFactory(None)
          >>> from xml.dom.minidom import parseString
          >>> xml = '''
          ... <ldml>
          ...   <layout>
          ...     <orientation lines="bottom-to-top"
          ...                  characters="right-to-left" />
          ...   </layout>
          ... </ldml>'''
          >>> dom = parseString(xml)
          >>> factory._data = parseString(xml).documentElement
          >>> orientation = factory._extractOrientation()
          >>> orientation.lines
          'bottom-to-top'
          >>> orientation.characters
          'right-to-left'
        """
        orientation_nodes = self._data.getElementsByTagName('orientation')
        if not orientation_nodes:
            return
        orientation = LocaleOrientation()
        for name in ("characters", "lines"):
            value = orientation_nodes[0].getAttribute(name)
            if value:
                setattr(orientation, name, value)
        return orientation

    def __call__(self):
        """Create the Locale."""
        locale = Locale(self._extractIdentity())

        names = self._extractDisplayNames()
        if names is not None:
            locale.displayNames = names

        dates = self._extractDates()
        if dates is not None:
            locale.dates = dates

        numbers = self._extractNumbers()
        if numbers is not None:
            locale.numbers = numbers

        delimiters = self._extractDelimiters()
        if delimiters is not None:
            locale.delimiters = delimiters

        orientation = self._extractOrientation()
        if orientation is not None:
            locale.orientation = orientation

        # Unmapped:
        #
        #   - <characters>
        #   - <measurement>
        #   - <collations>, <collation>

        return locale
