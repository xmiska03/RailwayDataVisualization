# This file contains definitions of dash callbacks used in the "animation control" part 
# of the app.

from dash import Output, Input, State
import base64

def get_callbacks(app):
    # play/pause the animation
    # this function handles the video, deck.gl visualization and play button icon
    app.clientside_callback(
        """
        function(btn) {
            const video = document.getElementById('background-video');
            const icon = document.getElementById("play-button").querySelector("i");

            if (!window.animation_running) {
                window.runDeckAnimation();         // run both deck animation and the video
                video.play();
                icon.classList.remove("bi-play-fill");
                icon.classList.add("bi-pause-fill");
            } else {
                // the video will not pause immediately, so the pause event needs to be used
                video.onpause=function(){ window.stopDeckAnimation() };
                video.pause();
                icon.classList.add("bi-play-fill");
                icon.classList.remove("bi-pause-fill");
            }
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
                
                if (new_pos != window.position) {
                    // update video
                    const video = document.getElementById('background-video');
                    const videoTime = window.camera_timestamps[new_pos];
                    video.currentTime = videoTime;

                    // update deck.gl visualization
                    window.position = new_pos;
                    window.changeLayersData();  // in case that we are not displaying united point cloud
                    window.updateDeck();  // call function defined in the JavaScript file

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
            window.frame_duration = 40 / speed;       // adjust deck animation speed (used in visualization.js)
            const video = document.getElementById('background-video');
            video.playbackRate = speed;               // adjust video speed
        }
        """,
        Input('animation-speed-dropdown', 'value'),
        prevent_initial_call=True
    )