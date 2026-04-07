"""GUI callbacks for the tropical cyclone modify tab.

Allows the user to modify the cyclone track geometry on the map
using the draw layer, with live preview of the modified track.
"""

from datetime import datetime
from typing import Any

import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point

from delftdashboard.app import app
from delftdashboard.operations import map

dateformat = "%Y%m%d %H%M%S"


def select(*args: Any) -> None:
    """Activate the modify tab and populate the track table."""
    map.update()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")

    # Store a backup of the current track so we can revert
    toolbox = app.toolbox["tropical_cyclone"]
    if toolbox.tc.track.gdf is not None and len(toolbox.tc.track.gdf) > 1:
        toolbox._backup_track_gdf = toolbox.tc.track.gdf.copy()
    else:
        toolbox._backup_track_gdf = None

    app.gui.setvar("tropical_cyclone", "track_modified", False)
    _update_table()


def deselect(*args: Any) -> None:
    """Called when leaving the modify tab. Ask to keep changes if needed."""
    toolbox = app.toolbox["tropical_cyclone"]

    if app.gui.getvar("tropical_cyclone", "track_modified"):
        # User is still editing — ask to keep
        keep = app.gui.window.dialog_yes_no(
            "You have unsaved track modifications. Keep the modified track?"
        )
        if keep:
            _accept()
        else:
            _revert()


def modify_on_map(*args: Any) -> None:
    """Load the current track into the draw layer for editing."""
    toolbox = app.toolbox["tropical_cyclone"]

    # Use the preview track if available, otherwise the actual track
    if hasattr(toolbox, "_preview_track_gdf") and toolbox._preview_track_gdf is not None:
        track_gdf = toolbox._preview_track_gdf
    else:
        track_gdf = toolbox.tc.track.gdf

    if track_gdf is None or len(track_gdf) < 2:
        app.gui.window.dialog_warning("No track loaded to modify.")
        return

    # Store as the base for interpolation (only set once per modify session)
    toolbox._original_track_gdf = track_gdf.copy()

    # Convert track points to a polyline for the draw layer
    # Store exact coordinates for matching after edit
    points = [
        (row.geometry.x, row.geometry.y)
        for _, row in track_gdf.iterrows()
    ]
    toolbox._original_coords = list(points)
    line = LineString(points)
    gdf = gpd.GeoDataFrame({"geometry": [line]}, crs=4326)

    # Make draw layer visible and load track for editing
    draw_layer = app.map.layer["tropical_cyclone"].layer["draw_track"]
    draw_layer.set_mode("active")
    draw_layer.set_data(gdf)
    feature_id = draw_layer.get_feature_id(0)
    if feature_id is not None:
        draw_layer.activate_feature(feature_id)

    # Hide cyclone track layer while editing
    app.map.layer["tropical_cyclone"].layer["cyclone_track"].hide()

    app.gui.setvar("tropical_cyclone", "track_modified", True)
    app.gui.window.update()


def track_modified_on_map(gdf, feature_index, feature_id):
    """Called each time the user moves/adds a vertex on the draw layer."""
    pass


def track_edit_finished():
    """Called when the user deselects the feature (leaves edit mode).

    Rebuilds the preview one final time and hides the draw layer.
    """
    # Read final geometry from draw layer
    draw_layer = app.map.layer["tropical_cyclone"].layer["draw_track"]
    if len(draw_layer.gdf) > 0:
        geom = draw_layer.gdf.iloc[0].geometry
        _rebuild_preview_from_geom(geom)

    # Hide the draw layer so it doesn't cover the cyclone track
    draw_layer.set_mode("invisible")


def _rebuild_preview_from_geom(geom):
    """Rebuild the track from a polyline geometry."""
    toolbox = app.toolbox["tropical_cyclone"]

    if not hasattr(toolbox, "_original_track_gdf") or toolbox._original_track_gdf is None:
        return

    new_coords = list(geom.coords)

    if len(new_coords) < 2:
        return

    # Rebuild the track from modified vertices
    new_track = _rebuild_track(toolbox._original_track_gdf, new_coords)
    if new_track is None:
        return

    # Store as preview (not committed to tc.track yet)
    toolbox._preview_track_gdf = new_track

    # Show preview on the cyclone track layer
    app.map.layer["tropical_cyclone"].layer["cyclone_track"].set_data(new_track)
    app.map.layer["tropical_cyclone"].layer["cyclone_track"].show()

    # Update table
    _update_table_from_gdf(new_track)


def table_edited(*args: Any) -> None:
    """Called when the user edits a cell in the track table.

    Rebuilds the preview track from the table data and updates the map.
    """
    toolbox = app.toolbox["tropical_cyclone"]
    df = app.gui.getvar("tropical_cyclone", "track_table")

    if df is None or len(df) == 0:
        return

    # Rebuild the preview GDF from the edited table
    # The table has lon/lat columns that need to become geometry
    table_df = df.drop(columns=["lon", "lat"], errors="ignore").copy()

    # Convert display datetime back to internal format
    display_fmt = "%Y-%m-%d %H:%M"
    if "datetime" in table_df.columns:
        table_df["datetime"] = table_df["datetime"].apply(
            lambda s: datetime.strptime(s, display_fmt).strftime(dateformat)
        )

    preview = gpd.GeoDataFrame(
        table_df,
        geometry=[Point(lon, lat) for lon, lat in zip(df["lon"], df["lat"])],
        crs=4326,
    )

    toolbox._preview_track_gdf = preview
    app.gui.setvar("tropical_cyclone", "track_modified", True)

    # Update the cyclone track layer on the map
    app.map.layer["tropical_cyclone"].layer["cyclone_track"].set_data(preview)
    app.map.layer["tropical_cyclone"].layer["cyclone_track"].show()


def save_track(*args: Any) -> None:
    """Save the current track to a .cyc file."""
    app.toolbox["tropical_cyclone"].save_track()


def accept_modification(*args: Any) -> None:
    """Accept the modified track and commit to the TropicalCyclone object."""
    _accept()


def cancel_modification(*args: Any) -> None:
    """Cancel track modification and restore the original."""
    _revert()


def _accept() -> None:
    """Commit the preview track to tc.track."""
    toolbox = app.toolbox["tropical_cyclone"]

    # Use preview if available, otherwise try to rebuild from draw layer
    if hasattr(toolbox, "_preview_track_gdf") and toolbox._preview_track_gdf is not None:
        toolbox.tc.track.gdf = toolbox._preview_track_gdf
    elif hasattr(toolbox, "_original_track_gdf"):
        # No modification was made, keep original
        pass

    _cleanup()
    toolbox.plot_track()
    _update_table()


def _revert() -> None:
    """Revert to the backup track."""
    toolbox = app.toolbox["tropical_cyclone"]

    if hasattr(toolbox, "_backup_track_gdf") and toolbox._backup_track_gdf is not None:
        toolbox.tc.track.gdf = toolbox._backup_track_gdf

    _cleanup()
    toolbox.plot_track()
    _update_table()


def _cleanup() -> None:
    """Clean up editing state."""
    toolbox = app.toolbox["tropical_cyclone"]

    draw_layer = app.map.layer["tropical_cyclone"].layer["draw_track"]
    draw_layer.clear()

    app.gui.setvar("tropical_cyclone", "track_modified", False)
    app.map.layer["tropical_cyclone"].layer["cyclone_track"].show()

    toolbox._preview_track_gdf = None
    toolbox._original_track_gdf = None


def _rebuild_track(
    original: gpd.GeoDataFrame, new_coords: list
) -> gpd.GeoDataFrame:
    """Rebuild the track from modified polyline vertices.

    Existing vertices keep their original times and attributes (only
    lon/lat is updated if the vertex was moved). Newly inserted
    vertices get a time midpoint between the two surrounding original
    points, with all attributes linearly interpolated.
    """
    orig_points = np.array(
        [(row.geometry.x, row.geometry.y) for _, row in original.iterrows()]
    )
    n_orig = len(orig_points)
    n_new = len(new_coords)

    # Match new vertices to original vertices using a greedy sequential
    # approach. MapboxDraw preserves original vertex order and only
    # inserts new vertices between them. We use the stored original
    # coordinates (toolbox._original_coords) for exact matching of
    # unmoved vertices, and sequential position for moved ones.
    toolbox = app.toolbox["tropical_cyclone"]
    orig_coords = getattr(toolbox, "_original_coords", None)

    matches = []  # (new_idx, orig_idx or None)
    orig_idx = 0

    for new_idx in range(n_new):
        lon, lat = new_coords[new_idx]

        if orig_idx >= n_orig:
            # All originals matched — remaining are inserted
            matches.append((new_idx, None))
            continue

        # Check exact coordinate match with the current original
        # (unmoved vertex)
        if orig_coords is not None:
            ox, oy = orig_coords[orig_idx]
            if abs(lon - ox) < 1e-10 and abs(lat - oy) < 1e-10:
                matches.append((new_idx, orig_idx))
                orig_idx += 1
                continue

        # Not an exact match — is this a moved original or an inserted point?
        # Count how many new vertices remain vs how many originals remain.
        # If there are exactly enough remaining for all remaining originals,
        # this must be a (moved) original vertex.
        remaining_new = n_new - new_idx
        remaining_orig = n_orig - orig_idx
        if remaining_new == remaining_orig:
            matches.append((new_idx, orig_idx))
            orig_idx += 1
        else:
            matches.append((new_idx, None))

    # Build the new track rows
    rows = []
    for new_idx, orig_match in matches:
        lon, lat = new_coords[new_idx]

        if orig_match is not None:
            # Existing vertex — keep all original attributes, update geometry
            row = original.iloc[orig_match].to_dict()
            row["geometry"] = Point(lon, lat)
            rows.append(row)
        else:
            # Inserted vertex — find surrounding original points
            # Look backwards and forwards in matches for the nearest originals
            prev_orig = None
            next_orig = None
            for j in range(new_idx - 1, -1, -1):
                m = [m for ni, m in matches if ni == j]
                if m and m[0] is not None:
                    prev_orig = m[0]
                    break
            for j in range(new_idx + 1, n_new):
                m = [m for ni, m in matches if ni == j]
                if m and m[0] is not None:
                    next_orig = m[0]
                    break

            if prev_orig is not None and next_orig is not None:
                # Interpolate between the two surrounding original points
                row_prev = original.iloc[prev_orig]
                row_next = original.iloc[next_orig]

                # Time: midpoint
                t_prev = datetime.strptime(row_prev["datetime"], dateformat)
                t_next = datetime.strptime(row_next["datetime"], dateformat)
                t_mid = t_prev + (t_next - t_prev) / 2
                # Round to nearest minute
                t_mid = t_mid.replace(second=0, microsecond=0)

                row = {"datetime": t_mid.strftime(dateformat), "geometry": Point(lon, lat)}

                # Linearly interpolate all numeric columns
                for col in original.columns:
                    if col in ("datetime", "geometry"):
                        continue
                    v_prev = row_prev[col]
                    v_next = row_next[col]
                    try:
                        row[col] = (float(v_prev) + float(v_next)) / 2
                    except (ValueError, TypeError):
                        row[col] = v_prev

                rows.append(row)
            else:
                # Edge case: inserted at start or end — copy nearest
                nearest = prev_orig if prev_orig is not None else (next_orig if next_orig is not None else 0)
                row = original.iloc[nearest].to_dict()
                row["geometry"] = Point(lon, lat)
                rows.append(row)

    try:
        new_track = gpd.GeoDataFrame(rows, crs=4326)
        return new_track
    except Exception as e:
        print(f"Track rebuild failed: {e}")
        return None


def _update_table() -> None:
    """Update the track table from the current tc.track."""
    toolbox = app.toolbox["tropical_cyclone"]
    track_gdf = toolbox.tc.track.gdf
    if track_gdf is not None and len(track_gdf) > 1:
        _update_table_from_gdf(track_gdf)


def _update_table_from_gdf(track_gdf: gpd.GeoDataFrame) -> None:
    """Update the track table GUI variable from a GeoDataFrame."""
    # Build table with all numeric columns + lon/lat from geometry
    exclude = {"geometry", "index"}
    cols = [c for c in track_gdf.columns if c not in exclude]

    df = track_gdf[cols].copy()

    # Format datetime for display: "20260407 180000" → "2026-04-07 18:00"
    if "datetime" in df.columns:
        df["datetime"] = df["datetime"].apply(
            lambda s: datetime.strptime(s, dateformat).strftime("%Y-%m-%d %H:%M")
        )

    # Insert lon/lat after datetime
    dt_idx = 1 if "datetime" in cols else 0
    df.insert(dt_idx, "lon", [round(g.x, 4) for g in track_gdf.geometry])
    df.insert(dt_idx + 1, "lat", [round(g.y, 4) for g in track_gdf.geometry])

    # Round numeric columns
    for col in df.columns:
        if df[col].dtype in (float, np.float64):
            df[col] = df[col].round(2)

    df = df.reset_index(drop=True)
    app.gui.setvar("tropical_cyclone", "track_table", df)
    app.gui.window.update()
