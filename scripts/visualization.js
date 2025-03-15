import {Deck, FirstPersonView, Viewport, OrbitView, View} from '@deck.gl/core';
import {PathLayer, PointCloudLayer,} from '@deck.gl/layers';

window.deck_initialized = false;
window.frames_cnt = 500;
window.position = 0;
window.animation_running = false;
window.frame_duration = 40;   // in milliseconds
window.gauge_distance = 100;   // in virtual camera positions

// color scales - mapping point intensity (d[3]) to colors
// red - green - blue (from greatest to lowest intensity)
function getColorRGB(d) {
  return [
    d[3] > 6 ? 7 * (d[3] - 6) : 0,
    d[3] > 6 ? 255 - 7 * (d[3] - 6) : 51 * d[3],
    d[3] > 6 ? 0 : 255 - 51 * d[3]
  ];
}

function getColorRB(d) {
  return [
    6 * d[3],
    0,
    255 - 6 * d[3]
  ];
}

function getColorYR(d) {
  return [
    255,
    6 * d[3],
    0
  ];
}

// for the loading gauge layer
function gaugeGetPath(d) {
  const gauge_pos = Math.min(window.position + window.gauge_distance, frames_cnt - 1);
  const points = new Array(d.length);
  
  for (let i = 0; i < d.length; i++) {
    const x = d[i][0] * window.transf_inv[gauge_pos][0][0] + (d[i][1] - 1.2) * window.transf_inv[gauge_pos][0][1] + d[i][2] * window.transf_inv[gauge_pos][0][2] + window.transf_inv[gauge_pos][0][3];
    const y = d[i][0] * window.transf_inv[gauge_pos][1][0] + (d[i][1] - 1.2) * window.transf_inv[gauge_pos][1][1] + d[i][2] * window.transf_inv[gauge_pos][1][2] + window.transf_inv[gauge_pos][1][3];
    const z = d[i][0] * window.transf_inv[gauge_pos][2][0] + (d[i][1] - 1.2) * window.transf_inv[gauge_pos][2][1] + d[i][2] * window.transf_inv[gauge_pos][2][2] + window.transf_inv[gauge_pos][2][3];
    
    points[i] = [x, y, z];
  }
  return points;
}

// definifions of the layers

function createPointCloudLayer() {
  return new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: window.data_dict.layers[0].pointColor === 'rgb'
      ? getColorRGB 
      : window.data_dict.layers[0].pointColor === 'rb' 
        ? getColorRB
        : getColorYR,
    getPosition: (d) => d,
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
    updateTriggers: {
      getPosition: [/*window.position,*/ window.transf],    // needed when changing getPosition or getColor
      getColor: window.data_dict.layers[0].pointColor
    }
  });
}

function createPathLayer() {
  return new PathLayer({
    id: 'path-layer',
    data: window.data_dict.layers[1].data,
    getColor: window.data_dict.layers[1].color,
    getPath: (d) => d,
    getWidth: window.data_dict.layers[1].width,
    billboard: true,     // lines turned towards the camera
    visible: window.data_dict.layers[1].visible,
    updateTriggers: {
      getPath: [/*window.position,*/ window.transf],  // needed when changing data accessors
      getColor: window.data_dict.layers[1].color
    },
    parameters: {
      depthCompare: 'always'    // the layer will be on top of previous layers
    }
  });
}

function createGaugeLayer() {
  return new PathLayer({
    id: 'gauge-layer',
    data: window.data_dict.layers[2].data,
    getColor: window.data_dict.layers[2].color,
    getPath: gaugeGetPath,
    getWidth: window.data_dict.layers[2].width,
    billboard: true,
    visible: window.data_dict.layers[2].visible,
    updateTriggers: {
      getPath: [/*window.position*/, window.transf, window.gauge_distance], // needed when changing data accessors
      getColor: window.data_dict.layers[2].color
    },
    parameters: {
      depthCompare: 'always'    // the layer will be on top of previous layers
    }
  });
}

// used for initializing the visualization
// and also reinitializing when new point cloud data is uploaded 
function initializeDeck() {

  if (window.transf == null) {
    // transformation data was not yet defined by the callback, wait until it is
    setTimeout(initializeDeck, 40);  // try again in 40 ms
    return;
  }

  const VIEW = new FirstPersonView({
    projectionMatrix: window.data_dict.views[0].projectionMatrix,
    controller: window.data_dict.views[0].controller
  });

  const INITIAL_VIEW_STATE = {
    bearing: window.data_dict.initialViewState.bearing,
    pitch: window.data_dict.initialViewState.pitch,
    position: [
      window.data_dict.initialViewState.position[0] + window.translations[window.position][2],
      window.data_dict.initialViewState.position[1] + window.translations[window.position][0],
      window.data_dict.initialViewState.position[2] + window.translations[window.position][1]
    ]
  };

  window.pc_layer = createPointCloudLayer();
  window.path_layer = createPathLayer();
  window.gauge_layer = createGaugeLayer();

  // the context is created manually to specify "preserveDrawingBuffer: true".
  // that is needed to enable reading the pixels of the visualisation for applying distortion.
  const canvas = document.getElementById("visualization-canvas");
  const context = canvas.getContext("webgl2", { preserveDrawingBuffer: true, premultipliedAlpha: false });

  window.deck = new Deck({
    initialViewState: INITIAL_VIEW_STATE,
    views: [VIEW],
    layers: [window.pc_layer, window.path_layer, window.gauge_layer],
    canvas: 'visualization-canvas',
    context: context
  });

  window.deck_initialized = true;
}


// to change camera position
function updatePosition() {
  // make a new viewstate from the new position
  const INITIAL_VIEW_STATE = {
    bearing: window.data_dict.initialViewState.bearing,
    pitch: window.data_dict.initialViewState.pitch,
    position: [
      window.data_dict.initialViewState.position[0] + window.translations[window.position][2],
      window.data_dict.initialViewState.position[1] + window.translations[window.position][0],
      window.data_dict.initialViewState.position[2] + window.translations[window.position][1]
    ]
  };

  window.deck.setProps({initialViewState: INITIAL_VIEW_STATE});
}


// to change point cloud visibility, point size or opacity
function updatePCLayerProps(visible, point_size, point_color, opacity) {
  window.data_dict.layers[0].visible = visible;
  window.data_dict.layers[0].pointSize = parseInt(point_size, 10);
  window.data_dict.layers[0].pointColor = point_color;
  window.data_dict.layers[0].opacity = parseFloat(opacity);

  window.pc_layer = createPointCloudLayer();

  window.deck.setProps({layers: [window.pc_layer, window.path_layer, window.gauge_layer]});
}


// to change vector data visibility, line width or color
function updatePathLayerProps(visible, line_width, line_color) {
  // convert to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.data_dict.layers[1].visible = visible;
  window.data_dict.layers[1].width = parseInt(line_width, 10);
  window.data_dict.layers[1].color = new_color;

  window.path_layer = createPathLayer();
  
  window.deck.setProps({layers: [window.pc_layer, window.path_layer, window.gauge_layer]});
}


// to change loading gauge visibility, distance, line width or color
function updateGaugeLayerProps(visible, distance, line_width, line_color) {
  // convert to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.data_dict.layers[2].visible = visible;
  window.gauge_distance = distance;
  window.data_dict.layers[2].width = parseInt(line_width, 10);
  window.data_dict.layers[2].color = new_color;

  window.gauge_layer = createGaugeLayer();
  
  window.deck.setProps({layers: [window.pc_layer, window.path_layer, window.gauge_layer]});
}


function animationStep(now, metadata) {
  const video = document.getElementById('background-video');
  if (window.animation_running) video.requestVideoFrameCallback(animationStep);
  
  console.log("called after: ", Date.now() - window.call_time, "ms");  // for debugging
  window.call_time = Date.now();
  
  // calculate new position from video time
  if (metadata) {
    if (window.animation_running) {
      // needs to be 1 frame forward to be in sync with the video
      window.position = Math.floor(metadata.mediaTime * 25) + 1;
    } else {
      // the final position when stopping needs to be exact
      window.position = Math.floor(metadata.mediaTime * 25);
    }
  }

  /*const video = document.getElementById('background-video');
  if (window.animation_running) requestAnimationFrame(animationStep);
  //if (window.animation_running) setTimeout(animationStep, 40);

  console.log("called after: ", Date.now() - window.call_time, "ms");  // for debugging
  window.call_time = Date.now();
  
  // calculate new position from video time
  if (window.animation_running) {
    // needs to be 1 frame forward to be in sync with the video
    window.position = Math.floor(video.currentTime * 25) + 1;
  } else {
    // the final position when stopping needs to be exact
    window.position = Math.floor(video.currentTime * 25);
  }
  */

  //console.log("animationStep - video.currentTime is: ", video.currentTime);
  //if (metadata) console.log("animationStep - metadata.mediaTime is: ", metadata.mediaTime);
  //console.log("animationStep - setting position: ", window.position);
 
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
window.updatePathLayerProps = updatePathLayerProps;
window.updateGaugeLayerProps = updateGaugeLayerProps;
window.runDeckAnimation = runDeckAnimation;
window.stopDeckAnimation = stopDeckAnimation;
