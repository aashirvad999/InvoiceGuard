# InvoiceGuard Engine Package
import os
import sys

_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
_API_DIR = os.path.dirname(_ENGINE_DIR)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)
