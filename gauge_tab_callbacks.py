from dash import Output, Input, State, Patch, clientside_callback

def get_callbacks(app):
    # change loading gauge visibility or distance
    app.clientside_callback(
        """
        function(layers, slider_val) {
            if (window.updateGaugeLayerProps) {
                // call function defined in the JavaScript file
                window.updateGaugeLayerProps(layers.includes('gauge'), Math.floor(parseFloat(slider_val)));
            }
        }
        """,
        Input('loading-gauge-checkbox', 'value'),
        Input('gauge-distance-slider-input', 'value'),
        prevent_initial_call=True
    )
