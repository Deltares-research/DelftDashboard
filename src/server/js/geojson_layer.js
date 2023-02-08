import { map, featureClicked } from '/js/main.js';

export function addLayer(id, data) {

  let hoveredStateId = null;
  let fillId = "fill_" + id
  let lineId = "line_" + id
  let selectedId = null

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

//  map.addLayer({
//    'id': 'circle_' + id,
//    'type': 'circle',
//    'source': id,
//    'paint': {
//      'circle-radius': 4,
//      'circle-stroke-width': 2,
//      'circle-color': 'red',
//      'circle-stroke-color': 'white'
//    }
//  });

  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': '#000',
      'line-width': 0.5
     }
  });

  map.addLayer({
    id: fillId,
    type: 'fill',
    source: id,
    'paint': {
      'fill-color': 'transparent',
      'fill-outline-color': 'transparent'
    }
  });

  map.addLayer({
    'id': 'points',
    'type': 'symbol',
    'source': id,
    'layout': {
      // get the title name from the source's "title" property
      'text-field': ['get', 'utm_number'],
      'text-font': [
        'Open Sans Semibold',
        'Arial Unicode MS Bold'
      ],
      'text-offset': [0, 0],
      'text-anchor': 'top',
      'text-size': 12
    }
  });
};

export function setData(id, data) {
  console.log('setting data in ' + id);
  console.log(data);
  var source = map.getSource(id);
  source.setData(data);
}
