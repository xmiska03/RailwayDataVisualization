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

    # change vector data visibility
    app.clientside_callback(
        """
        function(layers) {
            if (window.updateLineLayerProps) {
                // call function defined in the JavaScript file
                window.updateLineLayerProps(layers.includes('vec'));
            }
        }
        """,
        Input('vector-data-checkbox', 'value'),
        prevent_initial_call=True
    )

    # change animation speed
    app.clientside_callback(
        """
        function(speed_str) {
            let speed = parseFloat(speed_str);
            window.frame_duration = 40 / speed;       // adjust deck animation speed (used in visualization.js)
            const video = document.getElementById('background-video');
            video.playbackRate = speed;               // adjust video speed
        }
        """,
        Input('animation-speed-dropdown', 'value'),
        prevent_initial_call=True
    )
