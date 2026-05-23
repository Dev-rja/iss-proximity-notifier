# monkey_patch.py
# Must be imported FIRST in app.py and main.py before anything else.
# Fixes Python 3.13 breaking pyorbital's internal use of round() on datetimes.
import builtins

_original_round = builtins.round

def _safe_round(x, *args, **kwargs):
    try:
        return _original_round(x, *args, **kwargs)
    except TypeError:
        return x

builtins.round = _safe_round