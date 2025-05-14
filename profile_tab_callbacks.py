## @file profile_tab_callbacks.py
# @author Zuzana Miškaňová
# @brief Contains definitions of Dash callbacks used in the "profile" tab.

from dash import Input

## @brief Registers all callbacks for the "profile" tab.
# @param app The Dash app instance.
def get_callbacks(app):
    
    # change train profile distance
    app.clientside_callback(
        """
        function(distance) {
            window.vis.profile_distance = distance;
            window.vis.updateDeck();
        }
        """,
        Input('profile-distance-dropdown', 'value'),
        prevent_initial_call=True
    )

    # change train profile visibility, line width or color
    app.clientside_callback(
        """
        function(layers, line_width, line_color) {
            // call function defined in the JavaScript file
            window.vis.updateProfileLayerProps(layers.includes('profile'), line_width, line_color);
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
            // call function defined in the JavaScript file
            window.vis.updateProfileLineLayerProps(layers.includes('line'), line_width, line_color);
        }
        """,
        Input('profile-line-checkbox', 'value'),
        Input('profile-line-width-input', 'value'),
        Input('profile-line-color-picker', 'value'),
        prevent_initial_call=True
    )
