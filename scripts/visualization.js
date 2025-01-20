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

function initializeDeck() {
  const visCanvas = document.getElementById('visualization-canvas');

  // If the element doesn't exist yet, retry after 100ms
  if (!visCanvas) {
    setTimeout(initializeDeck, 100);
    return;
  }

  // Initialize Deck.gl once the div exists
  window.deck = new Deck({
    initialViewState: INITIAL_VIEW_STATE,
    views: [VIEW],
    controller: true,
    layers: [
      new PointCloudLayer({
        id: 'point-cloud-layer',
        data: data,
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

function updateLayerPosition() {
  window.step = (window.step + 10) % 500;
  const updatedLayer = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: data,
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
  });
  window.deck.setProps({layers: [updatedLayer]});
}

initializeDeck();

// make the functions global
window.initializeDeck = initializeDeck
window.updateLayerPosition = updateLayerPosition


