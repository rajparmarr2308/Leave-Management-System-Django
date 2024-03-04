__import__("pkg_resources").declare_namespace(__name__)

# Fix a NameError in Chameleon.
import chameleon.i18n  # noqa: E402


chameleon.i18n.basestring = (str,)
