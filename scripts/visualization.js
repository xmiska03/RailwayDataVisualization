import {Deck, FirstPersonView} from '@deck.gl/core';
import {PointCloudLayer} from '@deck.gl/layers';
import {LineLayer} from '@deck.gl/layers';
import transf from './transf.js';


window.frames_cnt = 500;
window.position = 0;
window.animation_running = false;
window.frame_rate = 40;

// color scales - mapping point intensity to colors
// red - green - blue (from greatest to lowest intensity)
function getColorRGB(d) {
  return [
    d.intensity > 6 ? 7 * (d.intensity - 6) : 0,
    d.intensity > 6 ? 255 - 7 * (d.intensity - 6) : 51 * d.intensity,
    d.intensity > 6 ? 0 : 255 - 51 * d.intensity
  ];
}

function getColorRB(d) {
  return [
    6 * d.intensity,
    0,
    255 - 6 * d.intensity
  ];
}

function getColorYR(d) {
  return [
    255,
    6 * d.intensity,
    0
  ];
}


function initializeDeck() {

  const INITIAL_VIEW_STATE = window.data_dict.initialViewState;
  
  const VIEW = new FirstPersonView({
      far: window.data_dict.views[0].far,
      fovy: window.data_dict.views[0].fovy,
      controller: window.data_dict.views[0].controller
  });

  window.pc_layer = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: window.data_dict.layers[0].pointColor === 'rgb'
      ? getColorRGB 
      : window.data_dict.layers[0].pointColor === 'rb' 
        ? getColorRB
        : getColorPY,
    getPosition: d => [
      d.x * transf[0].a + d.y * transf[0].b + d.z * transf[0].c + transf[0].d,
      d.x * transf[0].e + d.y * transf[0].f + d.z * transf[0].g + transf[0].h,
      d.x * transf[0].i + d.y * transf[0].j + d.z * transf[0].k + transf[0].l,
    ],
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
  });

  window.line_layer = new LineLayer({
    id: 'line-layer',
    data: window.data_dict.layers[1].data,
    getColor: window.data_dict.layers[1].color,
    getSourcePosition: d => [
      d.from.x * transf[0].a + d.from.y * transf[0].b + d.from.z * transf[0].c + transf[0].d,
      d.from.x * transf[0].e + d.from.y * transf[0].f + d.from.z * transf[0].g + transf[0].h,
      d.from.x * transf[0].i + d.from.y * transf[0].j + d.from.z * transf[0].k + transf[0].l,
    ],
    getTargetPosition: d => [
      d.to.x * transf[0].a + d.to.y * transf[0].b + d.to.z * transf[0].c + transf[0].d,
      d.to.x * transf[0].e + d.to.y * transf[0].f + d.to.z * transf[0].g + transf[0].h,
      d.to.x * transf[0].i + d.to.y * transf[0].j + d.to.z * transf[0].k + transf[0].l,
    ],
    getWidth: window.data_dict.layers[1].width,
    visible: window.data_dict.layers[1].visible
  });

  window.deck = new Deck({
    initialViewState: INITIAL_VIEW_STATE,
    views: [VIEW],
    layers: [window.pc_layer, window.line_layer],
    canvas: 'visualization-canvas'
  });
}


// to change camera position
function updatePosition() {
  let new_pos = window.position;
  const updatedPCLayer = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: window.data_dict.layers[0].pointColor === 'rgb'
      ? getColorRGB 
      : window.data_dict.layers[0].pointColor === 'rb' 
        ? getColorRB
        : getColorYR,
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
  window.pc_layer = updatedPCLayer;

  const updatedLineLayer = new LineLayer({
    id: 'line-layer',
    data: window.data_dict.layers[1].data,
    getColor: window.data_dict.layers[1].color,
    getSourcePosition: d => [
      d.from.x * transf[new_pos].a + d.from.y * transf[new_pos].b + d.from.z * transf[new_pos].c + transf[new_pos].d,
      d.from.x * transf[new_pos].e + d.from.y * transf[new_pos].f + d.from.z * transf[new_pos].g + transf[new_pos].h,
      d.from.x * transf[new_pos].i + d.from.y * transf[new_pos].j + d.from.z * transf[new_pos].k + transf[new_pos].l,
    ],
    getTargetPosition: d => [
      d.to.x * transf[new_pos].a + d.to.y * transf[new_pos].b + d.to.z * transf[new_pos].c + transf[new_pos].d,
      d.to.x * transf[new_pos].e + d.to.y * transf[new_pos].f + d.to.z * transf[new_pos].g + transf[new_pos].h,
      d.to.x * transf[new_pos].i + d.to.y * transf[new_pos].j + d.to.z * transf[new_pos].k + transf[new_pos].l,
    ],
    getWidth: window.data_dict.layers[1].width,
    visible: window.data_dict.layers[1].visible,
    updateTriggers: {
      getSourcePosition: new_pos,        // needed when changing getPosition or getColor
      getTargetPosition: new_pos
    }
  });
  window.line_layer = updatedLineLayer;

  window.deck.setProps({layers: [updatedPCLayer, updatedLineLayer]});
}


// to change point cloud visibility, point size or opacity
function updatePCLayerProps(visible, point_size, point_color, opacity) {
  var pos = window.position;

  window.data_dict.layers[0].visible = visible;
  window.data_dict.layers[0].pointSize = parseInt(point_size, 10);
  window.data_dict.layers[0].pointColor = point_color;
  window.data_dict.layers[0].opacity = parseFloat(opacity);

  const updatedPCLayer = new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: window.data_dict.layers[0].pointColor === 'rgb'
              ? getColorRGB 
              : window.data_dict.layers[0].pointColor === 'rb' 
                ? getColorRB
                : getColorYR,
    getPosition: d => [
      d.x * transf[pos].a + d.y * transf[pos].b + d.z * transf[pos].c + transf[pos].d,
      d.x * transf[pos].e + d.y * transf[pos].f + d.z * transf[pos].g + transf[pos].h,
      d.x * transf[pos].i + d.y * transf[pos].j + d.z * transf[pos].k + transf[pos].l,
    ],
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
    updateTriggers: {
      getColor: point_color        // needed when changing getPosition or getColor
    }
  });
  window.pc_layer = updatedPCLayer;

  window.deck.setProps({layers: [updatedPCLayer, window.line_layer]});
}


// to change vector data visibility
function updateLineLayerProps(visible) {
  var new_pos = window.position;

  window.data_dict.layers[1].visible = visible;

  const updatedLineLayer = new LineLayer({
    id: 'line-layer',
    data: window.data_dict.layers[1].data,
    getColor: window.data_dict.layers[1].color,
    getSourcePosition: d => [
      d.from.x * transf[new_pos].a + d.from.y * transf[new_pos].b + d.from.z * transf[new_pos].c + transf[new_pos].d,
      d.from.x * transf[new_pos].e + d.from.y * transf[new_pos].f + d.from.z * transf[new_pos].g + transf[new_pos].h,
      d.from.x * transf[new_pos].i + d.from.y * transf[new_pos].j + d.from.z * transf[new_pos].k + transf[new_pos].l,
    ],
    getTargetPosition: d => [
      d.to.x * transf[new_pos].a + d.to.y * transf[new_pos].b + d.to.z * transf[new_pos].c + transf[new_pos].d,
      d.to.x * transf[new_pos].e + d.to.y * transf[new_pos].f + d.to.z * transf[new_pos].g + transf[new_pos].h,
      d.to.x * transf[new_pos].i + d.to.y * transf[new_pos].j + d.to.z * transf[new_pos].k + transf[new_pos].l,
    ],
    getWidth: window.data_dict.layers[1].width,
    visible: window.data_dict.layers[1].visible
  });
  window.line_layer = updatedLineLayer;
  
  window.deck.setProps({layers: [window.pc_layer, updatedLineLayer]});
}

function animationStep() {
  if (!window.animation_running) return;

  const video = document.getElementById('background-video');
  const videoTime = video.currentTime*1000;   // seconds to miliseconds
  
  // calculate new position from video time
  window.position = Math.floor(videoTime / window.frame_rate);
  //console.log("video time: ", videoTime);
  //console.log("position: ", window.position);
 
  if (window.position >= window.frames_cnt) {                                // end of animation
    window.position = window.frames_cnt - 1;                                 // show the last frame
    window.animation_running = false;
    const icon = document.getElementById("play-button").querySelector("i");  // change icon
    icon.classList.toggle("bi-play-fill");
    icon.classList.toggle("bi-pause-fill");
    // this has to be done with the frame number input element so that Dash knows about the changes
    dash_clientside.set_props("camera-position-input", {value: window.position});
  }
 
  // update the visualization
  window.updatePosition();
  // update GUI elements
  //console.log("script setting inputs to: ", window.position);
  document.getElementById("camera-position-input").value = window.position;         // update input value
  document.getElementById("camera-position-slider-input").value = window.position;  // update slider value
  const time_sec = Math.floor(video.currentTime); // get time in seconds, round to whole number
  const minutes = Math.floor(time_sec / 60);
  const seconds = time_sec % 60;                                                    // update time label
  document.getElementById("current-time-div").innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  // plan the next step
  const timeToNextFrame = (window.position + 1) * window.frame_rate - videoTime;
  //console.log("set timeout to: ", timeToNextFrame);
  setTimeout(animationStep, Math.max(0, timeToNextFrame));
}

function runDeckAnimation() {
  if (window.position >= window.frames_cnt - 1) {  // it is at the end, start again from the beginning
    window.position = 0;
  }
  
  window.animation_running = true;
  animationStep();
}

function stopDeckAnimation() {
  window.animation_running = false;
  // TODO: this has to be done with the frame number input element so that Dash knows about the changes
  dash_clientside.set_props("camera-position-input", {value: window.position});
}

// make the functions global
window.initializeDeck = initializeDeck;
window.updatePosition = updatePosition;
window.updatePCLayerProps = updatePCLayerProps;
window.updateLineLayerProps = updateLineLayerProps;
window.runDeckAnimation = runDeckAnimation;
window.stopDeckAnimation = stopDeckAnimation;
