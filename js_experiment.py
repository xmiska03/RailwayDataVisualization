from dash import Dash, html, dcc, callback, Output, Input, State, Patch, ctx, clientside_callback
import dash_bootstrap_components as dbc

# create a Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"]
)


deckgl_visualization = html.Div(children=
    [
        dcc.Store(data="Cislo: ", id='permanent-store'),
        dcc.Store(data=0, id='varying-store'),
        html.Div(
            [html.Div(
                children=[
                    html.Button("Train go!", id='go-button'),
                    html.Canvas(id='visualization-canvas'), 
                ], id='visualization-div2', style={
                    "height": "100vh", 
                    "width": "40vw"
                }
            )],
            style={"position": "relative"}
        )
    ]
)

app.layout = html.Div(children=
    [
        html.H4(
            "Experiment",
            style={"textAlign": "center", "padding":"10px"}
        ),
        deckgl_visualization
    ]
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0 && window.updateLayerPosition) {
            window.updateLayerPosition();  // Call the global function
        }
        return '';
    }
    """,
    Output('varying-store', 'data'),
    Input('go-button', 'n_clicks')
)

if __name__ == "__main__":
    app.run(debug=True)