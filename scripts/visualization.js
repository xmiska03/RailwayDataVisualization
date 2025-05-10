/**
 * @fileoverview Creates and manages the deck.gl visualization and the train movement animation.
 * @module Visualization
 */
import {Deck, FirstPersonView} from '@deck.gl/core';
import {PathLayer, PointCloudLayer} from '@deck.gl/layers';

/**
 * Whether the visualization (Deck object window.deck) is already initialized.
 * @type {boolean}
 */
window.deck_initialized = false;
/**
 * Number of available positions.
 * @type {number}
 */
window.frames_cnt = 500;
/**
 * Current position.
 * @type {number}
 */
window.position = 0;
/**
 * Current position in point cloud chunks.
 * @type {number}
 */
window.pcl_position = 0;
/**
 * Whether the animation is currently running.
 * @type {boolean}
 */
window.animation_running = false;
/**
 * Currently picked train profile distance in meters. Either '25', '50', '75' or '100'.
 * @type {string}
 */
window.profile_distance = '25';
/**
 * Boundaries of the color scale for the point cloud - [from, middle, to].
 * @type {number[]}
 */
window.scale_boundaries = [0, 10, 20];          // boundaries of the point cloud color scale
/**
 * Custom camera offset set by the user - [x, y, z, yaw, pitch, roll].
 * @type {number[]}
 */
window.camera_offset = [0, 0, 0, 0, 0, 0];
/**
 * Whether to display united (postprocess) point cloud data.
 * @type {boolean}
 */
window.display_united = false;
/**
 * The current number of point cloud layers.
 * @type {number}
 */
window.curr_pcl_layers_cnt = 10;
/**
 * Number of point cloud layers when displaying the divided ("real-time") point cloud.
 * @type {number}
 */
window.pcl_layers_cnt = 10;
/**
 * Numbers of the currently displayed point cloud chunks.
 * Used when displaying the divided ("real-time") point cloud.
 * @type {number[]}
 */
let pcl_layers_positions = new Array(window.curr_pcl_layers_cnt).fill(0);
/**
 * Index of the layer with the oldest point cloud chunk, which will be replaced next.
 * @type {number}
 */
let pcl_layers_index = 0;



/**
 * Maps point intensity to a color on the blue-green-red color scale.
 * @param {number[]} d - The point data in format [x, y, z, intensity].
 */
function getColorBGR(d) {
  if (d[3] < window.scale_boundaries[0]) {
    return [0, 0, 255]   // under the scale - blue
  } else if (d[3] > window.scale_boundaries[2]) {
    return [255, 0, 0]   // over the scale - red
  } else if (d[3] < window.scale_boundaries[1]) {   // on the scale
    return [
      0, 
      Math.floor(255 * (d[3] - window.scale_boundaries[0]) 
                  / (window.scale_boundaries[1] - window.scale_boundaries[0])),
      Math.floor(255 - 255 * (d[3] - window.scale_boundaries[0]) 
                        / (window.scale_boundaries[1] - window.scale_boundaries[0]))
    ]
  } else {
    return [
      Math.floor(255 * (d[3] - window.scale_boundaries[1]) 
                  / (window.scale_boundaries[2] - window.scale_boundaries[1])),
      Math.floor(255 - 255 * (d[3] - window.scale_boundaries[1])
                        / (window.scale_boundaries[2] - window.scale_boundaries[1])),
      0
    ]
  }
}


/**
 * Maps point intensity to a color on the yellow-purple color scale.
 * @param {number[]} d - The point data in format [x, y, z, intensity].
 */
function getColorYP(d) {
  if (d[3] < window.scale_boundaries[0]) {
    return [255, 255, 0]   // under the scale - yellow
  } else if (d[3] > window.scale_boundaries[2]) {
    return [255, 0, 255]   // over the scale - purple
  } else {     // on the scale
    return [
      255,
      Math.floor(255 - 255 * (d[3] - window.scale_boundaries[0]) 
                        / (window.scale_boundaries[2] - window.scale_boundaries[0])),
      Math.floor(255 * (d[3] - window.scale_boundaries[0]) 
                  / (window.scale_boundaries[2] - window.scale_boundaries[0]))
    ]
  }
}


/**
 * Converts train profile distance in meters to an index in the paths data and transformations data.
 * @param {string} profile_dist - Either '25', '50', '75' or '100'.
 */
function profile_distance_to_index(profile_dist) {
  let i = 0;  // default is '25'
  switch (window.profile_distance) {
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


/**
 * Applies transformations to the train profile.
 * A data accessor for the train profile layer.
 * @param {Array<[number, number, number]>} d - The shape of the train profile (an array of points).
 */
function profileGetPath(d) {
  const n = profile_distance_to_index(window.profile_distance);
  
  let pos = window.position;
  if (pos > window.profile_transf[n].length - 1) pos = window.profile_transf[n].length - 1;
  
  const points = new Array(d.length);
  for (let i = 0; i < d.length; i++) {
    const x = d[i][0] * window.profile_transf[n][pos][0][0] + d[i][1] * window.profile_transf[n][pos][0][1] + d[i][2] * window.profile_transf[n][pos][0][2] + window.profile_transf[n][pos][0][3];
    const y = d[i][0] * window.profile_transf[n][pos][1][0] + d[i][1] * window.profile_transf[n][pos][1][1] + d[i][2] * window.profile_transf[n][pos][1][2] + window.profile_transf[n][pos][1][3];
    const z = d[i][0] * window.profile_transf[n][pos][2][0] + d[i][1] * window.profile_transf[n][pos][2][1] + d[i][2] * window.profile_transf[n][pos][2][2] + window.profile_transf[n][pos][2][3];

    points[i] = [x, y, z];
  }
  return points;
}


/**
 * Creates a point cloud layer for the deck.gl visualization.
 * @param {number} n - The index of the layer.
 */
function createPointCloudLayer(n) {
  return new PointCloudLayer({
    id: `point-cloud-layer${n}`,
    data: window.display_united
      ? window.united_pc_data
      : window.data_dict.layers[0].data[pcl_layers_positions[n]],
    getColor: window.data_dict.layers[0].pointColor === 'bgr'
      ? getColorBGR
      : getColorYP,
    getPosition: (d) => d,
    opacity: window.data_dict.layers[0].opacity,
    pointSize: window.data_dict.layers[0].pointSize,
    visible: window.data_dict.layers[0].visible,
    updateTriggers: {      // needed when changing getPosition or getColor (data accessors)
      getColor: [window.scale_boundaries[0], window.scale_boundaries[2], 
                 window.data_dict.layers[0].pointColor]
    }
  });
}


/**
 * Creates a layer with the line through train profile positions for the deck.gl visualization.
 */
function createProfileLineLayer() {
  return new PathLayer({
    id: 'profile-line-layer',
    data: window.profile_line_data[profile_distance_to_index(window.profile_distance)],
    getColor: window.data_dict.layers[1].color,
    getPath: (d) => d,
    getWidth: window.data_dict.layers[1].width,
    billboard: true,     // lines turned towards the camera
    visible: window.data_dict.layers[1].visible,
    updateTriggers: {
      getColor: window.data_dict.layers[1].color
    }
  });
}

/**
 * Creates a layer with the train profile for the deck.gl visualization.
 */
function createProfileLayer() {
  return new PathLayer({
    id: 'profile-layer',
    data: window.data_dict.layers[2].data,
    getColor: window.data_dict.layers[2].color,
    getPath: profileGetPath,
    getWidth: window.data_dict.layers[2].width,
    billboard: true,
    visible: window.data_dict.layers[2].visible,
    updateTriggers: {
      getPath: [window.position, window.profile_transf, window.profile_distance], // needed when changing data accessors
      getColor: window.data_dict.layers[2].color
    },
    parameters: {
      depthCompare: 'always'    // the layer will be on top of previous layers
    }
  });
}


/**
 * Creates a layer with the vector data for the deck.gl visualization.
 */
function createVectorLayer() {
  return new PathLayer({
    id: 'vector-layer',
    data: window.vector_data,
    getColor: window.data_dict.layers[3].color,
    getPath: (d) => d,
    getWidth: window.data_dict.layers[3].width,
    billboard: true,     // lines turned towards the camera
    visible: window.data_dict.layers[3].visible,
    updateTriggers: {
      getColor: window.data_dict.layers[3].color
    }
  });
}


/**
 * Creates all the layers for the deck.gl visualization.
 */
function createLayers() {
  window.layers = new Array(window.curr_pcl_layers_cnt + 2);

  for (let i = 0; i < window.curr_pcl_layers_cnt; i++) {
    window.layers[i] = createPointCloudLayer(i);
  }
  window.layers[window.curr_pcl_layers_cnt] = createProfileLineLayer();
  window.layers[window.curr_pcl_layers_cnt + 1] = createProfileLayer();
  window.layers[window.curr_pcl_layers_cnt + 2] = createVectorLayer();
}


/**
 * Recreates all the layers and updates the visualization.
 */
function updateLayers() {
  createLayers();

  if (window.deck.setProps) {
    window.deck.setProps({layers: window.layers});
  }
}


/**
 * Initializes the deck.gl visualization.
 */
function initializeDeck() {

  if (window.profile_transf == null) {
    // transformation data was not yet defined by the callback, wait until it is
    setTimeout(initializeDeck, 40);  // try again in 40 ms
    return;
  }
  
  const VIEW = new FirstPersonView({
    projectionMatrix: window.data_dict.views[0].projectionMatrix,
    controller: window.data_dict.views[0].controller
  });

  // The context is created manually to specify "preserveDrawingBuffer: true".
  // That is needed to enable reading the pixels of the visualisation for applying distortion.
  const canvas = document.getElementById("visualization-canvas");
  const context = canvas.getContext("webgl2", { preserveDrawingBuffer: true, premultipliedAlpha: false });

  window.deck = new Deck({
    views: [VIEW],
    layers: [],
    canvas: 'visualization-canvas',
    context: context,
    onDeviceInitialized: () => {
      // check whether WegGL is HW accelerated
      let renderer = window.deck.device.info.renderer;
      // according to this page, the software-based renderers are llvmpipe and SwiftShader
      // https://deviceandbrowserinfo.com/learning_zone/articles/webgl_renderer_values
      if (renderer.includes('llvmpipe') || renderer.includes('SwiftShader')) {
        window.alert(
          'V tomto prohlížeči není přístupná hardwarová akcelerace grafiky. '
          + 'Vykreslování většího množství dat bude probíhat pomalu.'
        )
      }
    }
  });

  updateDeck();
  window.deck_initialized = true;
} // end of function initializeDeck()


/**
 * Calculates which point cloud chunks should be displayed at the current position.
 */
function changeLayersData() {
  if (!window.display_united) {
    // find current position in point cloud timestamps
    window.pcl_position = 0;
    const video = document.getElementById('background-video'); 
    while(window.pcl_timestamps[window.pcl_position] < video.currentTime) {
      window.pcl_position++;
    }

    // display point cloud data corresponding to current position and 9 positions backwards (if they exist)
    // for example if window.pcl_position == 7, pcl_layers_position will be [0, 0, 0, 1, 2, 3, 4, 5, 6, 7]
    let pos = window.pcl_position;
    for (let i = window.curr_pcl_layers_cnt - 1; i >= 0; i--) {
      pcl_layers_positions[i] = pos;
      if (pos > 0) {
        pos--;
      }
    }
    // the first set of data in the buffer will now be the oldest to rewrite in case of animation start
    pcl_layers_index = 0;
  }
}


/**
 * Changes camera position.
 * The final position of the virtual camera is a combination of:
   1. the current position of the train (determined by the window.position variable, data is in arrays 
      window.translations, window.rotations_inv, window.rotations_euler),
   2. custom camera offset set by the user (window.camera_offset).
 */
function updateDeck() {
  const pos = window.position;

  const offset_x = window.camera_offset[0];
  const offset_y = window.camera_offset[1];
  const offset_z = window.camera_offset[2];
  const sum_x = offset_x + window.rotations[pos][0][0] * window.translations[pos][0] + window.rotations[pos][0][1] * window.translations[pos][1] + window.rotations[pos][0][2] * window.translations[pos][2];
  const sum_y = offset_y + window.rotations[pos][1][0] * window.translations[pos][0] + window.rotations[pos][1][1] * window.translations[pos][1] + window.rotations[pos][1][2] * window.translations[pos][2];
  const sum_z = offset_z + window.rotations[pos][2][0] * window.translations[pos][0] + window.rotations[pos][2][1] * window.translations[pos][1] + window.rotations[pos][2][2] * window.translations[pos][2];

  // multiply sum_* by inverse rotation matrix
  const final_x = window.rotations_inv[pos][0][0] * sum_x + window.rotations_inv[pos][0][1] * sum_y + window.rotations_inv[pos][0][2] * sum_z;
  const final_y = window.rotations_inv[pos][1][0] * sum_x + window.rotations_inv[pos][1][1] * sum_y + window.rotations_inv[pos][1][2] * sum_z;
  const final_z = window.rotations_inv[pos][2][0] * sum_x + window.rotations_inv[pos][2][1] * sum_y + window.rotations_inv[pos][2][2] * sum_z;

  // make a new viewstate from the new position
  const INITIAL_VIEW_STATE = {
    bearing: 90 + window.rotations_euler[pos][0] + window.camera_offset[4],
    pitch: window.rotations_euler[pos][1] + window.camera_offset[5],
    position: [final_x, final_y, final_z]
  };
  window.deck.setProps({initialViewState: INITIAL_VIEW_STATE});

  // add roll angle by rotating the canvas
  const canvas = document.getElementById('visualization-canvas');
  const dist_canvas = document.getElementById("distorted-visualization-canvas");
  const transform = `rotate(${ window.window.rotations_euler[pos][2] + window.camera_offset[5] }deg)`;
  canvas.style.transform = transform;
  dist_canvas.style.transform = transform;
  createLayers();

  window.deck.setProps({layers: window.layers});
} // end of function updateDeck()


/**
 * Changes point cloud visibility, point size and opacity.
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} point_size - Point size.
 * @param {string} point_color - Color scale, either 'bgr' or 'yp'.
 * @param {number} opacity - Opacity of the layer.
 */
function updatePCLayerProps(visible, point_size, point_color, opacity) {
  window.data_dict.layers[0].visible = visible;
  window.data_dict.layers[0].pointSize = parseInt(point_size, 10);
  window.data_dict.layers[0].pointColor = point_color;
  window.data_dict.layers[0].opacity = parseFloat(opacity);
  updateLayers();
}


/**
 * Switches between point cloud types - united (postprocess) or divided ("real-time").
 * @param {boolean} display_united - True if the visualization should display the united point cloud.
 */
function changePCMode(display_united) {
  window.display_united = display_united;
  
  if (display_united == true) {
    window.curr_pcl_layers_cnt = 1;
  } else {
    window.curr_pcl_layers_cnt = window.pcl_layers_cnt;
    // when displaying divided point cloud data, we need to change data according to the position
    changeLayersData();
    updateDeck();
  }
  updateLayers();
}


/**
 * Changes the visibility, line width and color of the line through train profile positions.
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} line_width - Line width.
 * @param {string} line_color - Line color in format "#FFFFFF".
 */
function updateProfileLineLayerProps(visible, line_width, line_color) {
  // convert color to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.data_dict.layers[1].visible = visible;
  window.data_dict.layers[1].width = parseInt(line_width, 10);
  window.data_dict.layers[1].color = new_color;
  updateLayers();
}


/**
 * Changes the visibility, line width and color of the vector data.
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} line_width - Line width.
 * @param {string} line_color - Line color in format "#FFFFFF".
 */
function updateVectorLayerProps(visible, line_width, line_color) {
  // convert to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.data_dict.layers[3].visible = visible;
  window.data_dict.layers[3].width = parseInt(line_width, 10);
  window.data_dict.layers[3].color = new_color;
  updateLayers();
}


/**
 * Changes the visibility, line width and color of the train profile.
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} line_width - Line width.
 * @param {string} line_color - Line color in format "#FFFFFF".
 */
function updateProfileLayerProps(visible, line_width, line_color) {
  // convert to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.data_dict.layers[2].visible = visible;
  window.data_dict.layers[2].width = parseInt(line_width, 10);
  window.data_dict.layers[2].color = new_color;

  createLayers(); // TODO: maybe optimize this so that only the right layers are recreated

  window.deck.setProps({layers: window.layers});
}


/**
 * One step in the animation of the train movement. Is tied to video frames as a callback for a new frame.
 * Updates both the visualization and the GUI elements showing the progress.
 * @param {DOMHighResTimeStamp } now - The time when the callback was called.
 * @param {Object} metadata - An object defined in the documentation of requestVideoFrameCallback() method.
 */
function animationStep(now, metadata) {
  const video = document.getElementById('background-video');
  if (window.animation_running) video.requestVideoFrameCallback(animationStep);
  
  // determine new position from video time and camera timestamps
  if (metadata) {
    while (window.camera_timestamps[window.position] < metadata.mediaTime) {
      window.position += 1;
    }
  }

  if (window.position >= window.frames_cnt - 2) {  // end of animation
    // stop the video
    const video = document.getElementById('background-video');
    video.pause();      // will fire stopDeckAnimation()
    window.position = window.frames_cnt - 1;           // show the last frame
  }

  // change point cloud data if we are not displaying the united point cloud
  if (metadata && !window.display_united) {
    // pcl_layers_positions is a circular buffer when the animation is running
    while(window.pcl_timestamps[window.pcl_position] < metadata.mediaTime) {
      // move to new position
      window.pcl_position++;
      // rewrite old data with new data
      pcl_layers_positions[pcl_layers_index] = window.pcl_position;
      // mark the next set of data as old data
      pcl_layers_index = (pcl_layers_index + 1) % window.curr_pcl_layers_cnt;
    }
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
} // end of function animationStep()


/**
 * Handles the beginning of the animation of the train movement.
 */
function runDeckAnimation() {
  if (window.position >= window.frames_cnt - 2) {  // it is at the end, start again from the beginning
    const video = document.getElementById('background-video');
    video.currentTime = 0;
    window.position = 0;
    window.pcl_position = 0;
    pcl_layers_positions = new Array(window.curr_pcl_layers_cnt).fill(0);
    window.updateDeck();
  }

  // change play icon to pause icon
  const icon = document.getElementById("play-button").querySelector("i");
  icon.classList.remove("bi-play-fill");
  icon.classList.add("bi-pause-fill");
  
  window.animation_running = true;
  animationStep();
}


/**
 * Handles the end of the animation of the train movement.
 * Is either called from {@link playOrStop}, or is fired as a callback at the end of the animation.
 */
function stopDeckAnimation() {
  window.animation_running = false;
  // change pause icon back to play icon
  const icon = document.getElementById("play-button").querySelector("i");
  icon.classList.add("bi-play-fill");
  icon.classList.remove("bi-pause-fill");

  const video = document.getElementById('background-video');
  // fix video offset
  video.currentTime = video.currentTime;
  // this has to be done with the GUI elements so that Dash knows about the changes
  // could not be done while the animation was running, because it is slow 
  dash_clientside.set_props("camera-position-input", {value: window.position});
  dash_clientside.set_props("camera-position-slider-input", {value: window.position});
  const time_sec = Math.floor(video.currentTime - 0.001); // get time in seconds, round to whole number
  const minutes = Math.floor(time_sec / 60);
  const seconds = time_sec % 60;
  const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  dash_clientside.set_props("current-time-div", {children: label});
}


/**
 * Starts/stops the animation of the train movement.
 */
function playOrStop() {
  if (!window.deck) return;

  const video = document.getElementById('background-video');
  if (!window.animation_running) {
    runDeckAnimation();        // run both deck animation and the video
    video.play();
    // define a callback that will run at the end of the animation
    video.onpause = function(){ stopDeckAnimation() };
  } else {
    video.pause();
  }
}


/**
 * Changes the current position.
 * @param {number} new_pos - The new position.
 */
function jumpToPosition(new_pos) {
  // update video
  const video = document.getElementById('background-video');
  const videoTime = window.camera_timestamps[new_pos];
  video.currentTime = videoTime;
  // update deck.gl visualization
  window.position = new_pos;
  changeLayersData();  // in case that we are not displaying united point cloud
  updateDeck();  // call function defined in the JavaScript file
  // update slider and input field and time label
  dash_clientside.set_props("camera-position-slider-input", {value: new_pos});
  dash_clientside.set_props("camera-position-input", {value: new_pos});
  // update time label
  const time_sec = Math.floor(videoTime);
  const minutes = Math.floor(time_sec / 60);
  const seconds = time_sec % 60;
  const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  dash_clientside.set_props("current-time-div", {children: label});
}


/**
 * Reacts to key presses.
 *  - space - play/stop the animation
 *  - right arrow/left arrow - jump 3 seconds forward/backwards
 * @param {KeyboardEvent} e - The keypress event. 
 */
function reactToKeyPress(e) {
  if (e.key === ' ') {                   //  play/stop the animation on space press
    playOrStop();

  } else if (e.key === 'ArrowLeft') {    // move the animation 3 seconds backwards on arrow left press
    e.preventDefault();  // do not move other things 
    // calculate the new time
    let new_time = window.camera_timestamps[window.position] - 3;
    if (new_time < 0) new_time = 0;
    // find the position corresponding to the new time and jump to it
    let new_pos = window.position;
    while (window.camera_timestamps[new_pos] > new_time) {
      new_pos -= 1;
    }
    jumpToPosition(new_pos);
  } else if (e.key === 'ArrowRight') {    // move the animation 3 seconds forward on arrow right press
    e.preventDefault();
    // calculate the new time
    let new_time = window.camera_timestamps[window.position] + 3;
    const max_time = window.camera_timestamps[window.frames_cnt - 1];
    if (new_time > max_time) new_time = max_time;
    // find the position corresponding to the new time and jump to it
    let new_pos = window.position;
    while (window.camera_timestamps[new_pos] < new_time) {
      new_pos += 1;
    }
    jumpToPosition(new_pos);
  } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {   // do not move camera sliders by arrows
    if (document.activeElement.id === 'camera-x-slider-input' 
      || document.activeElement.id === 'camera-y-slider-input'
      || document.activeElement.id === 'camera-z-slider-input'
      || document.activeElement.id === 'camera-yaw-slider-input'
      || document.activeElement.id === 'camera-pitch-slider-input'
      || document.activeElement.id === 'camera-roll-slider-input') e.preventDefault();
  }
}


// set the callback to the key press event
document.addEventListener('keydown', reactToKeyPress);

// a special accomodation for Google Chrome, to make the animation continue running when
// the user switches to another window in the browser and then switches back to this window
// (Chrome stops the animation when the window is not visible)
document.addEventListener("visibilitychange", () => {
  // wait 40 ms, because this runs before Chrome makes the animation run again
  setTimeout(() => {
    const video = document.getElementById('background-video');
    if (document.visibilityState === "visible" && !video.paused && !video.ended) {
      runDeckAnimation();
    }
  }, 40);
});

// make the functions global
window.initializeDeck = initializeDeck;
window.changeLayersData = changeLayersData;
window.updateDeck = updateDeck;
window.updateLayers = updateLayers;
window.updatePCLayerProps = updatePCLayerProps;
window.changePCMode = changePCMode;
window.updateVectorLayerProps = updateVectorLayerProps;
window.updateProfileLineLayerProps = updateProfileLineLayerProps;
window.updateProfileLayerProps = updateProfileLayerProps;
window.playOrStop = playOrStop;
window.jumpToPosition = jumpToPosition;
