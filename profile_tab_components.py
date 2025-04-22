from dash import html, dcc
import dash_bootstrap_components as dbc

from params import PROFILE_LINE_WIDTH, LINE_WIDTH

profile_distance_widget = [
    dbc.Col(html.Div("Vzdálenost průj. profilu: "), width=5),
    dbc.Col(dbc.Select(
        options={'25': '25m', '50': '50m', '75': '75m', '100': '100m'},
        value='25',
        id='profile-distance-dropdown',
    ), width=6)
]

profile_width_widget = [
    dbc.Col(html.Div("Tloušťka čar: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{PROFILE_LINE_WIDTH}",
        id="profile-width-input",
        type="number",
        min=1,
        max=15,
        step=1
    ), width=6)
]

profile_color_widget = [
    dbc.Col(html.Div("Barva čar: "), width=5),
    dbc.Col(dbc.Input(
        type="color",
        id="profile-color-picker",
        value="#e250ff",
    ), width=6)
]

profile_line_width_widget = [
    dbc.Col(html.Div("Tloušťka čáry: "), width=5),
    dbc.Col(dbc.Input(
        value=f"{LINE_WIDTH}",
        id="profile-line-width-input",
        type="number",
        min=1,
        max=15,
        step=1
    ), width=6)
]

profile_line_color_widget = [
    dbc.Col(html.Div("Barva čáry: "), width=5),
    dbc.Col(dbc.Input(
        type="color",
        id="profile-line-color-picker",
        value="#e8af10",
    ), width=6)
]

profile_tab = [
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat průjezdný profil', 'value': 'profile'}],
            value=['profile'],
            id='train-profile-checkbox',
            style={'marginTop': '15px'}
        )
    ),
    dbc.Row(profile_distance_widget, style={'marginTop': '15px'}),
    dbc.Row(profile_width_widget, style={'marginTop': '15px'}),
    dbc.Row(profile_color_widget, style={'marginTop': '15px'}),

    dbc.Row(html.Hr(), style={'marginTop': '15px'}),
    dbc.Row(html.Div("Čára přes pozice průjezdného profilu", style={"fontWeight": "bold", "textAlign": "center", "paddingBottom": "0.5em",})),
    dbc.Row(dcc.Checklist(
            options=[{'label': ' zobrazovat čáru', 'value': 'line'}],
            value=['line'],
            id='profile-line-checkbox',
            style={'marginTop': '15px'}
        )
    ),
    dbc.Row(profile_line_width_widget, style={'marginTop': '15px'}),
    dbc.Row(profile_line_color_widget, style={'marginTop': '15px'})
    
]