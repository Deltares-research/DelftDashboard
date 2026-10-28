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

# The map (MapLibre) needs WebGL. Chromium (QtWebEngine) blocklists some GPUs,
# notably virtual ones (VMware, Hyper-V, remote desktops), and then disables
# WebGL, leaving the map white. Ignore the blocklist so WebGL stays available.
# Must be set before QtWebEngine starts; flags set by the user are kept.
_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
if "--ignore-gpu-blocklist" not in _flags:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (_flags + " --ignore-gpu-blocklist").strip()


def _patch_numba_cache_locator():
    """Let numba cache jitted functions in the exe without their source files.

    The build keeps numba-jitted modules as bytecode (see
    installer/nuitka_numba_bytecode.py) so numba's JIT works. Their functions
    still point at the .py files on the build machine, which do not exist on
    other PCs. numba then finds no cache location and raises "cannot cache
    function ... no locator available" while importing any module with
    cache=True functions. This locator caches in NUMBA_CACHE_DIR regardless of
    the source file and invalidates the cache when the exe changes. It is put
    first, so the build machine behaves like any other PC.
    """
    if os.environ.get("NUMBA_DISABLE_JIT") == "1":
        return
    try:
        from numba.core import caching, config
    except Exception:
        return

    class _FrozenExeCacheLocator(caching._CacheLocator):
        def __init__(self, py_func, py_file):
            self._lineno = py_func.__code__.co_firstlineno
            self._cache_path = os.path.join(
                config.CACHE_DIR, self.get_suitable_cache_subpath(py_file)
            )

        def get_cache_path(self):
            return self._cache_path

        def get_source_stamp(self):
            st = os.stat(sys.executable)
            return st.st_mtime, st.st_size

        def get_disambiguator(self):
            return str(self._lineno)

        @classmethod
        def from_function(cls, py_func, py_file):
            if not config.CACHE_DIR:
                return None
            self = cls(py_func, py_file)
            try:
                self.ensure_cache_path()
            except OSError:
                return None
            return self

    # The class is called CacheImpl in recent numba, _CacheImpl in older ones.
    impl = getattr(caching, "CacheImpl", None) or getattr(caching, "_CacheImpl")
    impl._locator_classes.insert(0, _FrozenExeCacheLocator)


# Only in the compiled exe (Nuitka defines __compiled__); a source run uses
# numba's normal cache next to the source files.
if "__compiled__" in globals():
    _patch_numba_cache_locator()

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
