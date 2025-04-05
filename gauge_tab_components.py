from dash import html, dcc
import dash_bootstrap_components as dbc

from params import GAUGE_LINE_WIDTH

gauge_distance_widget = [
    dbc.Col(html.Div("Vzdálenost průj. profilu: "), width=5),
    dbc.Col(dcc.Dropdown(
        options={'25': '25m', '50': '50m', '75': '75m', '100': '100m'},
        value='25',
        clearable=False,
        id='gauge-distance-dropdown',
        #style={'width':'80px'}
    ), width=6)
]

gauge_line_width_widget = [
    dbc.Col(html.Div("Tloušťka čar: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{GAUGE_LINE_WIDTH}",
        id="gauge-line-width-input",
        type="number",
        min=1,
        max=15,
        step=1
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
            style={'marginTop': '15px'}
        )
    ),
    dbc.Row(gauge_distance_widget, style={'marginTop': '15px'}),
    dbc.Row(gauge_line_width_widget, style={'marginTop': '15px'}),
    dbc.Row(gauge_line_color_widget, style={'marginTop': '15px'})
]