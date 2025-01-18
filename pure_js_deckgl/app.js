import {Deck} from '@deck.gl/core';
import {PointCloudLayer} from '@deck.gl/layers';
import {OrbitView} from '@deck.gl/core';
import data from './data.js';
import transf from './transf.js';

let step = 0;

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

const deck = new Deck({
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
        d.x * transf[step].a + d.y * transf[step].b + d.z * transf[step].c + transf[step].d,
        d.x * transf[step].e + d.y * transf[step].f + d.z * transf[step].g + transf[step].h,
        d.x * transf[step].i + d.y * transf[step].j + d.z * transf[step].k + transf[step].l,
      ],
      opacity: 0.7,
      pointSize: 10,
      updateTriggers: {
        getPosition: step
      }
    })
  ]
});

function updateLayerPosition() {
  step = (step + 1) % 500;
  const updatedLayer = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: data,
    getColor: d => [
      d.intensity > 6 ? 7 * (d.intensity - 6) : 0,
      d.intensity > 6 ? 255 - 7 * (d.intensity - 6) : 51 * d.intensity,
      d.intensity > 6 ? 0 : 255 - 51 * d.intensity
    ],
    getPosition: d => [
      d.x * transf[step].a + d.y * transf[step].b + d.z * transf[step].c + transf[step].d,
      d.x * transf[step].e + d.y * transf[step].f + d.z * transf[step].g + transf[step].h,
      d.x * transf[step].i + d.y * transf[step].j + d.z * transf[step].k + transf[step].l,
    ],
    opacity: 0.7,
    pointSize: 10,
    updateTriggers: {
      getPosition: step
    }
  });
  deck.setProps({layers: [updatedLayer]});
}

setInterval(updateLayerPosition, 40);

