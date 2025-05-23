/**
 * @fileoverview Creates and manages the deck.gl visualization and the train movement animation.
 * @author Zuzana Miškaňová
 */
import {Deck, FirstPersonView} from '@deck.gl/core';
import {PathLayer, PointCloudLayer} from '@deck.gl/layers';


/**
 * A class that manages the Deck.gl visualization and the train movement animation.
 */
class Visualization {
  /**
   * @constructor
   */
  constructor() {
    /************************* define all the members (attributes) ******************************/

    /**
     * Whether the visualization (Deck object window.deck) is already initialized.
     * @type {boolean}
     */
    this.deck_initialized = false;
    /**
     * Number of positions.
     * @type {number}
     */
    this.frames_cnt = 500;
    /**
     * Current position.
     * @type {number}
     */
    this.position = 0;
    /**
     * Current position in point cloud chunks.
     * @type {number}
     */
    this.pcl_position = 0;
    /**
     * Whether the animation is currently running.
     * @type {boolean}
     */
    this.animation_running = false;
    /**
     * Currently picked train profile distance in meters. Either '25', '50', '75' or '100'.
     * @type {string}
     */
    this.profile_distance = '25';
    /**
     * Boundaries of the color scale for the point cloud - [from, middle, to].
     * @type {number[]}
     */
    this.scale_boundaries = [0, 10, 20];          // boundaries of the point cloud color scale
    /**
     * Custom camera offset set by the user - [x, y, z, yaw, pitch, roll].
     * @type {number[]}
     */
    this.camera_offset = [0, 0, 0, 0, 0, 0];
    /**
     * Whether to display united (postprocess) point cloud data.
     * @type {boolean}
     */
    this.display_united = false;
    /**
     * The current number of point cloud layers.
     * @type {number}
     */
    this.curr_pcl_layers_cnt = 10;
    /**
     * Number of point cloud layers when displaying the divided ("real-time") point cloud.
     * @type {number}
     */
    this.pcl_layers_cnt = 10;
    /**
     * Numbers of the currently displayed point cloud chunks.
     * Used when displaying the divided ("real-time") point cloud.
     * @type {number[]}
     */
    this.pcl_layers_positions = new Array(this.curr_pcl_layers_cnt).fill(0);
    /**
     * Index of the layer with the oldest point cloud chunk, which will be replaced next.
     * @type {number}
     */
    this.pcl_layers_index = 0;
    this.layers = [];

    /***************** the members into which data are copied from Dash stores *********************/

    /**
     * A dictionary containing the main visualization definition + divided point cloud data.
     * @type {Object}
     */
    this.data_dict = {};
    /**
     * The united point cloud.
     * @type {number[][]}
     */
    this.united_pc_data = [];
    /**
     * The lines through train profile positions.
     * @type {number[][][]}
     */
    this.profile_line_data = [];
    /**
     * The vector data (polylines).
     * @type {number[][][]}
     */
    this.vector_data = [];
    /**
     * Timestamps of the point cloud chunks.
     * @type {number[]}
     */
    this.pcl_timestamps = [];
    /**
     * Four arrays of transformation matrices (one for every train profile distance).
     * @type {number[][][][]}
     */
    this.profile_transf = [];
    /**
     * Camera translations.
     * @type {number[][]}
     */
    this.translations = [];
    /**
     * Camera rotation matrices.
     * @type {number[][][]}
     */
    this.rotations = [];
    /**
     * Inverse camera rotation matrices.
     * @type {number[][][]}
     */
    this.rotations_inv = [];
    /**
     * Camera rotations as Euler angles.
     * @type {number[][]}
     */
    this.rotations_euler = [];
    /**
     * Timestamps of the camera.
     * @type {number[]}
     */
    this.camera_timestamps = [];
  }
}


/************************* define all the methods ******************************/


/**
 * Maps point intensity to a color on the blue-green-red color scale.
 * A data accessor for the point cloud layers.
 * @function
 * @param {number[]} d - The point data in format [x, y, z, intensity].
 * @returns {number[]} The color.
 */
Visualization.prototype.getColorBGR = function (d) {
  if (d[3] < window.vis.scale_boundaries[0]) {
    return [0, 0, 255]   // under the scale - blue
  } else if (d[3] > window.vis.scale_boundaries[2]) {
    return [255, 0, 0]   // over the scale - red
  } else if (d[3] < window.vis.scale_boundaries[1]) {   // on the scale
    return [
      0, 
      Math.floor(255 * (d[3] - window.vis.scale_boundaries[0]) 
                  / (window.vis.scale_boundaries[1] - window.vis.scale_boundaries[0])),
      Math.floor(255 - 255 * (d[3] - window.vis.scale_boundaries[0]) 
                        / (window.vis.scale_boundaries[1] - window.vis.scale_boundaries[0]))
    ]
  } else {
    return [
      Math.floor(255 * (d[3] - window.vis.scale_boundaries[1]) 
                  / (window.vis.scale_boundaries[2] - window.vis.scale_boundaries[1])),
      Math.floor(255 - 255 * (d[3] - window.vis.scale_boundaries[1])
                        / (window.vis.scale_boundaries[2] - window.vis.scale_boundaries[1])),
      0
    ]
  }
};


/**
 * Maps point intensity to a color on the yellow-purple color scale.
 * A data accessor for the point cloud layers.
 * @function
 * @param {number[]} d - The point data in format [x, y, z, intensity].
 * @returns {number[]} The color.
 */
Visualization.prototype.getColorYP = function (d) {
  if (d[3] < window.vis.scale_boundaries[0]) {
    return [255, 255, 0]   // under the scale - yellow
  } else if (d[3] > window.vis.scale_boundaries[2]) {
    return [255, 0, 255]   // over the scale - purple
  } else {     // on the scale
    return [
      255,
      Math.floor(255 - 255 * (d[3] - window.vis.scale_boundaries[0]) 
                        / (window.vis.scale_boundaries[2] - window.vis.scale_boundaries[0])),
      Math.floor(255 * (d[3] - window.vis.scale_boundaries[0]) 
                  / (window.vis.scale_boundaries[2] - window.vis.scale_boundaries[0]))
    ]
  }
};


/**
 * Converts train profile distance in meters to an index in the paths data and transformations data.
 * @function
 * @param {string} profile_dist - Either '25', '50', '75' or '100'.
 * @returns {number} An index in range from 0 to 3.
 */
Visualization.prototype.profileDistanceToIndex = function (profile_dist) {
  let i = 0;  // default is '25'
  switch (window.vis.profile_distance) {
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
};


/**
 * Applies transformations to the train profile.
 * A data accessor for the train profile layer.
 * @function
 * @param {number[][]} d - The basic train profile (an array of points).
 * @returns {number[][]} The transformed train profile (an array of points).
 */
Visualization.prototype.profileGetPath = function (d) {
  const n = window.vis.profileDistanceToIndex(window.vis.profile_distance);
  
  let pos = window.vis.position;
  if (pos > window.vis.profile_transf[n].length - 1) pos = window.vis.profile_transf[n].length - 1;
  
  const points = new Array(d.length);
  for (let i = 0; i < d.length; i++) {
    const x = d[i][0] * window.vis.profile_transf[n][pos][0][0] + d[i][1] * window.vis.profile_transf[n][pos][0][1] + d[i][2] * window.vis.profile_transf[n][pos][0][2] + window.vis.profile_transf[n][pos][0][3];
    const y = d[i][0] * window.vis.profile_transf[n][pos][1][0] + d[i][1] * window.vis.profile_transf[n][pos][1][1] + d[i][2] * window.vis.profile_transf[n][pos][1][2] + window.vis.profile_transf[n][pos][1][3];
    const z = d[i][0] * window.vis.profile_transf[n][pos][2][0] + d[i][1] * window.vis.profile_transf[n][pos][2][1] + d[i][2] * window.vis.profile_transf[n][pos][2][2] + window.vis.profile_transf[n][pos][2][3];

    points[i] = [x, y, z];
  }
  return points;
};


/**
 * Creates a point cloud layer for the deck.gl visualization.
 * @function
 * @param {number} n - The index of the layer.
 * @returns {PointCloudLayer} The created layer.
 */
Visualization.prototype.createPointCloudLayer = function (n) {
  return new PointCloudLayer({
    id: `point-cloud-layer${n}`,
    data: window.vis.display_united
      ? window.vis.united_pc_data
      : window.vis.data_dict.layers[0].data[window.vis.pcl_layers_positions[n]],
    getColor: window.vis.data_dict.layers[0].pointColor === 'bgr'
      ? window.vis.getColorBGR
      : window.vis.getColorYP,
    getPosition: (d) => d,
    opacity: window.vis.data_dict.layers[0].opacity,
    pointSize: window.vis.data_dict.layers[0].pointSize,
    visible: window.vis.data_dict.layers[0].visible,
    updateTriggers: {      // needed when changing getPosition or getColor (data accessors)
      getColor: [window.vis.scale_boundaries[0], window.vis.scale_boundaries[2], 
                 window.vis.data_dict.layers[0].pointColor]
    }
  });
};


/**
 * Creates a layer with the line through train profile positions for the deck.gl visualization.
 * @function
 * @returns {PathLayer} The created layer.
 */
Visualization.prototype.createProfileLineLayer = function () {
  return new PathLayer({
    id: 'profile-line-layer',
    data: window.vis.profile_line_data[window.vis.profileDistanceToIndex(window.vis.profile_distance)],
    getColor: window.vis.data_dict.layers[1].color,
    getPath: (d) => d,
    getWidth: window.vis.data_dict.layers[1].width,
    billboard: true,     // lines turned towards the camera
    visible: window.vis.data_dict.layers[1].visible,
    updateTriggers: {
      getColor: window.vis.data_dict.layers[1].color
    }
  });
};

/**
 * Creates a layer with the train profile for the deck.gl visualization.
 * @function
 * @returns {PathLayer} The created layer.
 */
Visualization.prototype.createProfileLayer = function () {
  return new PathLayer({
    id: 'profile-layer',
    data: window.vis.data_dict.layers[2].data,
    getColor: window.vis.data_dict.layers[2].color,
    getPath: window.vis.profileGetPath,
    getWidth: window.vis.data_dict.layers[2].width,
    billboard: true,
    visible: window.vis.data_dict.layers[2].visible,
    updateTriggers: {
      getPath: [window.vis.position, window.vis.profile_transf, window.vis.profile_distance], // needed when changing data accessors
      getColor: window.vis.data_dict.layers[2].color
    },
    parameters: {
      depthCompare: 'always'    // the layer will be on top of previous layers
    }
  });
};


/**
 * Creates a layer with the vector data for the deck.gl visualization.
 * @function
 * @returns {PathLayer} The created layer.
 */
Visualization.prototype.createVectorLayer = function () {
  return new PathLayer({
    id: 'vector-layer',
    data: window.vis.vector_data,
    getColor: window.vis.data_dict.layers[3].color,
    getPath: (d) => d,
    getWidth: window.vis.data_dict.layers[3].width,
    billboard: true,     // lines turned towards the camera
    visible: window.vis.data_dict.layers[3].visible,
    updateTriggers: {
      getColor: window.vis.data_dict.layers[3].color
    }
  });
};


/**
 * Creates all the layers for the deck.gl visualization.
 * @function
 * @returns {PathLayer} The created layer.
 */
Visualization.prototype.createLayers = function () {
  window.vis.layers = new Array(window.vis.curr_pcl_layers_cnt + 2);

  for (let i = 0; i < window.vis.curr_pcl_layers_cnt; i++) {
    window.vis.layers[i] = window.vis.createPointCloudLayer(i);
  }
  window.vis.layers[window.vis.curr_pcl_layers_cnt] = window.vis.createProfileLineLayer();
  window.vis.layers[window.vis.curr_pcl_layers_cnt + 1] = window.vis.createProfileLayer();
  window.vis.layers[window.vis.curr_pcl_layers_cnt + 2] = window.vis.createVectorLayer();
};


/**
 * Recreates all the layers and updates the visualization.
 * @function
 */
Visualization.prototype.updateLayers = function () {
  window.vis.createLayers();

  if (window.deck.setProps) {
    window.deck.setProps({layers: window.vis.layers});
  }
};


/**
 * Initializes the deck.gl visualization.
 * @function
 */
Visualization.prototype.initializeDeck = function () {

  if (window.vis.profile_transf === undefined || window.vis.profile_transf.length === 0) {
    // transformation data was not yet defined by the callback, wait until it is
    setTimeout(window.vis.initializeDeck, 3000);  // try again in 40 ms
    return;
  }
  
  const VIEW = new FirstPersonView({
    projectionMatrix: window.vis.data_dict.views[0].projectionMatrix,
    controller: window.vis.data_dict.views[0].controller
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
      // according to window.vis page, the software-based renderers are llvmpipe and SwiftShader
      // https://deviceandbrowserinfo.com/learning_zone/articles/webgl_renderer_values
      if (renderer.includes('llvmpipe') || renderer.includes('SwiftShader')) {
        window.alert(
          'V tomto prohlížeči není přístupná hardwarová akcelerace grafiky. '
          + 'Vykreslování většího množství dat bude probíhat pomalu.'
        )
      }
    }
  });

  window.vis.updateDeck();
  window.vis.deck_initialized = true;
}; // end of function initializeDeck()


/**
 * Calculates which point cloud chunks should be displayed at the current position.
 * @function
 */
Visualization.prototype.changeLayersData = function () {
  if (!window.vis.display_united) {
    // find current position in point cloud timestamps
    window.vis.pcl_position = 0;
    const video = document.getElementById('background-video'); 
    while(window.vis.pcl_timestamps[window.vis.pcl_position] < video.currentTime) {
      window.vis.pcl_position++;
    }

    // display point cloud data corresponding to current position and 9 positions backwards (if they exist)
    // for example if window.vis.pcl_position == 7, pcl_layers_position will be [0, 0, 0, 1, 2, 3, 4, 5, 6, 7]
    let pos = window.vis.pcl_position;
    for (let i = window.vis.curr_pcl_layers_cnt - 1; i >= 0; i--) {
      window.vis.pcl_layers_positions[i] = pos;
      if (pos > 0) {
        pos--;
      }
    }
    // the first set of data in the buffer will now be the oldest to rewrite in case of animation start
    window.vis.pcl_layers_index = 0;
  }
};


/**
 * Changes camera position.
 * The final position of the virtual camera is a combination of:
   1. the current position of the train (determined by the window.vis.position variable, data is in arrays 
      window.vis.translations, window.vis.rotations_inv, window.vis.rotations_euler),
   2. custom camera offset set by the user (window.vis.camera_offset).
  * @function
 */
Visualization.prototype.updateDeck = function () {
  const pos = window.vis.position;

  const offset_x = window.vis.camera_offset[0];
  const offset_y = window.vis.camera_offset[1];
  const offset_z = window.vis.camera_offset[2];
  const sum_x = offset_x + window.vis.rotations[pos][0][0] * window.vis.translations[pos][0] + window.vis.rotations[pos][0][1] * window.vis.translations[pos][1] + window.vis.rotations[pos][0][2] * window.vis.translations[pos][2];
  const sum_y = offset_y + window.vis.rotations[pos][1][0] * window.vis.translations[pos][0] + window.vis.rotations[pos][1][1] * window.vis.translations[pos][1] + window.vis.rotations[pos][1][2] * window.vis.translations[pos][2];
  const sum_z = offset_z + window.vis.rotations[pos][2][0] * window.vis.translations[pos][0] + window.vis.rotations[pos][2][1] * window.vis.translations[pos][1] + window.vis.rotations[pos][2][2] * window.vis.translations[pos][2];

  // multiply sum_* by inverse rotation matrix
  const final_x = window.vis.rotations_inv[pos][0][0] * sum_x + window.vis.rotations_inv[pos][0][1] * sum_y + window.vis.rotations_inv[pos][0][2] * sum_z;
  const final_y = window.vis.rotations_inv[pos][1][0] * sum_x + window.vis.rotations_inv[pos][1][1] * sum_y + window.vis.rotations_inv[pos][1][2] * sum_z;
  const final_z = window.vis.rotations_inv[pos][2][0] * sum_x + window.vis.rotations_inv[pos][2][1] * sum_y + window.vis.rotations_inv[pos][2][2] * sum_z;

  // make a new viewstate from the new position
  const INITIAL_VIEW_STATE = {
    bearing: 90 + window.vis.rotations_euler[pos][0] + window.vis.camera_offset[3],
    pitch: window.vis.rotations_euler[pos][1] + window.vis.camera_offset[4],
    position: [final_x, final_y, final_z]
  };
  window.deck.setProps({initialViewState: INITIAL_VIEW_STATE});

  // add roll angle by rotating the canvas
  const canvas = document.getElementById('visualization-canvas');
  const dist_canvas = document.getElementById("distorted-visualization-canvas");
  const transform = `rotate(${ window.vis.rotations_euler[pos][2] + window.vis.camera_offset[5] }deg)`;
  canvas.style.transform = transform;
  dist_canvas.style.transform = transform;

  window.vis.updateLayers();
}; // end of function updateDeck()


/**
 * Changes point cloud visibility, point size and opacity.
 * @function
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} point_size - Point size.
 * @param {string} point_color - Color scale, either 'bgr' or 'yp'.
 * @param {number} opacity - Opacity of the layer.
 */
Visualization.prototype.updatePCLayerProps = function (visible, point_size, point_color, opacity) {
  window.vis.data_dict.layers[0].visible = visible;
  window.vis.data_dict.layers[0].pointSize = parseInt(point_size, 10);
  window.vis.data_dict.layers[0].pointColor = point_color;
  window.vis.data_dict.layers[0].opacity = parseFloat(opacity);
  window.vis.updateLayers();
};


/**
 * Switches between point cloud types - united (postprocess) or divided ("real-time").
 * @function
 * @param {boolean} display_united - True if the visualization should display the united point cloud.
 */
Visualization.prototype.changePCMode = function (display_united) {
  window.vis.display_united = display_united;
  
  if (display_united == true) {
    window.vis.curr_pcl_layers_cnt = 1;
  } else {
    window.vis.curr_pcl_layers_cnt = window.vis.pcl_layers_cnt;
    // when displaying divided point cloud data, we need to change data according to the position
    window.vis.changeLayersData();
    window.vis.updateDeck();
  }
  window.vis.updateLayers();
};


/**
 * Changes the visibility, line width and color of the line through train profile positions.
 * @function
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} line_width - Line width.
 * @param {string} line_color - Line color in format "#FFFFFF".
 */
Visualization.prototype.updateProfileLineLayerProps = function (visible, line_width, line_color) {
  // convert color to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.vis.data_dict.layers[1].visible = visible;
  window.vis.data_dict.layers[1].width = parseInt(line_width, 10);
  window.vis.data_dict.layers[1].color = new_color;
  window.vis.updateLayers();
};


/**
 * Changes the visibility, line width and color of the vector data.
 * @function
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} line_width - Line width.
 * @param {string} line_color - Line color in format "#FFFFFF".
 */
Visualization.prototype.updateVectorLayerProps = function (visible, line_width, line_color) {
  // convert to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.vis.data_dict.layers[3].visible = visible;
  window.vis.data_dict.layers[3].width = parseInt(line_width, 10);
  window.vis.data_dict.layers[3].color = new_color;
  window.vis.updateLayers();
};


/**
 * Changes the visibility, line width and color of the train profile.
 * @function
 * @param {boolean} visible - Whether the layer should be visible.
 * @param {number} line_width - Line width.
 * @param {string} line_color - Line color in format "#FFFFFF".
 */
Visualization.prototype.updateProfileLayerProps = function (visible, line_width, line_color) {
  // convert to RGB
  // the following line is taken from a piece of example code in deck.gl documentation (PathLayer section)
  const new_color = line_color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16));

  window.vis.data_dict.layers[2].visible = visible;
  window.vis.data_dict.layers[2].width = parseInt(line_width, 10);
  window.vis.data_dict.layers[2].color = new_color;

  window.vis.updateLayers();
};

/**
 * Sets the projection matrix.
 * @function
 * @param {number[]} proj_matrix - The new projection matrix.
 */
Visualization.prototype.setProjectionMatrix = function (proj_matrix) {
  window.vis.data_dict.views[0].projectionMatrix = proj_matrix;
  const VIEW = new FirstPersonView({
    projectionMatrix: window.vis.data_dict.views[0].projectionMatrix,
    controller: window.vis.data_dict.views[0].controller
  });
  window.deck.setProps({views: [VIEW]});
};


/**
 * One step in the animation of the train movement. Is tied to video frames as a callback for a new frame.
 * Updates both the visualization and the GUI elements showing the progress.
 * @function
 * @param {DOMHighResTimeStamp } now - The time when the callback was called.
 * @param {Object} metadata - An object defined in the documentation of requestVideoFrameCallback() method.
 */
Visualization.prototype.animationStep = function (now, metadata) {
  const video = document.getElementById('background-video');
  if (window.vis.animation_running) video.requestVideoFrameCallback(window.vis.animationStep);
  
  // determine new position from video time and camera timestamps
  if (metadata) {
    while (window.vis.camera_timestamps[window.vis.position] < metadata.mediaTime) {
      window.vis.position += 1;
    }
  }

  if (window.vis.position >= window.vis.frames_cnt - 2) {  // end of animation
    // stop the video
    const video = document.getElementById('background-video');
    video.pause();      // will fire window.vis.stopDeckAnimation()
    window.vis.position = window.vis.frames_cnt - 1;           // show the last frame
  }

  // change point cloud data if we are not displaying the united point cloud
  if (metadata && !window.vis.display_united) {
    // window.vis.pcl_layers_positions is a circular buffer when the animation is running
    while(window.vis.pcl_timestamps[window.vis.pcl_position] < metadata.mediaTime) {
      // move to new position
      window.vis.pcl_position++;
      // rewrite old data with new data
      window.vis.pcl_layers_positions[window.vis.pcl_layers_index] = window.vis.pcl_position;
      // mark the next set of data as old data
      window.vis.pcl_layers_index = (window.vis.pcl_layers_index + 1) % window.vis.curr_pcl_layers_cnt;
    }
  }
 
  // update the visualization
  window.vis.updateDeck();
  // update GUI elements
  document.getElementById("camera-position-input").value = window.vis.position;         // update input value
  document.getElementById("camera-position-slider-input").value = window.vis.position;  // update slider value
  const time_sec = Math.floor(Math.max(video.currentTime - 0.001, 0)); // get time in seconds, round to whole number
  const minutes = Math.floor(time_sec / 60);
  const seconds = time_sec % 60;                                                    // update time label
  document.getElementById("current-time-div").innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}; // end of function animationStep()


/**
 * Handles the beginning of the animation of the train movement.
 * @function
 */
Visualization.prototype.runDeckAnimation = function () {
  if (window.vis.position >= window.vis.frames_cnt - 2) {  // it is at the end, start again from the beginning
    const video = document.getElementById('background-video');
    video.currentTime = 0;
    window.vis.position = 0;
    window.vis.pcl_position = 0;
    window.vis.pcl_layers_positions = new Array(window.vis.curr_pcl_layers_cnt).fill(0);
    window.vis.updateDeck();
  }

  // change play icon to pause icon
  const icon = document.getElementById("play-button").querySelector("i");
  icon.classList.remove("bi-play-fill");
  icon.classList.add("bi-pause-fill");
  
  window.vis.animation_running = true;
  window.vis.animationStep();
};


/**
 * Handles the end of the animation of the train movement.
 * Is either called from {@link togglePlay}, or is fired as a callback at the end of the animation.
 * @function
 */
Visualization.prototype.stopDeckAnimation = function () {
  window.vis.animation_running = false;
  // change pause icon back to play icon
  const icon = document.getElementById("play-button").querySelector("i");
  icon.classList.add("bi-play-fill");
  icon.classList.remove("bi-pause-fill");

  const video = document.getElementById('background-video');
  // fix video offset
  video.currentTime = video.currentTime;
  // window.vis has to be done with the GUI elements so that Dash knows about the changes
  // could not be done while the animation was running, because it is slow 
  dash_clientside.set_props("camera-position-input", {value: window.vis.position});
  dash_clientside.set_props("camera-position-slider-input", {value: window.vis.position});
  const time_sec = Math.floor(video.currentTime - 0.001); // get time in seconds, round to whole number
  const minutes = Math.floor(time_sec / 60);
  const seconds = time_sec % 60;
  const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  dash_clientside.set_props("current-time-div", {children: label});
};


/**
 * Starts/stops the animation of the train movement.
 * @function
 */
Visualization.prototype.togglePlay = function () {
  if (!window.deck) return;

  const video = document.getElementById('background-video');
  if (!window.vis.animation_running) {
    window.vis.runDeckAnimation();        // run both deck animation and the video
    video.play();
    // define a callback that will run at the end of the animation
    video.onpause = function(){ window.vis.stopDeckAnimation() };
  } else {
    video.pause();
  }
};


/**
 * Changes the current position.
 * @param {number} new_pos - The new position.
 * @function
 */
Visualization.prototype.jumpToPosition = function (new_pos) {
  // update video
  const video = document.getElementById('background-video');
  const videoTime = window.vis.camera_timestamps[new_pos];
  video.currentTime = videoTime;
  // update deck.gl visualization
  window.vis.position = new_pos;
  window.vis.changeLayersData();  // in case that we are not displaying united point cloud
  window.vis.updateDeck();  // call function defined in the JavaScript file
  // update slider and input field and time label
  dash_clientside.set_props("camera-position-slider-input", {value: new_pos});
  dash_clientside.set_props("camera-position-input", {value: new_pos});
  // update time label
  const time_sec = Math.floor(videoTime);
  const minutes = Math.floor(time_sec / 60);
  const seconds = time_sec % 60;
  const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  dash_clientside.set_props("current-time-div", {children: label});
};


/**
 * Reacts to key presses.
 *  - space - play/stop the animation
 *  - right arrow/left arrow - jump 3 seconds forward/backwards
 * @function
 * @param {KeyboardEvent} e - The keypress event. 
 */
Visualization.prototype.reactToKeyPress = function (e) {
  if (e.key === ' ' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
    // prevent moving other elements, except when focus is on an input or text area
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
      // focus is on an input or textarea, do nothing
      return;
    } else {
      // focus is elsewhere
      e.preventDefault();
    }
  }

  if (e.key === ' ') {                   //  play/stop the animation on space press
    window.vis.togglePlay();

  } else if (e.key === 'ArrowLeft') {    // move the animation 3 seconds backwards on arrow left press
    // calculate the new time
    let new_time = window.vis.camera_timestamps[window.vis.position] - 3;
    if (new_time < 0) new_time = 0;
    // find the position corresponding to the new time and jump to it
    let new_pos = window.vis.position;
    while (window.vis.camera_timestamps[new_pos] > new_time) {
      new_pos -= 1;
    }
    window.vis.jumpToPosition(new_pos);
  } else if (e.key === 'ArrowRight') {    // move the animation 3 seconds forward on arrow right press
    // calculate the new time
    let new_time = window.vis.camera_timestamps[window.vis.position] + 3;
    const max_time = window.vis.camera_timestamps[window.vis.frames_cnt - 1];
    if (new_time > max_time) new_time = max_time;
    // find the position corresponding to the new time and jump to it
    let new_pos = window.vis.position;
    while (window.vis.camera_timestamps[new_pos] < new_time) {
      new_pos += 1;
    }
    window.vis.jumpToPosition(new_pos);
  } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {   // do not move camera sliders by arrows
    if (document.activeElement.id === 'camera-x-slider-input' 
      || document.activeElement.id === 'camera-y-slider-input'
      || document.activeElement.id === 'camera-z-slider-input'
      || document.activeElement.id === 'camera-yaw-slider-input'
      || document.activeElement.id === 'camera-pitch-slider-input'
      || document.activeElement.id === 'camera-roll-slider-input') e.preventDefault();
  }
};


/**
 * A global instance of the Visualization class.
 * @type {Visualization}
 * @global
 */
window.vis = new Visualization();


// set the callback to the key press event
document.addEventListener('keydown', window.vis.reactToKeyPress);

// a special accomodation for Google Chrome, to make the animation continue running when
// the user switches to another window in the browser and then switches back to this window
// (Chrome stops the animation when the window is not visible)
document.addEventListener("visibilitychange", () => {
  // wait 40 ms, because this runs before Chrome makes the animation run again
  setTimeout(() => {
    const video = document.getElementById('background-video');
    if (document.visibilityState === "visible" && !video.paused && !video.ended) {
      window.vis.runDeckAnimation();
    }
  }, 40);
});
