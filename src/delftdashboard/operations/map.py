"""Map widget callbacks and background topography management.

Handles map lifecycle events (ready, moved, mouse), background topography
rendering, layer mode updates, cursor resets, CRS changes, and status bar
updates.
"""

import os
import traceback
from typing import Any, Optional

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import xarray as xr
from pyproj import CRS, Transformer
from shapely.geometry import box

from delftdashboard.app import app

transformer_4326_to_3857 = Transformer.from_crs(CRS(4326), CRS(3857), always_xy=True)


def map_ready(*args: Any) -> None:
    """Initialize map layers and select the default model once the map loads.

    Add the main layer group, background topography raster layer, model
    layers, and toolbox layers, then select the first configured model.
    """
    print("Map is ready ! Adding background topography and other layers ...")

    # Find map widget
    element = app.gui.window.find_element_by_id("map")
    app.map = element.widget

    # Connect the documentation webpage widget (built during gui.build)
    info_element = app.gui.window.find_element_by_id("info")
    if info_element is not None:
        app.info.widget = info_element.widget

    # Add main DDB layer
    main_layer = app.map.add_layer("main")

    # Add background topography layer
    main_layer.add_layer("background_topography", type="raster_image")

    # Set update method for topography layer (this is called in the layer's update method!)
    app.map.layer["main"].layer["background_topography"].set_data(
        update_background_topography_data
    )
    app.map.layer["main"].layer["background_topography"].legend_position = "bottom-right"
    app.map.layer["main"].layer["background_topography"].legend_title = "XXX"
    app.map.layer["main"].layer["background_topography"].legend_label = "Elevation (m)"

    # Go to point
    app.map.jump_to(0.0, 0.0, 0.5)

    # Add layers to map (we can only do this after the map has finished loading)
    for name, model in app.model.items():
        model.add_layers()
    for name, toolbox in app.toolbox.items():
        toolbox.add_layers()

    # Default model is first model in config
    model_name = list(app.model.keys())[0]

    # Select this model (this will update the menu and add the toolbox)
    app.model[model_name].select()

    update_statusbar()

    # Need to do this in order to get the correct size of the widgets.
    # Should really be done by Guitares, but for some reason it does not work there.
    app.gui.window.resize()

    app.gui.close_splash()


def map_moved(coords: Any, widget: Any) -> None:
    """Handle map move events.

    Parameters
    ----------
    coords : Any
        New map coordinates after the move.
    widget : Any
        The map widget that triggered the event.
    """
    # Layers are already automatically updated in MapBox


def mouse_moved(x: float, y: float, lon: float, lat: float) -> None:
    """Update the status bar with the current mouse position and elevation.

    Parameters
    ----------
    x : float
        X coordinate in the map's projected CRS.
    y : float
        Y coordinate in the map's projected CRS.
    lon : float
        Longitude in WGS 84.
    lat : float
        Latitude in WGS 84.
    """
    # Check if the map is ready (it's possible that the map is not yet ready
    # when this method is called)
    if not hasattr(app, "map"):
        return

    if app.map.crs.is_geographic:
        app.gui.window.statusbar.set_text("lon", f"Lon : {lon:.6f}")
        app.gui.window.statusbar.set_text("lat", f"Lat : {lat:.6f}")
        app.gui.window.statusbar.set_text("x", "X :")
        app.gui.window.statusbar.set_text("y", "Y :")
    else:
        app.gui.window.statusbar.set_text("lon", f"Lon : {lon:.6f}")
        app.gui.window.statusbar.set_text("lat", f"Lat : {lat:.6f}")
        app.gui.window.statusbar.set_text("x", f"X : {x:.1f}")
        app.gui.window.statusbar.set_text("y", f"Y : {y:.1f}")

    x3857, y3857 = transformer_4326_to_3857.transform(lon, lat)

    z = np.nan
    if hasattr(app, "background_topography") and app.background_topography is not None:
        # Get the z value at the mouse position
        try:
            z = app.background_topography.sel(x=x3857, y=y3857, method="nearest").item()
        except Exception as e:
            z = np.nan
            print(f"Error getting z value: {e}")

    if np.isnan(z):
        app.gui.window.statusbar.set_text("z", "Z : N/A")
    else:
        app.gui.window.statusbar.set_text("z", f"Z : {z:.2f} m")


def update_background_topography_data() -> Optional[xr.DataArray]:
    """Fetch and configure background topography data for the current map extent.

    Query the topography data catalog for the visible area, apply colour
    scale and hillshading settings, and return the resulting DataArray.

    Returns
    -------
    xr.DataArray or None
        The topography raster for the current view, or ``None`` if
        unavailable.
    """
    da = None

    if not app.map.map_extent:
        print("Map extent not yet available ...")
        return

    try:
        auto_update = app.gui.getvar("view_settings", "topography_auto_update")
        visible = app.gui.getvar("view_settings", "topography_visible")
        quality = app.gui.getvar("view_settings", "topography_quality")
        colormap = app.gui.getvar("view_settings", "topography_colormap")
        interp_method = app.gui.getvar("view_settings", "topography_interp_method")
        opacity = app.gui.getvar("view_settings", "topography_opacity")
        zmin = app.gui.getvar("view_settings", "topography_zmin")
        zmax = app.gui.getvar("view_settings", "topography_zmax")
        autoscaling = app.gui.getvar("view_settings", "topography_autoscaling")
        hillshading = app.gui.getvar("view_settings", "topography_hillshading")

        if auto_update and visible:
            coords = app.map.map_extent

            hgt = app.map.view.geometry().height()
            if quality == "high":
                npix = hgt
            elif quality == "medium":
                npix = int(hgt * 0.5)
            else:
                npix = int(hgt * 0.25)

            # Actually easiest to use web mercator
            if coords[1][0] - coords[0][0] > 360.0:
                # If the map is larger than 360 degrees, we can make image of entire world
                coords[0][0] = -180.0
                coords[1][0] = 180.0
            x0, y0 = transformer_4326_to_3857.transform(coords[0][0], coords[0][1])
            x1, y1 = transformer_4326_to_3857.transform(coords[1][0], coords[1][1])
            if x0 > x1:
                # Subtract max size of web mercator
                x0 -= 40075016.68557849
            if x0 < -20037508.342789244:
                # Add max size of web mercator
                x0 += 40075016.68557849
                x1 += 40075016.68557849
            xl = [x0, x1]
            yl = [y0, y1]

            dxy = (yl[1] - yl[0]) / npix
            dataset_name = app.gui.getvar("view_settings", "topography_dataset")

            try:
                geom = gpd.GeoDataFrame(
                    geometry=[box(xl[0], yl[0], xl[1], yl[1])], crs=3857
                )
                da = app.topography_data_catalog.get_rasterdataset(
                    dataset_name, geom=geom, zoom=(dxy, "metre")
                )

                topo_layer = app.map.layer["main"].layer["background_topography"]
                topo_layer.opacity = opacity
                topo_layer.color_scale_auto = autoscaling
                topo_layer.color_scale_symmetric = True
                topo_layer.color_scale_symmetric_side = "min"
                topo_layer.color_scale_cmin = zmin
                topo_layer.color_scale_cmax = zmax
                topo_layer.hillshading = hillshading
                topo_layer.color_map = colormap

                app.background_topography = da

            except Exception:
                print("Error loading background topo ...")
                traceback.print_exc()

                print("Updating background topography done.")

    except:
        print("Error updating background topo ...")
        traceback.print_exc()

    return da


def update() -> None:
    """Reset the cursor and set all model/toolbox layers to inactive or invisible."""
    reset_cursor()
    # Sets all layers to inactive
    for name, model in app.model.items():
        # The active model is set to inactive, the rest to invisible
        if model == app.active_model:
            model.set_layer_mode("inactive")
        else:
            model.set_layer_mode("invisible")
    for name, toolbox in app.toolbox.items():
        # The active toolbox is set to inactive, the rest to invisible
        if toolbox == app.active_toolbox:
            toolbox.set_layer_mode("inactive")
        else:
            toolbox.set_layer_mode("invisible")
    app.map.close_popup()


def reset_cursor() -> None:
    """Reset the map cursor to the default pointer."""
    app.map.set_mouse_default()


def set_crs(crs: CRS) -> None:
    """Set the application and map coordinate reference system.

    Parameters
    ----------
    crs : CRS
        The new coordinate reference system to apply.
    """
    app.crs = crs
    app.map.crs = crs
    update_statusbar()


def show_timeseries_popup(
    ts: pd.DataFrame,
    lon: float,
    lat: float,
    title: str,
    y_label: str = "Value",
    x_label: str = "Time (UTC)",
    line_color: str = "#ff7f0e",
    html_name: str = "timeseries_popup.html",
    width: int = 520,
    height: int = 320,
) -> None:
    """Render a styled plotly line chart and show it as a map popup.

    Parameters
    ----------
    ts : pd.DataFrame
        Time-indexed DataFrame. Each column is drawn as a separate line.
    lon, lat : float
        Map location (EPSG:4326) where the popup anchors.
    title : str
        Plot title.
    y_label, x_label : str
        Axis labels.
    line_color : str
        Colour of the (first) line. Extra columns use plotly defaults.
    html_name : str
        File name written to ``<map_server>/overlays/``.
    width, height : int
        Popup size in pixels.
    """
    fig = px.line(
        ts,
        title=title,
        color_discrete_sequence=[line_color],
    )
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        margin=dict(l=50, r=20, t=50, b=40),
        height=height - 20,
        width=width - 20,
        title=dict(x=0.5, xanchor="center", font=dict(size=14, color="#333")),
        plot_bgcolor="#d9ecf7",
        paper_bgcolor="white",
        showlegend=False,
        yaxis_title=y_label,
        xaxis_title=x_label,
        font=dict(family="Arial, sans-serif", size=11, color="#333"),
    )
    axis_style = dict(
        showgrid=True, gridcolor="white", gridwidth=1,
        zeroline=False, linecolor="#333", ticks="outside",
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    html_path = os.path.join(app.map.server_path, "overlays", html_name)
    fig.write_html(
        html_path,
        include_plotlyjs="cdn",
        full_html=True,
        config={"displayModeBar": False},
    )

    app.map.show_popup(
        lon=lon, lat=lat, url=f"./overlays/{html_name}",
        width=width, height=height,
    )


def update_statusbar() -> None:
    """Update the status bar with the current CRS name and type."""
    if app.crs.is_geographic:
        crstp = f" (geographic) - {app.crs.to_string()}"
    else:
        crstp = f" (projected) - {app.crs.to_string()}"
    app.gui.window.statusbar.set_text("crs_name", f"   {app.crs.name}{crstp}")
