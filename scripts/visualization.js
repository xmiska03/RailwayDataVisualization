import {Deck} from '@deck.gl/core';
import {PointCloudLayer} from '@deck.gl/layers';
import {OrbitView} from '@deck.gl/core';
import transf from './transf.js';


console.log("Script visualization.js loaded");

function initializeDeck() {

  const INITIAL_VIEW_STATE = window.data_dict.initialViewState;
  
  const VIEW = new OrbitView({
      far: window.data_dict.views[0].far,
      fovy: window.data_dict.views[0].fovy,
      controller: window.data_dict.views[0].controller
  });

  const POINT_CLOUD_LAYER = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: d => [
      d.intensity > 6 ? 7 * (d.intensity - 6) : 0,
      d.intensity > 6 ? 255 - 7 * (d.intensity - 6) : 51 * d.intensity,
      d.intensity > 6 ? 0 : 255 - 51 * d.intensity
    ],
    getPosition: d => [
      d.x * transf[0].a + d.y * transf[0].b + d.z * transf[0].c + transf[0].d,
      d.x * transf[0].e + d.y * transf[0].f + d.z * transf[0].g + transf[0].h,
      d.x * transf[0].i + d.y * transf[0].j + d.z * transf[0].k + transf[0].l,
    ],
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
  });

  window.deck = new Deck({
    initialViewState: INITIAL_VIEW_STATE,
    views: [VIEW],
    layers: [POINT_CLOUD_LAYER],
    canvas: 'visualization-canvas'
  });
}

// to change camera position
function updatePosition() {
  var new_pos = window.position;
  const updatedLayer = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: d => [
      d.intensity > 6 ? 7 * (d.intensity - 6) : 0,
      d.intensity > 6 ? 255 - 7 * (d.intensity - 6) : 51 * d.intensity,
      d.intensity > 6 ? 0 : 255 - 51 * d.intensity
    ],
    getPosition: d => [
      d.x * transf[new_pos].a + d.y * transf[new_pos].b + d.z * transf[new_pos].c + transf[new_pos].d,
      d.x * transf[new_pos].e + d.y * transf[new_pos].f + d.z * transf[new_pos].g + transf[new_pos].h,
      d.x * transf[new_pos].i + d.y * transf[new_pos].j + d.z * transf[new_pos].k + transf[new_pos].l,
    ],
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
    updateTriggers: {
      getPosition: new_pos        // needed when changing getPosition or getColor
    }
  });
  window.deck.setProps({layers: [updatedLayer]});
}

// to change point cloud visibility, point size or opacity
function updatePCLayerProps(visible, point_size, opacity) {
  var pos = window.position;

  //console.log("is_visible:", is_visible);
  //console.log("new_size:", new_size, typeof new_size);
  //console.log("pos:", pos);

  window.data_dict.layers[0].visible = visible;
  window.data_dict.layers[0].pointSize = parseInt(point_size, 10);
  window.data_dict.layers[0].opacity = parseFloat(opacity);

  const updatedLayer = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: d => [
      d.intensity > 6 ? 7 * (d.intensity - 6) : 0,
      d.intensity > 6 ? 255 - 7 * (d.intensity - 6) : 51 * d.intensity,
      d.intensity > 6 ? 0 : 255 - 51 * d.intensity
    ],
    getPosition: d => [
      d.x * transf[pos].a + d.y * transf[pos].b + d.z * transf[pos].c + transf[pos].d,
      d.x * transf[pos].e + d.y * transf[pos].f + d.z * transf[pos].g + transf[pos].h,
      d.x * transf[pos].i + d.y * transf[pos].j + d.z * transf[pos].k + transf[pos].l,
    ],
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
  });
  window.deck.setProps({layers: [updatedLayer]});
}

// make the functions global
window.initializeDeck = initializeDeck;
window.updatePosition = updatePosition;
window.updatePCLayerProps = updatePCLayerProps;

