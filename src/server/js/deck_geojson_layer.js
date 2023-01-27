import { map } from './main.js';

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
    getLineWidth: 1
  });
  map.addLayer(geoJsonLayer);
  if (data) {geoJsonLayer.setProps({data: data})};
  map.getLayer(id)._deck_layer = geoJsonLayer;
 // console.log(Object.keys(geoJsonLayer))
}

export function setData(id, data) {
//  console.log('Finding layer with ID ' + id + ' ...');
  var deck_layer = map.getLayer(id)._deck_layer;
//  console.log(Object.keys(deck_layer));
//  console.log(data);
  deck_layer.setProps({data: data});
}
