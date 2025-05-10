# This file contains definitions of dash callbacks used in the "animation control" part 
# of the app.

from dash import Output, Input, State
import base64

def get_callbacks(app):
    # play/pause the animation
    app.clientside_callback(
        """
        function(btn) {
            window.vis.togglePlay();
        }
        """,
        Input("play-button", "n_clicks"),
        prevent_initial_call=True
    )

    # change the frame by number input or slider
    app.clientside_callback(
        """
        function(input_val, slider_val_dec) {
            if (!isNaN(input_val)) {
                const slider_val = Math.floor(parseFloat(slider_val_dec));
                
                // get the new position - which one triggered the callback, slider or input?
                const triggered_id = dash_clientside.callback_context.triggered_id;
                const new_pos = (triggered_id == 'camera-position-input') ? parseInt(input_val) : slider_val;
                
                if (new_pos != window.vis.position) {
                    window.vis.jumpToPosition(new_pos);
                }
            }
        }
        """,
        Input('camera-position-input', 'value'),
        Input('camera-position-slider-input', 'value'),
        prevent_initial_call=True
    )

    # change animation speed
    app.clientside_callback(
        """
        function(speed_str) {
            let speed = parseFloat(speed_str);
            const video = document.getElementById('background-video');
            video.playbackRate = speed;               // adjust video speed
        }
        """,
        Input('animation-speed-dropdown', 'value'),
        prevent_initial_call=True
    )