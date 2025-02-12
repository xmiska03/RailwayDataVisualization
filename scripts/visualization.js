import {Deck, FirstPersonView} from '@deck.gl/core';
import {PointCloudLayer} from '@deck.gl/layers';
import {LineLayer} from '@deck.gl/layers';


window.frames_cnt = 500;
window.position = 0;
window.animation_running = false;
window.frame_duration = 40;   // milliseconds

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
      d.x * window.transf[0][0][0] + d.y * window.transf[0][0][1] + d.z * window.transf[0][0][2] + window.transf[0][0][3],
      d.x * window.transf[0][1][0] + d.y * window.transf[0][1][1] + d.z * window.transf[0][1][2] + window.transf[0][1][3],
      d.x * window.transf[0][2][0] + d.y * window.transf[0][2][1] + d.z * window.transf[0][2][2] + window.transf[0][2][3],
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
      d.from.x * window.transf[0][0][0] + d.from.y * window.transf[0][0][1] + d.from.z * window.transf[0][0][2] + window.transf[0][0][3],
      d.from.x * window.transf[0][1][0] + d.from.y * window.transf[0][1][1] + d.from.z * window.transf[0][1][2] + window.transf[0][1][3],
      d.from.x * window.transf[0][2][0] + d.from.y * window.transf[0][2][1] + d.from.z * window.transf[0][2][2] + window.transf[0][2][3],
    ],
    getTargetPosition: d => [
      d.to.x * window.transf[0][0][0] + d.to.y * window.transf[0][0][1] + d.to.z * window.transf[0][0][2] + window.transf[0][0][3],
      d.to.x * window.transf[0][1][0] + d.to.y * window.transf[0][1][1] + d.to.z * window.transf[0][1][2] + window.transf[0][1][3],
      d.to.x * window.transf[0][2][0] + d.to.y * window.transf[0][2][1] + d.to.z * window.transf[0][2][2] + window.transf[0][2][3],
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
      d.x * window.transf[new_pos][0][0] + d.y * window.transf[new_pos][0][1] + d.z * window.transf[new_pos][0][2] + window.transf[new_pos][0][3],
      d.x * window.transf[new_pos][1][0] + d.y * window.transf[new_pos][1][1] + d.z * window.transf[new_pos][1][2] + window.transf[new_pos][1][3],
      d.x * window.transf[new_pos][2][0] + d.y * window.transf[new_pos][2][1] + d.z * window.transf[new_pos][2][2] + window.transf[new_pos][2][3],
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
      d.from.x * window.transf[new_pos][0][0] + d.from.y * window.transf[new_pos][0][1] + d.from.z * window.transf[new_pos][0][2] + window.transf[new_pos][0][3],
      d.from.x * window.transf[new_pos][1][0] + d.from.y * window.transf[new_pos][1][1] + d.from.z * window.transf[new_pos][1][2] + window.transf[new_pos][1][3],
      d.from.x * window.transf[new_pos][2][0] + d.from.y * window.transf[new_pos][2][1] + d.from.z * window.transf[new_pos][2][2] + window.transf[new_pos][2][3],
    ],
    getTargetPosition: d => [
      d.to.x * window.transf[new_pos][0][0] + d.to.y * window.transf[new_pos][0][1] + d.to.z * window.transf[new_pos][0][2] + window.transf[new_pos][0][3],
      d.to.x * window.transf[new_pos][1][0] + d.to.y * window.transf[new_pos][1][1] + d.to.z * window.transf[new_pos][1][2] + window.transf[new_pos][1][3],
      d.to.x * window.transf[new_pos][2][0] + d.to.y * window.transf[new_pos][2][1] + d.to.z * window.transf[new_pos][2][2] + window.transf[new_pos][2][3],
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
      d.x * window.transf[pos][0][0] + d.y * window.transf[pos][0][1] + d.z * window.transf[pos][0][2] + window.transf[pos][0][3],
      d.x * window.transf[pos][1][0] + d.y * window.transf[pos][1][1] + d.z * window.transf[pos][1][2] + window.transf[pos][1][3],
      d.x * window.transf[pos][2][0] + d.y * window.transf[pos][2][1] + d.z * window.transf[pos][2][2] + window.transf[pos][2][3],
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
      d.from.x * window.transf[new_pos][0][0] + d.from.y * window.transf[new_pos][0][1] + d.from.z * window.transf[new_pos][0][2] + window.transf[new_pos][0][3],
      d.from.x * window.transf[new_pos][1][0] + d.from.y * window.transf[new_pos][1][1] + d.from.z * window.transf[new_pos][1][2] + window.transf[new_pos][1][3],
      d.from.x * window.transf[new_pos][2][0] + d.from.y * window.transf[new_pos][2][1] + d.from.z * window.transf[new_pos][2][2] + window.transf[new_pos][2][3],
    ],
    getTargetPosition: d => [
      d.to.x * window.transf[new_pos][0][0] + d.to.y * window.transf[new_pos][0][1] + d.to.z * window.transf[new_pos][0][2] + window.transf[new_pos][0][3],
      d.to.x * window.transf[new_pos][1][0] + d.to.y * window.transf[new_pos][1][1] + d.to.z * window.transf[new_pos][1][2] + window.transf[new_pos][1][3],
      d.to.x * window.transf[new_pos][2][0] + d.to.y * window.transf[new_pos][2][1] + d.to.z * window.transf[new_pos][2][2] + window.transf[new_pos][2][3],
    ],
    getWidth: window.data_dict.layers[1].width,
    visible: window.data_dict.layers[1].visible
  });
  window.line_layer = updatedLineLayer;
  
  window.deck.setProps({layers: [window.pc_layer, updatedLineLayer]});
}

function animationStep(now, metadata) {
  const video = document.getElementById('background-video');
  if (window.animation_running) video.requestVideoFrameCallback(animationStep);
  
  console.log("called after: ", Date.now() - window.call_time, "ms");  // for debugging
  window.call_time = Date.now();
  
  // calculate new position from video time
  if (metadata) window.position = Math.floor(metadata.mediaTime * 25);
  
  //console.log("animationStep - video.currentTime is: ", video.currentTime);
  //if (metadata) console.log("animationStep - metadata.mediaTime is: ", metadata.mediaTime);
  console.log("animationStep - setting position: ", window.position);
 
  if (window.position >= window.frames_cnt - 2) {  // end of animation
    if (window.animation_running == true) {
      window.animation_running = false;
      const icon = document.getElementById("play-button").querySelector("i");  // change icon
      icon.classList.toggle("bi-play-fill");
      icon.classList.toggle("bi-pause-fill");
    }
    
    window.position = window.frames_cnt - 1;           // show the last frame
    // this has to be done with the elements so that Dash knows about the changes
    dash_clientside.set_props("camera-position-input", {value: window.position});
    dash_clientside.set_props("camera-position-slider-input", {value: window.position});
    const time_sec = Math.floor(video.currentTime - 0.001); // get time in seconds, round to whole number
    const minutes = Math.floor(time_sec / 60);
    const seconds = time_sec % 60;
    const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
    dash_clientside.set_props("current-time-div", {children: label});
  }
 
  // update the visualization
  window.updatePosition();
  // update GUI elements
  document.getElementById("camera-position-input").value = window.position;         // update input value
  document.getElementById("camera-position-slider-input").value = window.position;  // update slider value
  const time_sec = Math.floor(Math.max(video.currentTime - 0.001, 0)); // get time in seconds, round to whole number
  const minutes = Math.floor(time_sec / 60);
  const seconds = time_sec % 60;                                                    // update time label
  document.getElementById("current-time-div").innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function runDeckAnimation() {
  if (window.position >= window.frames_cnt - 2) {  // it is at the end, start again from the beginning
    const video = document.getElementById('background-video');
    video.currentTime = 0;
    window.position = 0;
    window.updatePosition();
  }
  
  window.animation_running = true;
  animationStep();
}

function stopDeckAnimation() {
  window.animation_running = false;

  setTimeout(() => {
    // this has to be done with the GUI elements so that Dash knows about the changes
    dash_clientside.set_props("camera-position-input", {value: window.position});
    dash_clientside.set_props("camera-position-slider-input", {value: window.position});
    const video = document.getElementById('background-video');
    const time_sec = Math.floor(video.currentTime - 0.001); // get time in seconds, round to whole number
    const minutes = Math.floor(time_sec / 60);
    const seconds = time_sec % 60;
    const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
    dash_clientside.set_props("current-time-div", {children: label});
  }, 500);
}

// make the functions global
window.initializeDeck = initializeDeck;
window.updatePosition = updatePosition;
window.updatePCLayerProps = updatePCLayerProps;
window.updateLineLayerProps = updateLineLayerProps;
window.runDeckAnimation = runDeckAnimation;
window.stopDeckAnimation = stopDeckAnimation;
