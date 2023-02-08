let MapboxDraw = mpbox.import_mapbox_draw()

import { map, featureDrawn, featureSelected, featureModified } from '/js/main.js';
import { DrawRectangle } from '/js/mapbox-gl-draw-rectangle-mode.js';
import { drawStyles } from '/js/draw_styles.js'
import { SRMode, SRCenter } from '/js/mapbox_gl_draw_scale_rotate_mode.js'

let createListener = dummyFunction
var featureList = []
var layerList = []
let activeLayerId
let modes

// Add extra modes
modes = MapboxDraw.modes;
modes.draw_rectangle = DrawRectangle;
modes.scale_rotate_mode = SRMode

export const draw = new MapboxDraw({displayControlsDefault: false,
                                    userProperties: true,
                                    styles: drawStyles,
                                    modes: modes,
                                   });

export function setDrawEvents() {
  map.on('draw.create', createListener);
  map.on('draw.modechange', modeChanged);
  map.on('draw.selectionchange', selectionChanged);
  map.on('draw.update', featureUpdated);
  // Set mode to simple_select when right-clicking
  map.on("mousedown", (e) => {
    if (e.originalEvent.button === 2) {
      draw.changeMode('simple_select', { featureIds: [] })
    }
  });
}

function dummyFunction(e) {
}

function modeChanged(e) {
  draw.changeMode('simple_select', {featureIds: []});
}

function selectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    var id = feature["id"];
    var featureProps = getFeatureProps(id)
    if (featureProps.shape == "polygon") {
      polygonSelectionChanged(e);
    }
    if (featureProps.shape == "polyline") {
      polylineSelectionChanged(e);
    }
    if (featureProps.shape == "rectangle") {
      rectangleSelectionChanged(e);
    }
  }
}

function featureUpdated(e) {
  var feature=e.features[0];
  if (feature) {
    var id = feature["id"];
    var featureProps = getFeatureProps(id)
    if (featureProps.shape == "polygon") {
      polygonUpdated(e);
    }
    if (featureProps.shape == "rectangle") {
      rectangleUpdated(e);
    }
  }
}

function activateScaleRotateMode(id) {
  draw.changeMode('scale_rotate_mode', {
    featureId: id,
    canScale: true,
    canRotate: true, // only rotation enabled
    canTrash: false, // disable feature delete
    rotatePivot: SRCenter.Center, // rotate around center
    scaleCenter: SRCenter.Opposite, // scale around opposite vertex
    singleRotationPoint: true, // only one rotation point
    rotationPointRadius: 1.2, // offset rotation point
    canSelectFeatures: true,
  });
}

function activateDirectSelectMode(id) {
  draw.changeMode('direct_select', {featureId: id});
}

/// POLYGON \\\

export function drawPolygon(id) {
  setDrawEvents();
  activeLayerId        = id;
  setLayerMode(id, 'active');
  draw.changeMode('draw_polygon');
  map.off('draw.create', createListener);
  createListener = polygonCreated
  map.on('draw.create', createListener);
}

function polygonCreated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  var layerProps = getLayerProps(activeLayerId)
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
  addToFeatureList(id, 'polygon', activeLayerId);
  featureDrawn(coordString, id, 'polygon');
}

function polygonUpdated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  featureModified(coordString, id, 'polygon');
}

function polygonSelectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    // Determine what sort of shape this is
    var id = feature["id"];
    activateDirectSelectMode(id);
    featureSelected(id);
  }
}

/// POLYLINE \\\

export function drawPolyline(id) {
  setDrawEvents();
  activeLayerId         = id;
  setLayerMode(id, 'active');
  draw.changeMode('draw_line_string');
  map.off('draw.create', createListener);
  createListener = polylineCreated
  map.on('draw.create', createListener);
}

function polylineCreated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  var layerProps = getLayerProps(activeLayerId)
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
  addToFeatureList(id, 'polyline', activeLayerId);
  featureDrawn(coordString, id, 'polyline');
}

function polylineUpdated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  featureModified(coordString, id, 'polyline');
}

function polylineSelectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    // Determine what sort of shape this is
    var id = feature["id"];
    activateDirectSelectMode(id);
    featureSelected(id);
  }
}

/// RECTANGLE \\\

export function drawRectangle(id) {
  setDrawEvents();
  activeLayerId = id;
  setLayerMode(id, 'active');
  draw.changeMode('draw_rectangle');
  map.off('draw.create', createListener);
  createListener = rectangleCreated
  map.on('draw.create', createListener);
}

function rectangleCreated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  var layerProps = getLayerProps(activeLayerId);
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
  addToFeatureList(id, 'rectangle', activeLayerId);
  featureDrawn(coordString, id, 'rectangle');
}

function rectangleUpdated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  featureModified(coordString, id, 'rectangle');
}

function rectangleSelectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    // Determine what sort of shape this is
    var id = feature["id"];
    activateScaleRotateMode(id);
    featureSelected(id);
  }
}

/// FEATURES \\\

export function addFeature(id, shape, geometry, layerId) {

  var layerProps = getLayerProps(layerId);

  if (layerProps == null) {
    console.log("No draw layer found with ID " + layerId)
    return
  }

  if (layerProps.mode == "active") {
    // Mode was inactive or invisible, but now active
    addActiveFeature(id, geometry, layerProps.paintProps)

  } else {

    addInactiveFeature(id, geometry, layerProps.paintProps)

    // Set opacity
    if (layerProps.mode == "inactive") {
      map.setLayoutProperty(id, 'visibility', 'visible');
    } else {
      map.setLayoutProperty(id, 'visibility', 'none');
    }
  }

  addToFeatureList(id, shape, layerId);

}

export function addActiveFeature(id, geometry, paintProps) {
  var feature = {
    id: id,
    type: 'Feature',
    properties: {},
    geometry: geometry
  };
  draw.add(feature);
  // Loop through paint props
  for (const [key, value] of Object.entries(paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
}

export function addInactiveFeature(id, geometry, paintProps) {

  map.addSource(id, {
    'type': 'geojson',
    'data': {'type': 'Feature', 'geometry': geometry}
  });
//  var shape = geometry.type
  if (geometry.type == 'LineString') {
    map.addLayer({
      'id': id,
      'type': 'line',
      'source': id,
      'layout': {},
      'paint': {
        'line-color': paintProps.polyline_line_color,
        'line-width': paintProps.polyline_line_width,
        'line-opacity': paintProps.polyline_line_opacity
      }
    });
  }
  if (geometry.type == 'Polygon') {
    map.addLayer({
      'id': id,
      'type': 'fill',
      'source': id,
      'layout': {},
      'paint': {
//        'line-color': paintProps.polygon_line_color,
//        'line-width': paintProps.polygon_line_width,
//        'line-opacity': paintProps.polygon_line_opacity,
        'fill-color': paintProps.polygon_fill_color,
        'fill-opacity': paintProps.polygon_fill_opacity
      }
    });
  }
}

export function deleteFeature(id) {
  // Used when feature is to be completely removed
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }
  // active features
  draw.delete(id);
  removeFromFeatureList(id);
}

export function setFeatureMode(id, mode) {

  var featureProps = getFeatureProps(id);
  var layerProps   = getLayerProps(featureProps.layerId);
  var currentMode  = layerProps.mode;
  var paintProps   = layerProps.paintProps;

  if (currentMode == mode) {
    // Layer is already in requested mode
    return
  }

  // First get feature geometry
  if (currentMode == "active") {
    var geometry = draw.get(id).geometry
    // Delete active feature
    draw.delete(id);
  }
  else {
    var geometry = map.getSource(id)._data.geometry;
    // And now delete geojson layer
    if (map.getLayer(id)) {
      map.removeLayer(id);
    }
    if (map.getSource(id)) {
      map.removeSource(id);
    }
  }
  if (mode == "active") {
    // Mode was inactive or invisible
    addActiveFeature(id, geometry, paintProps)
  } else { // Inactive or invisible mode
    addInactiveFeature(id, geometry, paintProps)
    // Set opacity
    if (mode == "inactive") {
      map.setLayoutProperty(id, 'visibility', 'visible');
    } else {
      map.setLayoutProperty(id, 'visibility', 'none');
    }
  }
}

export function activateFeature(id) {
  // Called from other script
  draw.changeMode('simple_select', { featureIds: [id] })
  var featureProps = getFeatureProps(id)
  if (featureProps.shape == "polygon" || featureProps.shape == "polyline") {
    activateDirectSelectMode(id);
  }
  if (featureProps.shape == "rectangle") {
    activateScaleRotateMode(id);
  }
}

function addToFeatureList(featureId, shape, layerId) {
  featureList.push({
    featureId: featureId,
    shape: shape,
    layerId: layerId
  });
}

function removeFromFeatureList(featureId) {
  featureList.splice(featureList.findIndex(v => v.featureId === featureId), 1);
}

function getFeatureProps(featureId) {
  var props = null
  var index = featureList.findIndex(v => v.featureId === featureId);
  if (index>=0) {props = featureList[index]};
  return props
}


/// LAYERS \\\

export function addLayer(id, mode, paintProps) {
  // Check if this layer already exists
  var props = getLayerProps(id);
  if (props != null) {
    return
  }
  addToLayerList(id, mode, paintProps);
}

export function deleteLayer(layerId) {
  // Loop through features in layer
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].layer == layerId) {
      deleteFeature(featureList[i].featureId)
    }
  }
  removeFromLayerList(layerId);
}

export function setLayerMode(layerId, mode) {
  var layerProps   = getLayerProps(layerId);
  if (layerProps == null) {return}
  if (layerProps.mode == mode) {
    // Layer is already in requested mode
    return
  }
  // Loop through features in layer
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].layerId == layerId) {
      setFeatureMode(featureList[i].featureId, mode)
    }
  }
  setLayerProps(layerId, "mode", mode)
}

function addToLayerList(layerId, mode, paintProps) {
  // Check if layer already exists
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index < 0) {
    layerList.push({layerId: layerId, mode: mode, paintProps: paintProps})
  }
}

function removeFromLayerList(featureId) {
  layerList.splice(layerList.findIndex(v => v.featureId === featureId), 1);
}

function getLayerProps(layerId) {
  var props = null
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index>=0) {props = layerList[index]};
  return props
}

function setLayerProps(layerId, key, val) {
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index>=0) {layerList[index][key] = val};
}


/// OTHER \\\

export function setMouseDefault() {
  draw.changeMode('simple_select', { featureIds: [] })
}
