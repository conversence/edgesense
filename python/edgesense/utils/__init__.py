from __future__ import absolute_import
from . import logger_initializer
from . import resource
from . import extract
from . import gexf

def sort_by(key):
    return (lambda e: e.get(key, None))

