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
        }
        """,
        Input('point-cloud-checkbox', 'value'),
        Input('point-size-input', 'value'),  # Dash sometimes gives number inputs as strings, sometimes as numbers!
        Input('point-color-dropdown', 'value'),
        Input('point-opacity-input', 'value'),
        prevent_initial_call=True
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

                    // calculate new coordinates for the pixel

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
