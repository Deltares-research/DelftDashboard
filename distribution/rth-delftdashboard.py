import sys
import yaml

from delftdashboard import __file__ as SRC_DIR
from delftdashboard.delftdashboard_gui import __file__ as ENTRY_POINT
from pathlib import Path

# Extend the python path to stop import errors when trying to import app.
# since the .exe is not in the same directory as delftdashboard_gui.py
sys.path.append(str(Path(SRC_DIR).absolute().parent))
sys.path.append(str(Path(ENTRY_POINT).absolute().parent))

DDB_INI = Path(SRC_DIR).resolve().parent / "config" / "delftdashboard.ini"

with open(DDB_INI, "r") as f:
    config = yaml.safe_load(f)

# paths are relative to the .exe, but ddb doesnt accept relative paths
# So make them absolute at runtime
if bathymetry_database:= config.get("bathymetry_database", None):
    config.update({ "bathymetry_database": str(Path(bathymetry_database).resolve()),})

data_libs = []
for rel_path in config.get("data_libs", []):
    p = Path(rel_path).resolve()
    if not p.exists():
        print(f"Something went wrong trying to update {DDB_INI}. Data catalog {p} does not exist. Skipping...")
        continue
    data_libs.append(str(Path(rel_path).resolve()))
if data_libs:
    config.update({ "data_libs": data_libs, })

with open(DDB_INI, "w") as f:
    yaml.dump(config, f)