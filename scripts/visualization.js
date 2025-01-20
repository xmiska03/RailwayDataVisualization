import {Deck} from '@deck.gl/core';
import {PointCloudLayer} from '@deck.gl/layers';
import {OrbitView} from '@deck.gl/core';
import data from './data.js';
import transf from './transf.js';

console.log("Script visualization.js loaded");
window.step = 0;

const INITIAL_VIEW_STATE = {
  rotationOrbit: 92,
  rotationX: 4.3,
  target: [0, -0.3, 1.0],
  zoom: 9,
  controller: true
};

const VIEW = new OrbitView({
    far: 300,
    fovy: 24,
    controller: true
});

function initializeDeck(data_dict_par) {
  const visCanvas = document.getElementById('visualization-canvas');

  // If the element doesn't exist yet, retry after 100ms
  if (!visCanvas) {
    setTimeout(initializeDeck, 100);
    return;
  }

  //window.data_dict = data_dict

  // Initialize Deck.gl once the div exists
  window.deck = new Deck({
    initialViewState: INITIAL_VIEW_STATE,
    views: [VIEW],
    controller: true,
    layers: [
      new PointCloudLayer({
        id: 'point-cloud-layer',
        data: window.data_dict.layers[0].data,
        getColor: d => [
          d.intensity > 6 ? 7 * (d.intensity - 6) : 0,
          d.intensity > 6 ? 255 - 7 * (d.intensity - 6) : 51 * d.intensity,
          d.intensity > 6 ? 0 : 255 - 51 * d.intensity
        ],
        getPosition: d => [
          d.x * transf[window.step].a + d.y * transf[window.step].b + d.z * transf[window.step].c + transf[window.step].d,
          d.x * transf[window.step].e + d.y * transf[window.step].f + d.z * transf[window.step].g + transf[window.step].h,
          d.x * transf[window.step].i + d.y * transf[window.step].j + d.z * transf[window.step].k + transf[window.step].l,
        ],
        opacity: 0.7,
        pointSize: 10,
        updateTriggers: {
          getPosition: window.step
        }
      })
    ],
    canvas: 'visualization-canvas'
  });
}

function updateLayerPosition(new_position) {
  console.log("called with", new_position);
  var new_pos = new_position
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
    opacity: 0.7,
    pointSize: 10,
    updateTriggers: {
      getPosition: new_pos
    }
  });
  window.deck.setProps({layers: [updatedLayer]});
}

//initializeDeck();

// make the functions global
window.initializeDeck = initializeDeck
window.updateLayerPosition = updateLayerPosition


