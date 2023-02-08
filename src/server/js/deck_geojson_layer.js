//let deck = mpbox.import_deck();
// Deck changes the mouse cursor. Need to fix this. Maybe with something like https://github.com/visgl/deck.gl/issues/3522

import { map } from './main.js';

var layerList = []

export function addLayer(id, data) {
  var geoJsonLayer = new deck.MapboxLayer({
    type: deck.GeoJsonLayer,
    id: id,
    pickable: false,
    stroked: true,
    filled: true,
    extruded: true,
    pointType: 'circle',
    lineWidthScale: 1,
    lineWidthMinPixels: 1,
    getLineWidth: 1,
    data: []
  });
  map.addLayer(geoJsonLayer);
  if (data) {geoJsonLayer.setProps({data: data})};
}

export function setData(id, data) {
  // For some reason this does NOT work. Make new Deck layer each time instead
  var layer = map.getLayer(id).implementation;
  layer.setProps({data: data});
}

// The following functions are not used and can be deleted.

export function deleteLayer(layerId) {
  // Loop through features in layer
  removeFromLayerList(layerId);
}

function addToLayerList(layerId, layer) {
  // Check if layer already exists
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index < 0) {
    layerList.push({layerId: layerId, deckLayer: layer})
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
