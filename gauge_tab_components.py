from dash import html, dcc
import dash_bootstrap_components as dbc

from params import GAUGE_LINE_WIDTH, LINE_WIDTH

gauge_distance_widget = [
    dbc.Col(html.Div("Vzdálenost průj. profilu: "), width=5),
    dbc.Col(dbc.Select(
        options={'25': '25m', '50': '50m', '75': '75m', '100': '100m'},
        value='25',
        id='gauge-distance-dropdown',
    ), width=6)
]

gauge_width_widget = [
    dbc.Col(html.Div("Tloušťka čar: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{GAUGE_LINE_WIDTH}",
        id="gauge-width-input",
        type="number",
        min=1,
        max=15,
        step=1
    ), width=6)
]

gauge_color_widget = [
    dbc.Col(html.Div("Barva čar: "), width=5),
    dbc.Col(dbc.Input(
        type="color",
        id="gauge-color-picker",
        value="#e250ff",
    ), width=6)
]

gauge_line_width_widget = [
    dbc.Col(html.Div("Tloušťka čar: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{LINE_WIDTH}",
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
        value="#e8af10",
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
    dbc.Row(gauge_width_widget, style={'marginTop': '15px'}),
    dbc.Row(gauge_color_widget, style={'marginTop': '15px'}),

    dbc.Row(html.Hr(), style={'marginTop': '15px'}),
    dbc.Row(html.Div("Čára přes pozice průjezdného profilu", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat čáru', 'value': 'line'}],
            value=['line'],
            id='gauge-line-checkbox',
            style={'marginTop': '15px'}
        )
    ),
    dbc.Row(gauge_line_width_widget, style={'marginTop': '15px'}),
    dbc.Row(gauge_line_color_widget, style={'marginTop': '15px'})
    
]