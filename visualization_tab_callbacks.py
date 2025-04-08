# This file contains definitions of dash callbacks used in the "visualization" tab 
# of the app.

from dash import Output, Input, Patch

def get_callbacks(app):
    
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

    # change point cloud visibility, point size, color scale or opacity
    app.clientside_callback(
        """
        function(layers, point_size, color_scale, opacity) {  
            if (window.updatePCLayerProps) {
                // call function defined in the JavaScript file
                window.updatePCLayerProps(layers.includes('pcl'), point_size, color_scale, opacity);
            }
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
        Input('display-united-store', 'data')
    )
    def change_scale_graph(scale_from_raw, scale_to_raw, colors, pc_data, united_pc_data, display_united):
        scale_from = int(scale_from_raw)
        scale_to = int(scale_to_raw)
        patched_figure = Patch()
        
        # write data into the graph
        for i in range(43):
            if display_united:
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
            window.scale_from = scale_boundaries[0];
            window.scale_to = scale_boundaries[1];
            window.scale_middle = (scale_boundaries[0] + scale_boundaries[1]) / 2;
            window.updatePCLayer();
            return dash_clientside.no_update;
        }
        """,
        Output('scale-from-input', 'id'),  # dummy output so that the initial call occurs
        Input('scale-boundaries-store', 'data')
    )

    # change vector data visibility, line width or color
    app.clientside_callback(
        """
        function(layers, line_width, line_color) {
            if (window.updatePathLayerProps) {
                // call function defined in the JavaScript file
                window.updatePathLayerProps(layers.includes('vec'), line_width, line_color);
            }
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
        function(x, y, z, yaw, pitch) {
            if (window.updateDeck) {
                window.camera_offset_x = parseFloat(x);
                window.camera_offset_y = parseFloat(y);
                window.camera_offset_z = parseFloat(z);
                window.camera_offset_yaw = parseFloat(yaw);
                window.camera_offset_pitch = parseFloat(pitch);
                console.log("new virtual camera settings: ", x, y, z, yaw, pitch)

                // call function defined in the JavaScript file
                window.updateDeck();
            }
        }
        """,
        Input('camera-x-slider-input', 'value'),
        Input('camera-y-slider-input', 'value'),
        Input('camera-z-slider-input', 'value'),
        Input('camera-yaw-slider-input', 'value'),
        Input('camera-pitch-slider-input', 'value'),
        prevent_initial_call=True
    )

    # set the sliders back to default
    app.clientside_callback(
        """
        function(btn) {
            dash_clientside.set_props("camera-x-slider-input", {value: 0});
            dash_clientside.set_props("camera-y-slider-input", {value: 0});
            dash_clientside.set_props("camera-z-slider-input", {value: 0});
            dash_clientside.set_props("camera-yaw-slider-input", {value: 0});
            dash_clientside.set_props("camera-pitch-slider-input", {value: 0});
        }
        """,
        Input('back-to-default-button', 'n_clicks'),
        prevent_initial_call=True
    )

    # set far plane
    app.clientside_callback(
        """
        function(far_plane) {
            // todo
        }
        """,
        Input('far-plane-input', 'value')
    )

    # distort the point cloud
    app.clientside_callback(
        """
        function(btn) {
            const beg_time = Date.now();

            const K1 = -0.1832170424487164 
            const K2 = 0.02691675026209955
            const P1 = -0.001191374354805736
            const P2 = 0.000804309339521888
            const K3 = 0.3354456739081583
            
            const width = 910;
            const height = 682;

            window.dist_array = new Array(height);

            // for every pixel on the canvas
            for (let y = 0; y < height; y++) {
                
                window.dist_array[y] = new Array(width);
                
                for (let x = 0; x < width; x++) {
                    // pre-calculate new coordinates for the pixel

                    // convert to normalized image coordinates
                    const y_norm = (y - Math.round(height/2)) / width
                    const x_norm = (x - Math.round(width/2)) / width
                    const r_pow2 = x_norm*x_norm + y_norm*y_norm    // r^2
                    
                    // count the radial distortion
                    const px_coef = (1 + K1*r_pow2 + K2*r_pow2*r_pow2 + K3*r_pow2*r_pow2)
                    const x_dist_norm = x_norm * px_coef
                    const y_dist_norm = y_norm * px_coef

                    // count the tangential distortion
                    /*
                    x_dist_norm = x_norm + (2*P1*x_norm*y_norm + P2*(r_pow2 + 2*x_norm*x_norm))
                    y_dist_norm = y_norm + (P1*(r_pow2 + 2*y_norm*y_norm) + 2*P1*x_norm*y_norm)
                    */

                    // convert back from normalized image coordinates to pixels
                    const y_dist = Math.round(y_dist_norm * width + Math.round(height/2))
                    const x_dist = Math.round(x_dist_norm * width + Math.round(width/2))

                    window.dist_array[y][x] = [y_dist, x_dist];
                }
            }
            //console.log("distortion pre-calculation took", Date.now() - beg_time, "ms");
            return dash_clientside.no_update;
        }
        """,
        Output('distortion-button', 'id'),  # dummy input and output
        Input('distortion-button', 'id')
    )

    # distort the point cloud
    app.clientside_callback(
        """
        function(btn) {
            const beg_time = Date.now();

            const K1 = -0.1832170424487164 
            const K2 = 0.02691675026209955
            const P1 = -0.001191374354805736
            const P2 = 0.000804309339521888
            const K3 = 0.3354456739081583
            
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

            //gl_ctx.bindFramebuffer(gl_ctx.FRAMEBUFFER, null); 
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
                    const y_dist = window.dist_array[y][x][0];
                    const x_dist = window.dist_array[y][x][1];

                    // write the pixel on the new position
                    dist_ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${a/255})`;
                    dist_ctx.fillRect(x_dist, (height - 1) - y_dist, 1, 1);
                }
            }

            canvas.style.visibility = "hidden";
            console.log("distortion calculation took", Date.now() - beg_time, "ms");
        }
        """,
        Input('distortion-button', 'n_clicks'),
        prevent_initial_call=True
    )

