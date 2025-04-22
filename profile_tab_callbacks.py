from dash import Output, Input, State, Patch, clientside_callback

def get_callbacks(app):
    # change train profile distance
    app.clientside_callback(
        """
        function(distance) {
            window.profile_distance = distance;
            window.updateDeck();
        }
        """,
        Input('profile-distance-dropdown', 'value'),
        prevent_initial_call=True
    )

    # change train profile visibility, line width or color
    app.clientside_callback(
        """
        function(layers, line_width, line_color) {
            if (window.updateProfileLayerProps) {
                // call function defined in the JavaScript file
                window.updateProfileLayerProps(layers.includes('profile'), line_width, line_color);
            }
        }
        """,
        Input('train-profile-checkbox', 'value'),
        Input('profile-width-input', 'value'),
        Input('profile-color-picker', 'value'),
        prevent_initial_call=True
    )

    # change profile line visibility, line width or color
    app.clientside_callback(
        """
        function(layers, line_width, line_color) {
            if (window.updateProfileLineLayerProps) {
                // call function defined in the JavaScript file
                window.updateProfileLineLayerProps(layers.includes('line'), line_width, line_color);
            }
        }
        """,
        Input('profile-line-checkbox', 'value'),
        Input('profile-line-width-input', 'value'),
        Input('profile-line-color-picker', 'value'),
        prevent_initial_call=True
    )
