import logging
import os.path
from contextlib import closing
from os.path import join

from pythongettext.msgfmt import Msgfmt
from pythongettext.msgfmt import PoSyntaxError


logger = logging.getLogger('zope.i18n')


HAS_PYTHON_GETTEXT = True


def _safe_mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def compile_mo_file(domain, lc_messages_path):
    """Creates or updates a mo file in the locales folder."""

    base = join(lc_messages_path, domain)
    pofile = str(base + '.po')
    mofile = str(base + '.mo')

    po_mtime = _safe_mtime(pofile)
    mo_mtime = _safe_mtime(mofile) or 0

    if po_mtime is None:
        logger.debug("Unable to access %s (%s)",
                     pofile, po_mtime)
        return

    if po_mtime > mo_mtime:
        try:
            # Msgfmt doesn't properly close a
            # file it opens for reading if you pass the path,
            # but it does if you pass the file.
            with open(pofile, 'rb') as pofd:
                with closing(Msgfmt(pofd, domain).getAsFile()) as mo:
                    with open(mofile, 'wb') as fd:
                        fd.write(mo.read())
        except PoSyntaxError as err:
            logger.warning(
                'Syntax error while compiling %s (%s).', pofile, err.msg)
        except OSError as err:
            logger.warning('Error while compiling %s (%s).', pofile, err)
