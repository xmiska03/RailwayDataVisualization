## @file visualization_tab_callbacks.py
# @author Zuzana Miškaňová
# @brief Contains definitions of Dash callbacks used in the "visualization" tab.

import base64
import tomllib

from dash import Output, Input, State, Patch, no_update

## @brief Registers all callbacks for the "visualization" tab.
# @param app The Dash app instance.
def get_callbacks(app):

    # change point cloud visibility, point size, color scale or opacity
    app.clientside_callback(
        """
        function(layers, point_size, color_scale, opacity) {
            // call function defined in the JavaScript file
            window.vis.updatePCLayerProps(layers.includes('pcl'), point_size, color_scale, opacity);
            return color_scale;
        }
        """,
        Output('scale-colors-store', 'data'),
        Input('point-cloud-checkbox', 'value'),
        Input('point-size-input', 'value'),  # Dash sometimes gives number inputs as strings, sometimes as numbers!
        Input('color-scale-dropdown', 'value'),
        Input('point-opacity-input', 'value'),
        prevent_initial_call=True
    )

    # switch between displaying united and divided united point cloud data
    app.clientside_callback(
        """
        function(dropdown_value) {
            if (dropdown_value == 'united') {
                window.vis.changePCMode(true);
            } else {
                window.vis.changePCMode(false);
            }
            return dropdown_value;
        }
        """,
        Output('point-cloud-type-store', 'data'),
        Input('point-cloud-type-dropdown', 'value'),
        prevent_initial_call=True
    )

    # count an aggregation of the ununited point cloud data (by intensity, for the color scale graph)
    @app.callback(
        Output('pc-data-aggregation', 'data'),
        Input('visualization-data', 'data')
    )
    def recount_data_aggregation(visualization_data):
        new_aggregation = [0 for _ in range(43)]
        for i in range(len(visualization_data["layers"][0]["data"])):
            for point in visualization_data["layers"][0]["data"][i]:
                if int(point[3]) < 43:
                    new_aggregation[int(point[3])] += 1
        return new_aggregation
    
    # count an aggregation of the united point cloud data (by intensity, for the color scale graph)
    @app.callback(
        Output('united-pc-data-aggregation', 'data'),
        Input('united-pc-data', 'data')
    )
    def recount_data_aggregation(united_pc_data):
        new_aggregation = [0 for _ in range(43)]
        for point in united_pc_data:
            if int(point[3]) < 43:
                new_aggregation[int(point[3])] += 1 
        return new_aggregation

    # change the graph of the color scale (when there is new data, new scale boundaries or colors)
    @app.callback(
        Output('color-scale-graph', 'figure'),
        Output('scale-boundaries-store', 'data'),
        Input('scale-from-input', 'value'),
        Input('scale-to-input', 'value'),
        Input('scale-colors-store', 'data'),
        Input('pc-data-aggregation', 'data'),
        Input('united-pc-data-aggregation', 'data'),
        Input('point-cloud-type-store', 'data')
    )
    def change_scale_graph(scale_from_raw, scale_to_raw, colors, pc_data, united_pc_data, pc_type):
        if (scale_from_raw == None or scale_to_raw == None):
            return no_update, no_update
        
        scale_from = int(scale_from_raw)
        scale_to = int(scale_to_raw)
        patched_figure = Patch()
        
        # write data into the graph
        for i in range(43):
            if pc_type == 'united':
                patched_figure["data"][0]["y"][i] = united_pc_data[i]
            else:
                patched_figure["data"][0]["y"][i] = pc_data[i]
        
        # color the graph according to the boundaries and the set colors
        for i in range(43):
            if colors == 'bgr': 
                # blue - green - red      
                if i <= scale_from:
                    patched_figure["data"][0]["marker"]["color"][i] = '#0000FF'   # low intensity - blue
                elif i >= scale_to:
                    patched_figure["data"][0]["marker"]["color"][i] = '#FF0000'   # high intensity - red
                else:
                    # intensity is somewhere on the scale                                              
                    middle_point = (scale_from + scale_to) / 2    # calculate the color
                    if i < middle_point:
                        r = 0
                        g = int((i - scale_from) / (middle_point - scale_from) * 255)
                        b = int(255 - (i - scale_from) / (middle_point - scale_from) * 255)
                    else:
                        r = int((i - middle_point) / (scale_to - middle_point) * 255)
                        g = int(255 - (i - middle_point) / (scale_to - middle_point) * 255)
                        b = 0
                    # convert to HEX color format
                    patched_figure["data"][0]["marker"]["color"][i] = '#{:02x}{:02x}{:02x}'.format(r, g, b) 
            else:
                # yellow - purple
                if i <= scale_from:
                    patched_figure["data"][0]["marker"]["color"][i] = '#FFFF00'   # low intensity - yellow
                elif i >= scale_to:
                    patched_figure["data"][0]["marker"]["color"][i] = '#FF00FF'   # high intensity - purple
                else:
                    # intensity is somewhere on the scale
                    r = 255
                    g = int(255 - (i - scale_from) / (scale_to - scale_from) * 255)
                    b = int((i - scale_from) / (scale_to - scale_from) * 255)
                    # convert to HEX color format
                    patched_figure["data"][0]["marker"]["color"][i] = '#{:02x}{:02x}{:02x}'.format(r, g, b)

        return patched_figure, [scale_from, scale_to]

    # rewrite the change of the boundaries of the color scale to JavaScript so that the visualization updates
    app.clientside_callback(
        """
        function(scale_boundaries) { 
            if (window.vis) {
                const scale_from = scale_boundaries[0];
                const scale_to = scale_boundaries[1];
                const scale_middle = (scale_boundaries[0] + scale_boundaries[1]) / 2;
                window.vis.scale_boundaries = [scale_from, scale_middle, scale_to];
                window.vis.updateLayers();
            }
            return dash_clientside.no_update;
        }
        """,
        Input('scale-boundaries-store', 'data')
    )

    # turn the background video on/off
    @app.callback(
        Output('background-video', 'style'),
        Input('camera-picture-checkbox', 'value'),
    )
    def change_background(options_list):
        patched_style = Patch()
        if 'pic' in options_list:
            patched_style["visibility"] = "visible"
        else:
            patched_style["visibility"] = "hidden"
        return patched_style

    # change vector data visibility, line width or color
    app.clientside_callback(
        """
        function(layers, line_width, line_color) {
            // call function defined in the JavaScript file
            window.vis.updateVectorLayerProps(layers.includes('vec'), line_width, line_color);
        }
        """,
        Input('vector-data-checkbox', 'value'),
        Input('line-width-input', 'value'),
        Input('line-color-picker', 'value'),
        prevent_initial_call=True
    )

    # change virtual camera position
    app.clientside_callback(
        """
        function(x, y, z, yaw, pitch, roll) {
            if (window.vis) {
                window.vis.camera_offset = [parseFloat(x), parseFloat(y), parseFloat(z),
                                        parseFloat(yaw), parseFloat(pitch), parseFloat(roll)];
                // call function defined in the JavaScript file
                window.vis.updateDeck();
            }
        }
        """,
        Input('camera-x-slider-input', 'value'),
        Input('camera-y-slider-input', 'value'),
        Input('camera-z-slider-input', 'value'),
        Input('camera-yaw-slider-input', 'value'),
        Input('camera-pitch-slider-input', 'value'),
        Input('camera-roll-slider-input', 'value'),
        prevent_initial_call=True
    )

    # set the sliders back to default
    app.clientside_callback(
        """
        function(btn, default_offsets) {
            dash_clientside.set_props("camera-x-slider-input", {value: default_offsets[0]});
            dash_clientside.set_props("camera-y-slider-input", {value: default_offsets[1]});
            dash_clientside.set_props("camera-z-slider-input", {value: default_offsets[2]});
            dash_clientside.set_props("camera-yaw-slider-input", {value: default_offsets[3]});
            dash_clientside.set_props("camera-pitch-slider-input", {value: default_offsets[4]});
            dash_clientside.set_props("camera-roll-slider-input", {value: default_offsets[5]});
        }
        """,
        Input('back-to-default-button', 'n_clicks'),
        State('camera-offset-default-store', 'data'),
        prevent_initial_call=True
    )

    # pre-calculate coordinates for distortion
    app.clientside_callback(
        """
        function(dist_params) {
            
            // define a function to precalculate distortion
            function precalculateDistortion() { 
                const beg_time = Date.now();

                const K1 = dist_params[0]
                const K2 = dist_params[1]
                const P1 = dist_params[2]
                const P2 = dist_params[3]
                const K3 = dist_params[4]

                const canvas = document.getElementById("visualization-canvas");
                const height = window.innerHeight;   // canvas does not have initialized size yet
                const width = Math.round(2048/1536 * height);

                window.dist_array = new Array(height);

                // for every pixel on the canvas
                for (let y = 0; y < height; y++) {
                    
                    window.dist_array[y] = new Array(width);
                    
                    for (let x = 0; x < width; x++) {
                        // pre-calculate new coordinates for the pixel

                        // convert to normalized image coordinates
                        const y_norm = (y - Math.round((height-1)/2)) / width
                        const x_norm = (x - Math.round((width-1)/2)) / width
                        const r_pow2 = x_norm*x_norm + y_norm*y_norm    // r^2
                        
                        // count the distortion (radial + tangential)
                        const radial_coef = (1 + K1*r_pow2 + K2*r_pow2*r_pow2 + K3*r_pow2*r_pow2)
                        const x_tangential = (2*P1*x_norm*y_norm + P2*(r_pow2 + 2*x_norm*x_norm))
                        const y_tangential = (P1*(r_pow2 + 2*y_norm*y_norm) + 2*P1*x_norm*y_norm)
                        const x_dist_norm = x_norm * radial_coef + x_tangential
                        const y_dist_norm = y_norm * radial_coef + y_tangential

                        // convert back from normalized image coordinates to pixels
                        const y_dist = Math.round(y_dist_norm * width + Math.round(height/2))
                        const x_dist = Math.round(x_dist_norm * width + Math.round(width/2))

                        window.dist_array[y][x] = [y_dist, x_dist];
                    }
                }
                //console.log("distortion pre-calculation took", Date.now() - beg_time, "ms");
            }

            // the first calculation
            precalculateDistortion();

            // and then every time the canvas is resized (e. g. when window is resized)
            window.onresize = () => {
                precalculateDistortion();
            };

            // redraw so that the new values of parameters show if distortion is on
            if (window.vis.deck_initialized) {
                window.deck.redraw(true);
            }

            return dash_clientside.no_update;
        }
        """,
        Output('distortion-checkbox', 'id'),  # dummy output
        Input('distortion-params-store', 'data')
    )

    # distort the point cloud
    app.clientside_callback(
        """
        function(dist_checkbox_val) {
            if (dist_checkbox_val.includes('dist')) {              // turn distortion on

                // register a distortion-calculating callback which will be called after every render
                window.deck.setProps({
                    onAfterRender: () => {

                        // the canvas into which deck.gl draws
                        const canvas = document.getElementById("visualization-canvas");
                        const gl_ctx = canvas.getContext("webgl2");

                        // the canvas into which this function will draw the result
                        const dist_canvas = document.getElementById("distorted-visualization-canvas");
                        const dist_ctx = dist_canvas.getContext("2d");
                        
                        const width = canvas.width;
                        const height = canvas.height;

                        dist_canvas.width = width;    // set the same size for the canvas with distorted image
                        dist_canvas.height = height;
                        dist_canvas.style.width = canvas.style.width;
                        dist_canvas.style.height = canvas.style.height;

                        const pixelData = new Uint8Array(width * height * 4); // RGBA data
                        gl_ctx.readPixels(0, 0, width, height, gl_ctx.RGBA, gl_ctx.UNSIGNED_BYTE, pixelData);

                        // for every point on the canvas
                        for (let y = 0; y < height; y++) {
                            for (let x = 0; x < width; x++) {
                                
                                // get pixel color
                                const r = pixelData[(y * width + x) * 4];
                                const g = pixelData[(y * width + x) * 4 + 1];
                                const b = pixelData[(y * width + x) * 4 + 2];
                                const a = pixelData[(y * width + x) * 4 + 3];
                                if (a == 0) {
                                    continue;    // empty space, no need to write anything
                                }

                                // new coordinates for the pixel are pre-calculated
                                
                                if (window.dist_array[y] == undefined 
                                  || window.dist_array[y][x] == undefined) {
                                    continue;
                                }
                                
                                const y_dist = window.dist_array[y][x][0];
                                const x_dist = window.dist_array[y][x][1];
                                // write the pixel on the new position
                                dist_ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a/255})`;
                                dist_ctx.fillRect(x_dist, (height - 1) - y_dist, 1, 1);
                            }
                        }
                    }
                });

                // redraw so that the callback is called immediately even if the animation is not running
                window.deck.redraw(true);
                
                // make the original canvas invisible and the distorted one visible
                const canvas = document.getElementById("visualization-canvas");
                const dist_canvas = document.getElementById("distorted-visualization-canvas");
                canvas.style.visibility = "hidden";
                dist_canvas.style.visibility = "visible";
                
            } else {            // turn distortion off

                // unregister the callback
                window.deck.setProps({
                    onAfterRender: () => {}
                });

                // make the original canvas visible and the distorted one invisible
                const canvas = document.getElementById("visualization-canvas");
                const dist_canvas = document.getElementById("distorted-visualization-canvas");
                canvas.style.visibility = "visible";
                dist_canvas.style.visibility = "hidden";
            }
        }
        """,
        Input('distortion-checkbox', 'value'),
        prevent_initial_call=True
    )

    # export workspace settings
    @app.callback(
        Output("workspace-download", "data"),
        Input("export-workspace-button", "n_clicks"),
        
        State('point-cloud-checkbox', 'value'),
        State('point-cloud-type-dropdown', 'value'),
        State('point-size-input', 'value'),
        State('color-scale-dropdown', 'value'),
        State('scale-from-input', 'value'),
        State('scale-to-input', 'value'),
        State('point-opacity-input', 'value'),

        State('camera-picture-checkbox', 'value'),

        State('vector-data-checkbox', 'value'),
        State('line-width-input', 'value'),
        State('line-color-picker', 'value'),

        State('camera-x-slider-input', 'value'),
        State('camera-y-slider-input', 'value'),
        State('camera-z-slider-input', 'value'),
        State('camera-yaw-slider-input', 'value'),
        State('camera-pitch-slider-input', 'value'),
        State('camera-roll-slider-input', 'value'),

        State('distortion-checkbox', 'value'),

        State('train-profile-checkbox', 'value'),
        State('profile-distance-dropdown', 'value'),
        State('profile-width-input', 'value'),
        State('profile-color-picker', 'value'),

        State('profile-line-checkbox', 'value'),
        State('profile-line-width-input', 'value'),
        State('profile-line-color-picker', 'value'),
        
        prevent_initial_call=True
    )
    def export_workspace(n_clicks, 
             pc_checkbox, pc_type, point_size, color_scale, scale_from, scale_to, point_opacity,
             video_checkbox,
             vec_data_checkbox, vec_data_width, vec_data_color,
             cam_offset_x, cam_offset_y, cam_offset_z, cam_offset_yaw, cam_offset_pitch, cam_offset_roll, 
             distortion_checkbox,
             profile_checkbox, profile_dist, profile_width, profile_color,
             profile_line_checkbox, profile_line_width, profile_line_color,
             ):
        content = (
            '# point cloud \n'
            f'display_point_cloud = {"true" if "pcl" in pc_checkbox else "false"} \n'
            f'point_cloud_type = "{pc_type}" \n'
            f'point_size = {point_size} \n'
            f'color_scale = "{color_scale}" \n'
            f'color_scale_from = {scale_from} \n'
            f'color_scale_to = {scale_to} \n'
            f'point_cloud_opacity = {point_opacity} \n'
            '\n'
            '# video \n'
            f'display_video = {"true" if "pic" in video_checkbox else "false"} \n'
            '\n'
            '# vector data \n'
            f'display_vector_data = {"true" if "vec" in vec_data_checkbox else "false"} \n'
            f'vector_data_line_width = {vec_data_width} \n'
            f'vector_data_line_color = "{vec_data_color}" \n'
            '\n'
            '# camera position offset \n'
            f'camera_offset_x = {cam_offset_x} \n'
            f'camera_offset_y = {cam_offset_y} \n'
            f'camera_offset_z = {cam_offset_z} \n'
            f'camera_offset_yaw = {cam_offset_yaw} \n'
            f'camera_offset_pitch = {cam_offset_pitch} \n'
            f'camera_offset_roll = {cam_offset_roll} \n'
            '\n'
            '# distortion \n'
            f'distortion = {"true" if "dist" in distortion_checkbox else "false"} \n'
            '\n'
            '# train profile \n'
            f'display_train_profile = {"true" if "profile" in profile_checkbox else "false"} \n'
            f'train_profile_distance = "{profile_dist}" \n'
            f'train_profile_line_width = {profile_width} \n'
            f'train_profile_line_color = "{profile_color}" \n'
            '\n'
            '# line through train profile positions \n'
            f'display_profile_line = {"true" if "line" in profile_line_checkbox else "false"} \n'
            f'profile_line_line_width = {profile_line_width} \n'
            f'profile_line_line_color = "{profile_line_color}" \n'
            '\n'
        )
        return dict(content=content, filename="workspace.toml")
    
    # import workspace settings
    @app.callback(
        Output('point-cloud-checkbox', 'value'),
        Output('point-cloud-type-dropdown', 'value'),
        Output('point-size-input', 'value'),
        Output('color-scale-dropdown', 'value'),
        Output('scale-from-input', 'value'),
        Output('scale-to-input', 'value'),
        Output('point-opacity-input', 'value'),

        Output('camera-picture-checkbox', 'value'),

        Output('vector-data-checkbox', 'value'),
        Output('line-width-input', 'value'),
        Output('line-color-picker', 'value'),

        Output('camera-x-slider-input', 'value'),
        Output('camera-y-slider-input', 'value'),
        Output('camera-z-slider-input', 'value'),
        Output('camera-yaw-slider-input', 'value'),
        Output('camera-pitch-slider-input', 'value'),
        Output('camera-roll-slider-input', 'value'),
        Output('camera-offset-default-store', 'data'),

        Output('distortion-checkbox', 'value'),

        Output('train-profile-checkbox', 'value'),
        Output('profile-distance-dropdown', 'value'),
        Output('profile-width-input', 'value'),
        Output('profile-color-picker', 'value'),

        Output('profile-line-checkbox', 'value'),
        Output('profile-line-width-input', 'value'),
        Output('profile-line-color-picker', 'value'),

        Input('import-workspace-upload', 'contents'),
        prevent_initial_call = True
    )
    def import_workspace(file_content):
        if file_content is None:
            return (no_update,) * 26

        # new file uploaded
        content_type, content_string = file_content.split(',')
        decoded = base64.b64decode(content_string)
        data = tomllib.loads(decoded.decode("utf-8"))

        # load settings from toml file
        cam_offset_x = data["camera_offset_x"]
        cam_offset_y = data["camera_offset_y"]
        cam_offset_z = data["camera_offset_z"]
        cam_offset_yaw = data["camera_offset_yaw"]
        cam_offset_pitch = data["camera_offset_pitch"]
        cam_offset_roll = data["camera_offset_roll"]

        return (
            ["pcl"] if data["display_point_cloud"] else [],
            data["point_cloud_type"],
            data["point_size"],
            data["color_scale"],
            data["color_scale_from"],
            data["color_scale_to"],
            data["point_cloud_opacity"],

            ["pic"] if data["display_video"] else [],

            ["vec"] if data["display_vector_data"] else [],
            data["vector_data_line_width"],
            data["vector_data_line_color"],

            cam_offset_x,
            cam_offset_y,
            cam_offset_z,
            cam_offset_yaw,
            cam_offset_pitch,
            cam_offset_roll,
            [cam_offset_x, cam_offset_y, cam_offset_z, cam_offset_yaw, cam_offset_pitch, cam_offset_roll],

            ["dist"] if data["distortion"] else [],

            ["profile"] if data["display_train_profile"] else [],
            data["train_profile_distance"],
            data["train_profile_line_width"],
            data["train_profile_line_color"],

            ["line"] if data["display_profile_line"] else [],
            data["profile_line_line_width"],
            data["profile_line_line_color"]
        )
           

