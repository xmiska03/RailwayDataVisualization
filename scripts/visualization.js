import {Deck, FirstPersonView} from '@deck.gl/core';
import {PathLayer, PointCloudLayer} from '@deck.gl/layers';

window.deck_initialized = false;
window.frames_cnt = 500;
window.position = 0;
window.animation_running = false;
window.frame_duration = 40;    // in milliseconds
window.gauge_distance = '25';  // 25 meters
window.scale_from = 0;         // boundaries of the point cloud color scale
window.scale_to = 18;
window.scale_middle = 9;
window.camera_offset_x = 0;    // camera offset set manually by the user
window.camera_offset_y = 0;
window.camera_offset_z = 0;
window.camera_offset_yaw = 0;
window.camera_offset_pitch = 0;

// color scales - mapping point intensity to colors
// red - green - blue (from greatest to lowest intensity)
function getColorBGR(d) {
  if (d[3] < window.scale_from) {
    return [0, 0, 255]   // under the scale - blue
  } else if (d[3] > window.scale_to) {
    return [255, 0, 0]   // over the scale - red
  } else if (d[3] < window.scale_middle) {   // on the scale
    return [
      0, 
      Math.floor((d[3] - window.scale_from) / (window.scale_middle - window.scale_from) * 255),
      Math.floor(255 - (d[3] - window.scale_from) / (window.scale_middle - window.scale_from) * 255)
    ]
  } else {
    return [
      Math.floor((d[3] - window.scale_middle) / (window.scale_to - window.scale_middle) * 255),
      Math.floor(255 - (d[3] - window.scale_middle) / (window.scale_to - window.scale_middle) * 255),
      0
    ]
  }
}

function getColorYP(d) {
  if (d[3] < window.scale_from) {
    return [255, 255, 0]   // under the scale - yellow
  } else if (d[3] > window.scale_to) {
    return [255, 0, 255]   // over the scale - purple
  } else {     // on the scale
    return [
      255,
      Math.floor(255 - (d[3] - window.scale_from) / (window.scale_to - window.scale_from) * 255),
      Math.floor((d[3] - window.scale_from) / (window.scale_to - window.scale_from) * 255)
    ]
  }
}

// converts loading gauge distance (in meters) to index in paths data and transformations data
function gauge_distance_to_index(gauge_dist) {
  var i = 0;  // default is '25'
  switch (window.gauge_distance) {
    case '50':
      i = 1;
      break;
    case '75':
      i = 2;
      break;
    case '100':
      i = 3;
      break;
  }
  return i;
}


// transformation for the loading gauge
function gaugeGetPath(d) {
  const pos = window.position;
  const n = gauge_distance_to_index(window.gauge_distance);
  const points = new Array(d.length);
  
  for (let i = 0; i < d.length; i++) {
    //window.gauge_transf[0] - 25m distance
    const x = d[i][0] * window.gauge_transf[n][pos][0][0] + d[i][1] * window.gauge_transf[n][pos][0][1] + d[i][2] * window.gauge_transf[n][pos][0][2] + window.gauge_transf[n][pos][0][3];
    const y = d[i][0] * window.gauge_transf[n][pos][1][0] + d[i][1] * window.gauge_transf[n][pos][1][1] + d[i][2] * window.gauge_transf[n][pos][1][2] + window.gauge_transf[n][pos][1][3];
    const z = d[i][0] * window.gauge_transf[n][pos][2][0] + d[i][1] * window.gauge_transf[n][pos][2][1] + d[i][2] * window.gauge_transf[n][pos][2][2] + window.gauge_transf[n][pos][2][3];

    points[i] = [x, y, z];
  }
  return points;
}

// definifions of the layers

function createPointCloudLayer() {
  return new PointCloudLayer({
    id: 'point-cloud-layer',
    data: window.data_dict.layers[0].data,
    getColor: window.data_dict.layers[0].pointColor === 'bgr'
      ? getColorBGR
      : getColorYP,
    getPosition: (d) => d,
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
    updateTriggers: {      // needed when changing getPosition or getColor (data accessors)
      getColor: [window.scale_from, window.scale_to, window.data_dict.layers[0].pointColor]
    }
  });
}

function createPathLayer() {
  return new PathLayer({
    id: 'path-layer',
    data: window.data_dict.layers[1].data[gauge_distance_to_index(window.gauge_distance)],
    getColor: window.data_dict.layers[1].color,
    getPath: (d) => d,
    getWidth: window.data_dict.layers[1].width,
    billboard: true,     // lines turned towards the camera
    visible: window.data_dict.layers[1].visible,
    updateTriggers: {
      getColor: window.data_dict.layers[1].color
    },
    /*parameters: {
      depthCompare: 'always'    // the layer will be on top of previous layers
    }*/
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
      getPath: [window.position, window.gauge_transf, window.gauge_distance], // needed when changing data accessors
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

  if (window.translations == null) {
    // transformation data was not yet defined by the callback, wait until it is
    setTimeout(initializeDeck, 40);  // try again in 40 ms
    return;
  }

  const INITIAL_VIEW_STATE = {
    bearing: window.data_dict.initialViewState.bearing + window.bearing_pitch[window.position][0],
    pitch: window.data_dict.initialViewState.pitch + window.bearing_pitch[window.position][1],
    position: [
      window.data_dict.initialViewState.position[0] + window.translations[window.position][0],
      window.data_dict.initialViewState.position[1] + window.translations[window.position][1],
      window.data_dict.initialViewState.position[2] + window.translations[window.position][2]
    ]
  };
  
  const VIEW = new FirstPersonView({
    projectionMatrix: window.data_dict.views[0].projectionMatrix,
    controller: window.data_dict.views[0].controller
  });

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
function updateDeck() {
  /*
  The final position of the virtual camera is a combination of:
    - camera offset settings from a file + initial parameters set in the Python code 
      (window.data_dict.initialViewState)
    - custom camera offset set by the user (window.camera_offset_*)
    - current position of the train (determined by the window.position variable, data is in arrays 
      window.translations, window.rotations_inv, window.bearing_pitch)
  */
  const pos = window.position;

  const offset_x = window.data_dict.initialViewState.position[0] + window.camera_offset_x;
  const offset_y = window.data_dict.initialViewState.position[1] + window.camera_offset_y;
  const offset_z = window.data_dict.initialViewState.position[2] + window.camera_offset_z;
  const sum_x = offset_x + window.rotations[pos][0][0] * window.translations[pos][0] + window.rotations[pos][0][1] * window.translations[pos][1] + window.rotations[pos][0][2] * window.translations[pos][2];
  const sum_y = offset_y + window.rotations[pos][1][0] * window.translations[pos][0] + window.rotations[pos][1][1] * window.translations[pos][1] + window.rotations[pos][1][2] * window.translations[pos][2];
  const sum_z = offset_z + window.rotations[pos][2][0] * window.translations[pos][0] + window.rotations[pos][2][1] * window.translations[pos][1] + window.rotations[pos][2][2] * window.translations[pos][2];

  // multiply sum_* by inverse rotation matrix
  const final_x = window.rotations_inv[pos][0][0] * sum_x + window.rotations_inv[pos][0][1] * sum_y + window.rotations_inv[pos][0][2] * sum_z;
  const final_y = window.rotations_inv[pos][1][0] * sum_x + window.rotations_inv[pos][1][1] * sum_y + window.rotations_inv[pos][1][2] * sum_z;
  const final_z = window.rotations_inv[pos][2][0] * sum_x + window.rotations_inv[pos][2][1] * sum_y + window.rotations_inv[pos][2][2] * sum_z;

  // make a new viewstate from the new position
  const INITIAL_VIEW_STATE = {
    bearing: window.data_dict.initialViewState.bearing + window.bearing_pitch[pos][0] + window.camera_offset_yaw,
    pitch: window.data_dict.initialViewState.pitch + window.bearing_pitch[pos][1] + window.camera_offset_pitch,
    position: [final_x, final_y, final_z]
  };
  window.deck.setProps({initialViewState: INITIAL_VIEW_STATE});

  // the loading gauge needs to move to a new position, so it needs a layer update
  window.gauge_layer = createGaugeLayer();
  window.deck.setProps({layers: [window.pc_layer, window.path_layer, window.gauge_layer]});
}


// to change point cloud visibility, point size or opacity
function updatePCLayerProps(visible, point_size, point_color, opacity) {
  window.data_dict.layers[0].visible = visible;
  window.data_dict.layers[0].pointSize = parseInt(point_size, 10);
  window.data_dict.layers[0].pointColor = point_color;
  window.data_dict.layers[0].opacity = parseFloat(opacity);
  updatePCLayer();
}

function updatePCLayer() {
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
  updatePathLayer();
}

function updatePathLayer() {
  window.path_layer = createPathLayer();
  window.deck.setProps({layers: [window.pc_layer, window.path_layer, window.gauge_layer]});
}


// to change loading gauge visibility, line width or color
function updateGaugeLayerProps(visible, line_width, line_color) {
  // convert to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.data_dict.layers[2].visible = visible;
  window.data_dict.layers[2].width = parseInt(line_width, 10);
  window.data_dict.layers[2].color = new_color;

  window.gauge_layer = createGaugeLayer();
  window.deck.setProps({layers: [window.pc_layer, window.path_layer, window.gauge_layer]});
}

function animationStep(now, metadata) {
  const video = document.getElementById('background-video');
  if (window.animation_running) video.requestVideoFrameCallback(animationStep);
  
  // determine new position from video time and camera timestamps
  if (metadata) {
    while (window.camera_timestamps[Math.max(window.position - 1, 0)] < metadata.mediaTime) {
      console.log("mediaTime is:", metadata.mediaTime, "on position", window.position, "timestamp", window.camera_timestamps[window.position]);
      window.position += 1;
    }
  }

  //if (window.animation_running) requestAnimationFrame(animationStep);
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
  window.updateDeck();
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
    window.updateDeck();
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
window.updateDeck = updateDeck;
window.updatePCLayerProps = updatePCLayerProps;
window.updatePCLayer = updatePCLayer;
window.updatePathLayerProps = updatePathLayerProps;
window.updatePathLayer = updatePathLayer;
window.updateGaugeLayerProps = updateGaugeLayerProps;
window.runDeckAnimation = runDeckAnimation;
window.stopDeckAnimation = stopDeckAnimation;
