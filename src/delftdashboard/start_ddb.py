"""Entry point for the (PyInstaller / Nuitka) built DelftDashboard executable."""

import os
import sys
import tempfile
import traceback

# numba (via numba_celltree, used to rasterise polygons onto the grid when
# updating the active-cell mask) caches compiled functions with cache=True. In a
# frozen build the default cache location - next to the bundled module - is
# often unresolvable or non-writable, which makes the first JIT compile hang
# with no error. Point numba at a guaranteed-writable per-user directory before
# anything imports it. setdefault() leaves any user-provided value untouched.
os.environ.setdefault(
    "NUMBA_CACHE_DIR",
    os.path.join(
        os.environ.get("LOCALAPPDATA") or tempfile.gettempdir(),
        "DelftDashboard",
        "numba_cache",
    ),
)

import delftdashboard  # noqa: E402

# rasterio 1.5 installs a broken sys.excepthook that recurses infinitely, and
# hydromt wraps it (see hydromt/__init__.py). In a frozen build that recursion
# overflows the C stack and turns any unhandled exception into a segfault,
# hiding the real error. Restore the default hook so genuine errors are
# reported normally instead of crashing the reporter.
sys.excepthook = sys.__excepthook__

try:
    delftdashboard.start()
except BaseException:
    # hydromt re-installs rasterio's broken excepthook while start() imports it,
    # so restore the default again before we finish - otherwise re-raising would
    # recurse through it and segfault. Print the real traceback ourselves and
    # keep the console window open so the message can be read, then exit cleanly
    # (sys.exit avoids routing the exception through sys.excepthook at all).
    sys.excepthook = sys.__excepthook__
    traceback.print_exc()
    try:
        input("\nDelftDashboard exited with an error. Press Enter to close...")
    except EOFError:
        pass
    sys.exit(1)
