from dash import Output, Input


def get_callbacks(app):
    
    # roll out the side panel on button click
    app.clientside_callback(
        """
        function(n_clicks) {
            const side_panel = document.getElementById('side-panel-div');
            const bottom_panel = document.getElementById('bottom-panel-div');
            const icon = document.getElementById("roll-out-button").querySelector("i");
            
            if (n_clicks % 2 == 0) {
                // roll out side panel
                bottom_panel.style.width = 'calc(100% - 500px)';
                side_panel.style.width = '500px';
                // change the icon
                icon.classList.remove("bi-chevron-right");
                icon.classList.add("bi-chevron-left");
            } else {
                // pack side panel
                bottom_panel.style.width = '100%'
                side_panel.style.width = 0;
                // change the icon
                icon.classList.add("bi-chevron-right");
                icon.classList.remove("bi-chevron-left");
            }
        }
        """,
        Input("roll-out-button", "n_clicks")
    )

    # change color mode by switch
    app.clientside_callback(
        """
        function(switch_on) {
            let color = '';
            let opposite_color = '';

            if (switch_on) {
                // light mode
                color = 'white';
                opposite_color = '#212529';
                document.documentElement.setAttribute('data-bs-theme', 'light');
            } else {
                // dark mode
                color = '#212529';
                opposite_color = 'white'
                document.documentElement.setAttribute('data-bs-theme', 'dark');
            }

            document.getElementById("roll-out-button").style.backgroundColor = color;
            document.getElementById("roll-out-button").style.borderColor = opposite_color;
            document.getElementById("roll-out-button").querySelector("i").style.color = opposite_color;      
            document.getElementById("color-mode-div").style.backgroundColor = color;
            document.getElementById("camera-position-div").style.backgroundColor = color;
            document.getElementById("play-controls-div").style.backgroundColor = color;
            document.getElementById("play-button").querySelector("i").style.color = opposite_color;  
            return dash_clientside.no_update;
        }
        """,
        Output("color-mode-switch", "id"),  # dummy output needed so that the initial call occurs
        Input("color-mode-switch", "value"),
    )
