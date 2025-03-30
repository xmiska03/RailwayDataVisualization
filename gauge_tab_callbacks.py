from dash import Output, Input, State, Patch, clientside_callback

def get_callbacks(app):
    # change loading gauge distance
    app.clientside_callback(
        """
        function(distance) {
            window.gauge_distance = distance;
            window.updateDeck();
            window.updatePathLayer();
        }
        """,
        Input('gauge-distance-dropdown', 'value'),
        prevent_initial_call=True
    )

    # change loading gauge visibility, line width or color
    app.clientside_callback(
        """
        function(layers, line_width, line_color) {
            if (window.updateGaugeLayerProps) {
                // call function defined in the JavaScript file
                window.updateGaugeLayerProps(layers.includes('gauge'), line_width, line_color);
            }
        }
        """,
        Input('loading-gauge-checkbox', 'value'),
        Input('gauge-line-width-input', 'value'),
        Input('gauge-line-color-picker', 'value'),
        prevent_initial_call=True
    )
