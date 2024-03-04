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
"""Interfaces related to Locales
"""
import datetime
import re

from zope.interface import Attribute
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Date
from zope.schema import Dict
from zope.schema import Field
from zope.schema import Int
from zope.schema import List
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Tuple


class ILocaleProvider(Interface):
    """This interface is our connection to the Zope 3 service. From it
    we can request various Locale objects that can perform all sorts of
    fancy operations.

    This service will be singelton global service, since it doe not make much
    sense to have many locale facilities, especially since this one will be so
    complete, since we will the ICU XML Files as data.  """

    def loadLocale(language=None, country=None, variant=None):
        """Load the locale with the specs that are given by the arguments of
        the method. Note that the LocaleProvider must know where to get the
        locales from."""

    def getLocale(language=None, country=None, variant=None):
        """Get the Locale object for a particular language, country and
        variant."""


class ILocaleIdentity(Interface):
    """Identity information class for ILocale objects.

    Three pieces of information are required to identify a locale:

      o language -- Language in which all of the locale text information are
        returned.

      o script -- Script in which all of the locale text information are
        returned.

      o territory -- Territory for which the locale's information are
        appropriate. None means all territories in which language is spoken.

      o variant -- Sometimes there are regional or historical differences even
        in a certain country. For these cases we use the variant field. A good
        example is the time before the Euro in Germany for example. Therefore
        a valid variant would be 'PREEURO'.

    Note that all of these attributes are read-only once they are set (usually
    done in the constructor)!

    This object is also used to uniquely identify a locale.
    """

    language = TextLine(
        title="Language Type",
        description="The language for which a locale is applicable.",
        constraint=re.compile(r'[a-z]{2}').match,
        required=True,
        readonly=True)

    script = TextLine(
        title="Script Type",
        description=("""The script for which the language/locale is
                       applicable."""),
        constraint=re.compile(r'[a-z]*').match)

    territory = TextLine(
        title="Territory Type",
        description="The territory for which a locale is applicable.",
        constraint=re.compile(r'[A-Z]{2}').match,
        required=True,
        readonly=True)

    variant = TextLine(
        title="Variant Type",
        description="The variant for which a locale is applicable.",
        constraint=re.compile(r'[a-zA-Z]*').match,
        required=True,
        readonly=True)

    version = Field(
        title="Locale Version",
        description="The value of this field is an ILocaleVersion object.",
        readonly=True)

    def __repr__(self):
        """Defines the representation of the id, which should be a compact
        string that references the language, country and variant."""


class ILocaleVersion(Interface):
    """Represents the version of a locale.

    The locale version is part of the ILocaleIdentity object.
    """

    number = TextLine(
        title="Version Number",
        description="The version number of the locale.",
        constraint=re.compile(r'^([0-9].)*[0-9]$').match,
        required=True,
        readonly=True)

    generationDate = Date(
        title="Generation Date",
        description="Specifies the creation date of the locale.",
        constraint=lambda date: date < datetime.datetime.now(),
        readonly=True)

    notes = Text(
        title="Notes",
        description="Some release notes for the version of this locale.",
        readonly=True)


class ILocaleDisplayNames(Interface):
    """Localized Names of common text strings.

    This object contains localized strings for many terms, including
    language, script and territory names. But also keys and types used
    throughout the locale object are localized here.
    """

    languages = Dict(
        title="Language type to translated name",
        key_type=TextLine(title="Language Type"),
        value_type=TextLine(title="Language Name"))

    scripts = Dict(
        title="Script type to script name",
        key_type=TextLine(title="Script Type"),
        value_type=TextLine(title="Script Name"))

    territories = Dict(
        title="Territory type to translated territory name",
        key_type=TextLine(title="Territory Type"),
        value_type=TextLine(title="Territory Name"))

    variants = Dict(
        title="Variant type to name",
        key_type=TextLine(title="Variant Type"),
        value_type=TextLine(title="Variant Name"))

    keys = Dict(
        title="Key type to name",
        key_type=TextLine(title="Key Type"),
        value_type=TextLine(title="Key Name"))

    types = Dict(
        title="Type type and key to localized name",
        key_type=Tuple(title="Type Type and Key"),
        value_type=TextLine(title="Type Name"))


class ILocaleTimeZone(Interface):
    """Represents and defines various timezone information. It mainly manages
    all the various names for a timezone and the cities contained in it.

    Important: ILocaleTimeZone objects are not intended to provide
    implementations for the standard datetime module timezone support. They
    are merily used for Locale support.
    """

    type = TextLine(
        title="Time Zone Type",
        description="Standard name of the timezone for unique referencing.",
        required=True,
        readonly=True)

    cities = List(
        title="Cities",
        description="Cities in Timezone",
        value_type=TextLine(title="City Name"),
        required=True,
        readonly=True)

    names = Dict(
        title="Time Zone Names",
        description="Various names of the timezone.",
        key_type=Choice(
            title="Time Zone Name Type",
            values=("generic", "standard", "daylight")),
        value_type=Tuple(title="Time Zone Name and Abbreviation",
                         min_length=2, max_length=2),
        required=True,
        readonly=True)


class ILocaleFormat(Interface):
    """Specifies a format for a particular type of data."""

    type = TextLine(
        title="Format Type",
        description="The name of the format",
        required=False,
        readonly=True)

    displayName = TextLine(
        title="Display Name",
        description="Name of the calendar, for example 'gregorian'.",
        required=False,
        readonly=True)

    pattern = TextLine(
        title="Format Pattern",
        description="The pattern that is used to format the object.",
        required=True,
        readonly=True)


class ILocaleFormatLength(Interface):
    """The format length describes a class of formats."""

    type = Choice(
        title="Format Length Type",
        description="Name of the format length",
        values=("full", "long", "medium", "short")
    )

    default = TextLine(
        title="Default Format",
        description="The name of the defaulkt format.")

    formats = Dict(
        title="Formats",
        description="Maps format types to format objects",
        key_type=TextLine(title="Format Type"),
        value_type=Field(
            title="Format Object",
            description="Values are ILocaleFormat objects."),
        required=True,
        readonly=True)


class ILocaleMonthContext(Interface):
    """Specifices a usage context for month names"""

    type = TextLine(
        title="Month context type",
        description="Name of the month context, format or stand-alone.")

    defaultWidth = TextLine(
        title="Default month name width",
        default="wide")

    months = Dict(
        title="Month Names",
        description=("A mapping of month name widths to a mapping of"
                     "corresponding month names."),
        key_type=Choice(
            title="Width type",
            values=("wide", "abbreviated", "narrow")),
        value_type=Dict(
            title="Month name",
            key_type=Int(title="Type", min=1, max=12),
            value_type=TextLine(title="Month Name"))
    )


class ILocaleDayContext(Interface):
    """Specifices a usage context for days names"""

    type = TextLine(
        title="Day context type",
        description="Name of the day context, format or stand-alone.")

    defaultWidth = TextLine(
        title="Default day name width",
        default="wide")

    days = Dict(
        title="Day Names",
        description=("A mapping of day name widths to a mapping of"
                     "corresponding day names."),
        key_type=Choice(
            title="Width type",
            values=("wide", "abbreviated", "narrow")),
        value_type=Dict(
            title="Day name",
            key_type=Choice(
                title="Type",
                values=("sun", "mon", "tue", "wed",
                        "thu", "fri", "sat")),
            value_type=TextLine(title="Day Name"))
    )


class ILocaleCalendar(Interface):
    """There is a massive amount of information contained in the calendar,
    which made it attractive to be added."""

    type = TextLine(
        title="Calendar Type",
        description="Name of the calendar, for example 'gregorian'.")

    defaultMonthContext = TextLine(
        title="Default month context",
        default="format")

    monthContexts = Dict(
        title="Month Contexts",
        description=("A mapping of month context types to "
                     "ILocaleMonthContext objects"),
        key_type=Choice(title="Type",
                        values=("format", "stand-alone")),
        value_type=Field(title="ILocaleMonthContext object"))

    # BBB: leftover from CLDR 1.0
    months = Dict(
        title="Month Names",
        description="A mapping of all month names and abbreviations",
        key_type=Int(title="Type", min=1, max=12),
        value_type=Tuple(title="Month Name and Abbreviation",
                         min_length=2, max_length=2))

    defaultDayContext = TextLine(
        title="Default day context",
        default="format")

    dayContexts = Dict(
        title="Day Contexts",
        description=("A mapping of day context types to "
                     "ILocaleDayContext objects"),
        key_type=Choice(title="Type",
                        values=("format", "stand-alone")),
        value_type=Field(title="ILocaleDayContext object"))

    # BBB: leftover from CLDR 1.0
    days = Dict(
        title="Weekdays Names",
        description="A mapping of all month names and abbreviations",
        key_type=Choice(title="Type",
                        values=("sun", "mon", "tue", "wed",
                                "thu", "fri", "sat")),
        value_type=Tuple(title="Weekdays Name and Abbreviation",
                         min_length=2, max_length=2))

    week = Dict(
        title="Week Information",
        description="Contains various week information",
        key_type=Choice(
            title="Type",
            description=("""
            Varies Week information:

              - 'minDays' is just an integer between 1 and 7.

              - 'firstDay' specifies the first day of the week by integer.

              - The 'weekendStart' and 'weekendEnd' are tuples of the form
                (weekDayNumber, datetime.time)
            """),
            values=("minDays", "firstDay",
                    "weekendStart", "weekendEnd")))

    am = TextLine(title="AM String")

    pm = TextLine(title="PM String")

    eras = Dict(
        title="Era Names",
        key_type=Int(title="Type", min=0),
        value_type=Tuple(title="Era Name and Abbreviation",
                         min_length=2, max_length=2))

    defaultDateFormat = TextLine(title="Default Date Format Type")

    dateFormats = Dict(
        title="Date Formats",
        description="Contains various Date Formats.",
        key_type=Choice(
            title="Type",
            description="Name of the format length",
            values=("full", "long", "medium", "short")),
        value_type=Field(title="ILocaleFormatLength object"))

    defaultTimeFormat = TextLine(title="Default Time Format Type")

    timeFormats = Dict(
        title="Time Formats",
        description="Contains various Time Formats.",
        key_type=Choice(
            title="Type",
            description="Name of the format length",
            values=("full", "long", "medium", "short")),
        value_type=Field(title="ILocaleFormatLength object"))

    defaultDateTimeFormat = TextLine(title="Default Date-Time Format Type")

    dateTimeFormats = Dict(
        title="Date-Time Formats",
        description="Contains various Date-Time Formats.",
        key_type=Choice(
            title="Type",
            description="Name of the format length",
            values=("full", "long", "medium", "short")),
        value_type=Field(title="ILocaleFormatLength object"))

    def getMonthNames():
        """Return a list of month names."""

    def getMonthTypeFromName(name):
        """Return the type of the month with the right name."""

    def getMonthAbbreviations():
        """Return a list of month abbreviations."""

    def getMonthTypeFromAbbreviation(abbr):
        """Return the type of the month with the right abbreviation."""

    def getDayNames():
        """Return a list of weekday names."""

    def getDayTypeFromName(name):
        """Return the id of the weekday with the right name."""

    def getDayAbbr():
        """Return a list of weekday abbreviations."""

    def getDayTypeFromAbbr(abbr):
        """Return the id of the weekday with the right abbr."""

    def isWeekend(datetime):
        """Determines whether a the argument lies in a weekend."""

    def getFirstDayName():
        """Return the the type of the first day in the week."""


class ILocaleDates(Interface):
    """This object contains various data about dates, times and time zones."""

    localizedPatternChars = TextLine(
        title="Localized Pattern Characters",
        description="Localized pattern characters used in dates and times")

    calendars = Dict(
        title="Calendar type to ILocaleCalendar",
        key_type=Choice(
            title="Calendar Type",
            values=("gregorian",
                    "arabic",
                    "chinese",
                    "civil-arabic",
                    "hebrew",
                    "japanese",
                    "thai-buddhist")),
        value_type=Field(title="Calendar",
                         description="This is a ILocaleCalendar object."))

    timezones = Dict(
        title="Time zone type to ILocaleTimezone",
        key_type=TextLine(title="Time Zone type"),
        value_type=Field(title="Time Zone",
                         description="This is a ILocaleTimeZone object."))

    def getFormatter(category, length=None, name=None, calendar="gregorian"):
        """Get a date/time formatter.

        `category` must be one of 'date', 'dateTime', 'time'.

        The 'length' specifies the output length of the value. The allowed
        values are: 'short', 'medium', 'long' and 'full'. If no length was
        specified, the default length is chosen.
        """


class ILocaleCurrency(Interface):
    """Defines a particular currency."""

    type = TextLine(title="Type")

    symbol = TextLine(title="Symbol")

    displayName = TextLine(title="Official Name")

    symbolChoice = Bool(title="Symbol Choice")


class ILocaleNumbers(Interface):
    """This object contains various data about numbers and currencies."""

    symbols = Dict(
        title="Number Symbols",
        key_type=Choice(
            title="Format Name",
            values=("decimal", "group", "list", "percentSign",
                    "nativeZeroDigit", "patternDigit", "plusSign",
                    "minusSign", "exponential", "perMille",
                    "infinity", "nan")),
        value_type=TextLine(title="Symbol"))

    defaultDecimalFormat = TextLine(title="Default Decimal Format Type")

    decimalFormats = Dict(
        title="Decimal Formats",
        description="Contains various Decimal Formats.",
        key_type=Choice(
            title="Type",
            description="Name of the format length",
            values=("full", "long", "medium", "short")),
        value_type=Field(title="ILocaleFormatLength object"))

    defaultScientificFormat = TextLine(title="Default Scientific Format Type")

    scientificFormats = Dict(
        title="Scientific Formats",
        description="Contains various Scientific Formats.",
        key_type=Choice(
            title="Type",
            description="Name of the format length",
            values=("full", "long", "medium", "short")),
        value_type=Field(title="ILocaleFormatLength object"))

    defaultPercentFormat = TextLine(title="Default Percent Format Type")

    percentFormats = Dict(
        title="Percent Formats",
        description="Contains various Percent Formats.",
        key_type=Choice(
            title="Type",
            description="Name of the format length",
            values=("full", "long", "medium", "short")),
        value_type=Field(title="ILocaleFormatLength object"))

    defaultCurrencyFormat = TextLine(title="Default Currency Format Type")

    currencyFormats = Dict(
        title="Currency Formats",
        description="Contains various Currency Formats.",
        key_type=Choice(
            title="Type",
            description="Name of the format length",
            values=("full", "long", "medium", "short")),
        value_type=Field(title="ILocaleFormatLength object"))

    currencies = Dict(
        title="Currencies",
        description="Contains various Currency data.",
        key_type=TextLine(
            title="Type",
            description="Name of the format length"),
        value_type=Field(title="ILocaleCurrency object"))

    def getFormatter(category, length=None, name=""):
        """Get the NumberFormat based on the category, length and name of the
        format.

        The 'category' specifies the type of number format you would like to
        have. The available options are: 'decimal', 'percent', 'scientific',
        'currency'.

        The 'length' specifies the output length of the number. The allowed
        values are: 'short', 'medium', 'long' and 'full'. If no length was
        specified, the default length is chosen.

        Every length can have actually several formats. In this case these
        formats are named and you can specify the name here. If no name was
        specified, the first unnamed format is chosen.
        """

    def getDefaultCurrency():
        """Get the default currency."""


_orientations = ["left-to-right", "right-to-left",
                 "top-to-bottom", "bottom-to-top"]


class ILocaleOrientation(Interface):
    """Information about the orientation of text."""

    characters = Choice(
        title="Orientation of characters",
        values=_orientations,
        default="left-to-right"
    )

    lines = Choice(
        title="Orientation of characters",
        values=_orientations,
        default="top-to-bottom"
    )


class ILocale(Interface):
    """This class contains all important information about the locale.

    Usually a Locale is identified using a specific language, country and
    variant.  However, the country and variant are optional, so that a lookup
    hierarchy develops.  It is easy to recognize that a locale that is missing
    the variant is more general applicable than the one with the variant.
    Therefore, if a specific Locale does not contain the required information,
    it should look one level higher.  There will be a root locale that
    specifies none of the above identifiers.
    """

    id = Field(
        title="Locale identity",
        description="ILocaleIdentity object identifying the locale.",
        required=True,
        readonly=True)

    displayNames = Field(
        title="Display Names",
        description=("""ILocaleDisplayNames object that contains localized
                        names."""))

    dates = Field(
        title="Dates",
        description="ILocaleDates object that contains date/time data.")

    numbers = Field(
        title="Numbers",
        description="ILocaleNumbers object that contains number data.")

    orientation = Field(
        title="Orientation",
        description="ILocaleOrientation with text orientation info.")

    delimiters = Dict(
        title="Delimiters",
        description="Contains various Currency data.",
        key_type=Choice(
            title="Delimiter Type",
            description="Delimiter name.",
            values=("quotationStart",
                    "quotationEnd",
                    "alternateQuotationStart",
                    "alternateQuotationEnd")),
        value_type=Field(title="Delimiter symbol"))

    def getLocaleID():
        """Return a locale id as specified in the LDML specification"""


class ILocaleInheritance(Interface):
    """Locale inheritance support.

    Locale-related objects implementing this interface are able to ask for its
    inherited self. For example, 'en_US.dates.monthNames' can call on itself
    'getInheritedSelf()' and get the value for 'en.dates.monthNames'.
    """

    __parent__ = Attribute("The parent in the location hierarchy")

    __name__ = TextLine(
        title="The name within the parent",
        description=("""The parent can be traversed with this name to get
                       the object."""))

    def getInheritedSelf():
        """Return itself but in the next higher up Locale."""


class IAttributeInheritance(ILocaleInheritance):
    """Provides inheritance properties for attributes"""

    def __setattr__(name, value):
        """Set a new attribute on the object.

        When a value is set on any inheritance-aware object and the value
        also implements ILocaleInheritance, then we need to set the
        '__parent__' and '__name__' attribute on the value.
        """

    def __getattribute__(name):
        """Return the value of the attribute with the specified name.

        If an attribute is not found or is None, the next higher up Locale
        object is consulted."""


class IDictionaryInheritance(ILocaleInheritance):
    """Provides inheritance properties for dictionary keys"""

    def __setitem__(key, value):
        """Set a new item on the object.

        Here we assume that the value does not require any inheritance, so
        that we do not set '__parent__' or '__name__' on the value.
        """

    def __getitem__(key):
        """Return the value of the item with the specified name.

        If an key is not found or is None, the next higher up Locale
        object is consulted.
        """


class ICollator(Interface):
    """Provide support for collating text strings

    This interface will typically be provided by adapting a locale.
    """

    def key(text):
        """Return a collation key for the given text.
        """

    def cmp(text1, text2):
        """Compare two text strings.

        The return value is negative if text1 < text2, 0 is they are
        equal, and positive if text1 > text2.
        """
