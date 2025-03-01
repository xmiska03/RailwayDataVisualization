from dash import html, dcc
import dash_bootstrap_components as dbc

gauge_tab = [
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat průjezdný profil', 'value': 'pcl'}],
            value=['pcl'],
            id='loading-gauge-checkbox',
            style={'marginTop':'20px', 'marginBottom':'20px'}
        )
    ),
    dbc.Row(html.Div("Vzdálenost průjezdného profilu:")),
    dbc.Row(dcc.Input(
        value=50,
        id="gauge-distance-slider-input",
        type="range",
        min=20,
        max=80,
        style={"margin":"10px", "width": "90%"}
    ))
]