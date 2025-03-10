from dash import Output, Input, State, Patch, clientside_callback

def get_callbacks(app):
    # change loading gauge visibility or distance
    app.clientside_callback(
        """
        function(layers, slider_val, line_width, line_color) {
            if (window.updateGaugeLayerProps) {
                // call function defined in the JavaScript file
                window.updateGaugeLayerProps(layers.includes('gauge'), Math.floor(parseFloat(slider_val)),
                                             line_width, line_color);
            }
        }
        """,
        Input('loading-gauge-checkbox', 'value'),
        Input('gauge-distance-slider-input', 'value'),
        Input('gauge-line-width-input', 'value'),
        Input('gauge-line-color-picker', 'value'),
        prevent_initial_call=True
    )
