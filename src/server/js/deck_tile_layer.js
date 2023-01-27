import { map } from './main.js';

export function addLayer(id, data) {

  var tileSize = 256

  var tileLayer = new deck.MapboxLayer({
    type: deck.TileLayer,
    id: id,
    minZoom: 0,
    maxZoom: 13,
    tileSize: 256,
    data: 'topobathy/{z}/{x}/{y}.png',
    getTileData: async function (tile) {
      const rgb = await getPromise(tile.url);
      const arrLength = 256 * 256 * 4
      for (let i = 0; i < arrLength / 4; i++) {
        const zb = -20000.0 + (rgb.data[i * 4] * 65536 + rgb.data[(i * 4) + 1] * 256 + rgb.data[(i * 4) + 2]) * 0.01;
        const depth = 10.0 - zb
        if (depth>0.0 & zb>-2.0) {
          rgb.data[i * 4] = 0
          rgb.data[(i * 4) + 1] = 0
          rgb.data[(i * 4) + 2] = 255
        } else {
          rgb.data[(i * 4) + 3] = 0
        }
      }
      return createImageBitmap(rgb)
    },

    renderSubLayers: props => {
      const {
        data,
        bbox: {west, south, east, north}
      } = props.tile;
      return new deck.BitmapLayer(props, {
        data: null,
        image: props.tile.data,
        bounds: [west, south, east, north]
      });
    }
  });

  console.log("Adding tiles ...")
  map.addLayer(tileLayer);
  map.getLayer(id)._deck_layer = tileLayer;
}

function getPromise(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = function() {
        var canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        var context = canvas.getContext('2d');
        context.drawImage(img, 0, 0);
        var pixels = context.getImageData(0, 0, img.width, img.height);
//        var bmp = createImageBitmap(pixels)
//        resolve(bmp);
        resolve(pixels);
    }
    img.onerror = function () {
//      console.log('no tile: ' + url)
      reject(null);
    };
    img.src = url
  });
}

export function setData(id, data) {
//  console.log('Finding layer with ID ' + id + ' ...');
  var deck_layer = map.getLayer(id)._deck_layer;
//  console.log(Object.keys(deck_layer));
//  console.log(data);
  deck_layer.setProps({data: data});
}

async function flood(url) {

  console.log('FLOOD');
  console.log(url);

  var pixels = await read_pixels(url)

  return pixels

//return data;
//  const pixel = pixels[0];
//    const height =
//      -20000 + (pixel[0] * 256 * 256 + pixel[1] * 256 + pixel[2]) * 0.01;
//    if (height <= data.level) {
//      pixel[0] = 134;
//      pixel[1] = 203;
//      pixel[2] = 249;
//      pixel[3] = 255;
//  }
//  return pixel;
}
