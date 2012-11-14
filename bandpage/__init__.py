"""
bandpage
~~~~~~~~

:copyright: (c) 2012 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('bandpage').version
except Exception:
    VERSION = 'unknown'

# Import the public API
from .api import *
