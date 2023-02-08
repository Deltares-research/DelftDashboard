import { map } from './main.js';

export function addLayer(fileName, id, bounds, colorbar) {

    map.addSource(id, {
        'type': 'image',
        'url': fileName,
        'coordinates': [
        [bounds[0][0], bounds[1][1]],
        [bounds[0][1], bounds[1][1]],
        [bounds[0][1], bounds[1][0]],
        [bounds[0][0], bounds[1][0]]
        ]
    });

    map.addLayer({
        'id': id,
        'source': id,
        'type': 'raster',
        'paint': {
            'raster-resampling': 'nearest'
        }
    }, 'dummy_layer');

    map.setPaintProperty(id,
      'raster-opacity',0.5
    );

    // Legend
    const legend     = document.createElement("div");
    legend.id        = "legend" + id;
    legend.className = "overlay_legend";
    var newSpan = document.createElement('span');
    newSpan.class = 'title';
    newSpan.innerHTML = '<b>' + colorbar["title"] + '</b>';
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));
    for (let i = 0; i < colorbar["contour"].length; i++) {
    let cnt = colorbar["contour"][i]
        var newI = document.createElement('i');
        newI.setAttribute('style','background:' + cnt["color"]);
        legend.appendChild(newI);
        var newSpan = document.createElement('span');
        newSpan.innerHTML = cnt["text"];
        legend.appendChild(newSpan);
        legend.appendChild(document.createElement("br"));
    }
    document.body.appendChild(legend);
}

export function updateLayer(fileName, id, bounds, colorbar) {

    map.getSource(id).updateImage({
        'url': fileName,
        'coordinates': [
        [bounds[0][0], bounds[1][1]],
        [bounds[0][1], bounds[1][1]],
        [bounds[0][1], bounds[1][0]],
        [bounds[0][0], bounds[1][0]]
        ]
    });

    // Legend
    var legend = document.getElementById("legend" + id);
    if (legend) {
        legend.remove();
    }
    var legend     = document.createElement("div");
    legend.id        = "legend" + id;
    legend.className = "overlay_legend";
    var newSpan = document.createElement('span');
    newSpan.class = 'title';
    newSpan.innerHTML = '<b>' + colorbar["title"] + '</b>';
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));
    for (let i = 0; i < colorbar["contour"].length; i++) {
    let cnt = colorbar["contour"][i]
        var newI = document.createElement('i');
        newI.setAttribute('style','background:' + cnt["color"]);
        legend.appendChild(newI);
        var newSpan = document.createElement('span');
        newSpan.innerHTML = cnt["text"];
        legend.appendChild(newSpan);
        legend.appendChild(document.createElement("br"));
    }
    document.body.appendChild(legend);
}

