let mapboxgl = mpbox.import_mapbox_gl()

import { draw, setDrawEvents } from '/js/draw.js';

let mapReady;
let mapMoved;
let getMapExtent;
export let featureDrawn;
export let featureSelected;
export let featureModified;
export let jsonString;
export let featureClicked;

console.log('Adding MapBox map ...')

mapboxgl.accessToken = 'pk.eyJ1IjoibXZhbm9ybW9uZHQiLCJhIjoiY2w1cnkyMHM3MGh3aTNjbjAwajh0NHUyZiJ9.5h1GFWjmJGW5hAK2FFCVDQ';

export const map = new mapboxgl.Map({
  container: 'map', // container ID
  style: 'mapbox://styles/mapbox/streets-v11', // style URL
  center: [0.0, 0.0], // starting position [lng, lat]
  zoom: 2, // starting zoom
//  projection: 'globe' // display the map as a 3D globe
  projection: 'mercator' // display the map as a 3D globe
});

map.scrollZoom.setWheelZoomRate(1 / 200);

// Web Channel
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.MapBox = channel.objects.MapBox;
  if (typeof MapBox != 'undefined') {
    mapReady          = function() { MapBox.mapReady(jsonString)};
    mapMoved          = function() { MapBox.mapMoved(jsonString)};
    getMapExtent      = function() { MapBox.getMapExtent(jsonString)};
    featureClicked    = function(featureId, featureProps) { MapBox.featureClicked(featureId, JSON.stringify(featureProps))};
    featureDrawn      = function(coordString, featureId, featureType) { MapBox.featureDrawn(coordString, featureId, featureType)};
    featureModified   = function(coordString, featureId, featureType) { MapBox.featureModified(coordString, featureId, featureType)};
    featureSelected   = function(featureId) { MapBox.featureSelected(featureId)};
  }
});

map.on('load', () => {
  console.log('Mapbox loaded !');
  // Add dummy layer
  addDummyLayer();
  map.addControl(draw, 'top-left');
  mapLoaded();
});

map.on('moveend', () => {
    onMoveEnd();
});

function mapLoaded(evt) {
  // Get the map extents and tell Python Mapbox object that we're ready
  var extent = map.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight]);
  mapReady();
}

//map.on('style.load', () => {
//  map.setFog({}); // Set the default atmosphere style
//});

function onMoveEnd(evt) {
	// Called after moving map ended
	// Get new map extents
    var extent = map.getBounds();
    var sw = extent.getSouthWest();
    var ne = extent.getNorthEast();
    var bottomLeft = [sw["lng"], sw["lat"]];
    var topRight   = [ne["lng"], ne["lat"]];
    jsonString = JSON.stringify([bottomLeft, topRight]);
    mapMoved();
}



export function removeLayer(id) {
  // Remove layer
  var mapLayer = map.getLayer(id);
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer & source.
    map.removeLayer(id);
  }
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.remove();
  }
}

export function showLayer(id) {
	// Show layer
	var mapLayer = map.getLayer(id);
	map.setLayoutProperty(id, 'visibility', 'visible');
}

export function hideLayer(id) {
	// Show layer
	var mapLayer = map.getLayer(id);
	map.setLayoutProperty(id, 'visibility', 'none');
}

export function getExtent() {
	// Called after moving map ended
	// Get new map extents
    var extent = map.getBounds();
    var sw = extent.getSouthWest();
    var ne = extent.getNorthEast();
    var bottomLeft = [sw["lng"], sw["lat"]];
    var topRight   = [ne["lng"], ne["lat"]];
    jsonString = JSON.stringify([bottomLeft, topRight]);
    getMapExtent();
}

export function setCenter(lon, lat) {
	// Called after moving map ended
	// Get new map extents
	map.setCenter([lon, lat]);
}

export function setZoom(zoom) {
	// Called after moving map ended
	// Get new map extents
	map.setZoom(zoom);
}

export function jumpTo(lon, lat, zoom) {
	// Called after moving map ended
	// Get new map extents
	map.jumpTo({center: [lon, lat], zoom: zoom});
}

export function flyTo(lon, lat, zoom) {
	// Called after moving map ended
	// Get new map extents
	map.flyTo({center: [lon, lat], zoom: zoom});
}

function addDummyLayer() {
  // Add a dummy layer (other layer will be added BEFORE this dummy layer)
  var id = 'dummy_layer';
  map.addSource(id, {
    'type': 'geojson'
  });
  map.addLayer({
    'id': 'dummy_layer',
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': '#000',
      'line-width': 1
    }
  });
}
