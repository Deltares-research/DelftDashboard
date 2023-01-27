import { map } from './main.js';

export function addMarkerLayer(geojson, markerFile, id) {

	layerID = id;

    if (map.hasImage(id)) {
        map.removeImage(id);
    }

    map.loadImage('icons/' + markerFile,
        (error, image) => {
            if (error) throw error;
            map.addImage(id, image);

            // Add a GeoJSON source with 2 points
            map.addSource(id, {
			      type: 'geojson',
			      data: geojson
            })

            // Add a symbol layer
            map.addLayer({
                'id': id,
                'type': 'symbol',
                'source': id,
                'layout': {
                    'icon-image': id,
                    'icon-size': 0.5,
                    'text-field': ['get', 'title'],
                    'text-font': [
                        'Open Sans Semibold',
                        'Arial Unicode MS Bold'
                    ],
                    'text-offset': [0, 1.25],
                    'text-anchor': 'top'
                }
            });

            // Create a popup, but don't add it to the map yet.
            const popup = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false
            });

            map.on('mouseenter', id, (e) => {

                // Change the cursor style as a UI indicator.
                map.getCanvas().style.cursor = 'pointer';

                // Copy coordinates array.
                const coordinates = e.features[0].geometry.coordinates.slice();
                var description   = e.features[0].properties.hover_popup_text;
                if (e.features[0].properties.hasOwnProperty('hover_popup_width')) {
					popup.setMaxWidth(e.features[0].properties.hover_popup_width);
			    }

                // Ensure that if the map is zoomed out such that multiple
                // copies of the feature are visible, the popup appears
                // over the copy being pointed to.
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Populate the popup and set its coordinates
                // based on the feature found.
                popup.setLngLat(coordinates).setHTML(description).addTo(map);

            });

            map.on('mouseleave', id, () => {
                map.getCanvas().style.cursor = '';
                popup.remove();
            });

        }
    );

//    layerAdded();

}
