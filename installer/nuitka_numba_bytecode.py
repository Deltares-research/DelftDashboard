"""Nuitka user plugin: keep numba-jitted code as Python bytecode.

numba compiles a function by reading its Python bytecode. Nuitka normally turns
every module into C, which leaves numba nothing to read, so by default Nuitka
disables numba's JIT in standalone builds (NUMBA_DISABLE_JIT=1). The jitted
loops then run as slow plain Python - e.g. updating the SFINCS mask with a
polygon, drawing grids/masks with datashader, building subgrid tables.

This plugin tells Nuitka to include the modules that define jitted functions
(and numba itself, whose overloads are jitted from Python source too) as
bytecode instead of C. Combined with ``--module-parameter=numba-disable-jit=no``
numba then works in the exe as it does when running from source.

Used by build_delftdashboard.py via ``--user-plugin=``.
"""

from nuitka.plugins.PluginBase import NuitkaPluginBase

# Whole packages: numba itself plus libraries that are mostly jitted code.
BYTECODE_PACKAGES = (
    "numba",
    "numba_celltree",  # xugrid polygon rasterisation (mask update)
    "xugrid",
    "datashader",  # map drawing of grids, masks, points
    "pyflwdir",  # hydromt flow directions
)

# Single modules with jitted functions inside otherwise compiled packages.
BYTECODE_MODULES = (
    "hydromt.stats.design_events",
    "hydromt.stats.extremes",
    "hydromt_sfincs.components.grid.subgrid",
    "hydromt_sfincs.components.quadtree.subgrid_quadtree_builder",
    "hydromt_sfincs.workflows.subgrid",
    "hydromt_hurrywave.components.quadtree.wave_blocking",
    "hydromt_hurrywave.workflows.tiling",
)


class NuitkaPluginNumbaBytecode(NuitkaPluginBase):
    plugin_name = "numba-bytecode"
    plugin_desc = "Keep numba-jitted modules as bytecode so numba's JIT works."

    def decideCompilation(self, module_name):
        if module_name.hasOneOfNamespaces(BYTECODE_PACKAGES):
            return "bytecode"
        if module_name.asString() in BYTECODE_MODULES:
            return "bytecode"
        return None
