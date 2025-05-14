## @file animation_control_callbacks.py
# @author Zuzana Miškaňová
# @brief Contains definitions of Dash callbacks used in the "animation control" panel.

from dash import Output, Input, State
import base64

## @brief Registers all callbacks for the "animation control" panel.
# @param app The Dash app instance.
def get_callbacks(app):

    ## @brief Plays and pauses the animation.
    # @param btn The "play" button clicks.
    app.clientside_callback(
        """
        function(btn) {
            window.vis.togglePlay();
        }
        """,
        Input("play-button", "n_clicks"),
        prevent_initial_call=True
    )
 
    ## @brief Changes the position in the animation by the frame number input and by the slider.
    # @param input_val The frame number input value.
    # @param slider_val_dec The slider value.
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

    ## @brief Changes the animation speed.
    # @param speed_str The animation speed input.
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