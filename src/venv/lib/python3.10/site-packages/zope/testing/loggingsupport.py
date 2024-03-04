##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
import logging


class Handler(logging.Handler):
    """
    A `logging.Handler` that collects logging records
    that are emitted by the loggers named in *names*.

    You must call `install` to begin collecting records,
    and before destroying this object you must call
    `uninstall`.
    """

    def __init__(self, *names, **kw):
        logging.Handler.__init__(self)
        self.names = names
        self.records = []
        self.setLoggerLevel(**kw)

    def setLoggerLevel(self, level=1):
        self.level = level
        self.oldlevels = {}

    def emit(self, record):
        """
        Save the given record in ``self.records``.
        """
        self.records.append(record)

    def clear(self):
        """
        Delete all records collecting by this
        object.
        """
        del self.records[:]

    def install(self):
        """
        Begin collecting logging records for all the
        logger names given to the constructor.
        """
        for name in self.names:
            logger = logging.getLogger(name)
            self.oldlevels[name] = logger.level
            logger.setLevel(self.level)
            logger.addHandler(self)

    def uninstall(self):
        """
        Stop collecting logging records.
        """
        for name in self.names:
            logger = logging.getLogger(name)
            logger.setLevel(self.oldlevels[name])
            logger.removeHandler(self)

    def __str__(self):
        return '\n'.join(
            "{} {}\n  {}".format(
                record.name, record.levelname,
               '\n'.join(
                   line
                   for line in record.getMessage().split('\n')
                   if line.strip()
               ),
            )
            for record in self.records
        )


class InstalledHandler(Handler):
    """
    A `Handler` that automatically calls `install`
    when constructed.

    You must still manually call `uninstall`.
    """

    def __init__(self, *names, **kw):
        Handler.__init__(self, *names, **kw)
        self.install()
