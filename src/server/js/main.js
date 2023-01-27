//import mapboxgl from './assets/index.9e7ef0f8.js'; // or "const mapboxgl = require('mapbox-gl');"
//console.log('main.js ...');

import mapboxgl from 'https://cdn.skypack.dev/mapbox-gl';
//import deckGl from 'https://cdn.skypack.dev/deck.gl';
//import mapboxMapboxGlDraw from 'https://cdn.skypack.dev/@mapbox/mapbox-gl-draw'

let mapReady;
let mapMoved;
let getMapExtent;
let layerAdded;
export let featureDrawn;
export let featureSelected;
export let featureModified;
let layerName;
let layerGroupName;
export let jsonString;
let idCounter = 0;
let layerID = 'abc';
export let featureId = '';
let activeLayerId;
let drawLayer = {};

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

map.on('moveend', () => {
    onMoveEnd();
});

map.scrollZoom.setWheelZoomRate(1 / 200);

// Web Channel
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.MapBox = channel.objects.MapBox;
  if (typeof MapBox != 'undefined') {
    mapReady          = function() { MapBox.mapReady(jsonString)};
    mapMoved          = function() { MapBox.mapMoved(jsonString)};
    getMapExtent      = function() { MapBox.getMapExtent(jsonString)};
    featureDrawn      = function(coordString, featureId, featureType) { MapBox.featureDrawn(coordString, featureId, featureType)};
    featureModified   = function(coordString, featureId, featureType) { MapBox.featureModified(coordString, featureId, featureType)};
    featureSelected   = function(featureId) { MapBox.featureSelected(featureId)};
  }
});

map.on('load', () => {
    mapLoaded();
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
	      map.removeLayer(id).removeSource(id);
    }
    var legend = document.getElementById("legend" + id);
    if (legend) {
        legend.remove();
    }
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
