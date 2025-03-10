from dash import html, dcc
import dash_bootstrap_components as dbc

from params import GAUGE_LINE_WIDTH

gauge_line_width_widget = [
    dbc.Col(html.Div("Tloušťka čar: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{GAUGE_LINE_WIDTH}",
        id="gauge-line-width-input",
        type="number",
        min=10,
        max=150,
        step=5
    ), width=6)
]

gauge_line_color_widget = [
    dbc.Col(html.Div("Barva čar: "), width=5),
    dbc.Col(dbc.Input(
        type="color",
        id="gauge-line-color-picker",
        value="#e250ff",
    ), width=6)
]

gauge_tab = [
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat průjezdný profil', 'value': 'gauge'}],
            value=['gauge'],
            id='loading-gauge-checkbox',
            style={'marginTop':'20px', 'marginBottom':'20px'}
        )
    ),
    dbc.Row(html.Div("Vzdálenost průjezdného profilu:")),
    dbc.Row(dcc.Input(
        value=100,
        id="gauge-distance-slider-input",
        type="range",
        min=10,
        max=210,
        style={"margin":"10px", "width": "90%"}
    )),
    dbc.Row(gauge_line_width_widget),
    dbc.Placeholder(color="black", size="xs"),
    dbc.Row(gauge_line_color_widget),
    dbc.Placeholder(color="black", size="xs"),
]