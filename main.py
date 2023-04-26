import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import main
from functions import *
import plotly.express as px
from jupyter_dash import JupyterDash
import dash
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc  # conda install dash_bootstrap_components
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import dash_loading_spinners as dls # pip install dash-loading-spinners

# inizializzazione dataset
df_artcode = get_df_artcode()
df_artcode_references = get_df_artcode_references()
df_errors_plus_complete = pd.read_csv("errors_plus.csv")
# Matieni solo running = true. Filtro qui in modo da velocizzare la creazione del grafico. Non dipende da input
df_errors_plus_running_true = df_errors_plus_complete[df_errors_plus_complete["running"] == True]

# components
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
grafico = dcc.Graph(figure={}, style={"display": "none"})
grafico2 = dcc.Graph(figure={}, style={"display": "none"})
#discard = dcc.RadioItems(options=["True", "False", "Entrambi"], value="Entrambi")
discard = dbc.RadioItems(options=[{"label": "True", "value": "True"},
                                  {"label": "False", "value": "False"},
                                  {"label": "Entrambi", "value": "Entrambi"},],
            value="Entrambi",
            id="discard",
            inline=True,
        )
program = dcc.Dropdown(options=get_programs_list(),style={'color': 'black'})
family = dcc.Dropdown(options=list(range(0, 9)),style={'color': 'black'})
macchina = dcc.Dropdown(options=get_machines_list(),style={'color': 'black'})
bottone = dbc.Button("Crea grafico", color="primary")
messaggio_errore = dbc.Alert("Non è stato selezionato il programma.", color="danger", is_open=False)
lines = dbc.RadioItems(options=[{"label": "Linea RPM", "value": "RPM"},
                                  {"label": "Linea step", "value": "step"},
                                  {"label": "Entrambe le linee", "value": "Entrambi"},],
            value="Entrambi",
            id="lines",
            inline=True,
        )
layer = dbc.RadioItems(options=[{"label": "Mostra economie", "value": "economie"},
                                  {"label": "Mostra zone", "value": "zone"},
                                  {"label": "Non mostrare economie/zone", "value": "nessuno"},],
            value="nessuno",
            id="layer",
            inline=True,
        )
# customize layout
app.layout = dbc.Container([
    # discard
    dbc.Row([
        dbc.Col(dbc.Label("Discard:"),width=2),
        dbc.Col([discard],width=6)
    ], justify='center'),
    # program
    dbc.Row([
        dbc.Col(dbc.Label("Program:"),width=2),
        dbc.Col([program], width=6)
    ], justify='center'),
    # famiglia
    dbc.Row([
        dbc.Col(dbc.Label("Family:"),width=2),
        dbc.Col([family], width=6)
    ], justify='center'),
    # macchina
    dbc.Row([
        dbc.Col(dbc.Label("Macchina:"),width=2),
        dbc.Col([macchina], width=6)
    ], justify='center'),
    # scelta rpm/step
    dbc.Row([
        dbc.Col(dbc.Label("RPM/Step:"), width=2),
        dbc.Col([lines], width={"size": 6, })
    ], justify='center'),
    # scelta zone
    dbc.Row([
        dbc.Col(dbc.Label("Zone/Economie:"),width=2),
        dbc.Col([layer], width={"size": 6,})
    ], justify='center'),
    # bottone
    dbc.Row([
        dbc.Col([bottone],width=2)
    ], justify='center'),
    # messaggio di errore
    dbc.Row([
        dbc.Col([html.Br(),messaggio_errore], width=6)
    ], justify='center'),
    # break row before figure
    html.Br(),
    # grafico
    dbc.Row([
        dbc.Col(
            dls.Hash( #loader component
                grafico,
                color="#435278",
                speed_multiplier=2,
                size=100,
            ),width=12
        )
    ]),
    # grafico2
    dbc.Row([
        dbc.Col(
            dls.Hash(
                grafico2,
                color="#435278",
                speed_multiplier=2,
                size=100,
            ),width=12
        )
    ])
],fluid=True)


# callback
@app.callback(
    Output(grafico, "figure"),
    Output(grafico, "style"),
    Output(grafico2, "figure"),
    Output(grafico2, "style"),
    Output(messaggio_errore, "is_open"),
    State(discard, "value"),
    State(program, "value"),
    State(family, "value"),
    State(macchina, "value"),
    State(lines, "value"),
    State(layer,"value"),
    Input(bottone, "n_clicks")
)
def update_graph(discard, program, family, macchina, lines, layer, n_clicks):
    titolo=""
    messaggio_errore = False
    # create fig
    fig = go.Figure()
    fig2 = go.Figure()
    # bottone
    if n_clicks is None:
        raise PreventUpdate
    if n_clicks > 0 and program is None:
        messaggio_errore = True
    # titolo
    if program is not None:
        if discard == "True":
            if family is None:
                if macchina is None:
                    titolo = f"Program {program}, discard = True"
                else:
                    titolo = f"Program {program}, discard = True, macchina {macchina}"
            else:
                if macchina is None:
                    titolo = f"Program {program}, discard = True, family {family}"
                else:
                    titolo = f"Program {program}, discard = True, family {family}, macchina {macchina}"
        if discard == "False":
            if family is None:
                if macchina is None:
                    titolo = f"Program {program}, discard = False"
                else:
                    titolo = f"Program {program}, discard = False, macchina {macchina}"
            else:
                if macchina is None:
                    titolo = f"Program {program}, discard = False, family {family}"
                else:
                    titolo = f"Program {program}, discard = False, family {family}, macchina {macchina}"
        if discard == "Entrambi":
            if family is None:
                if macchina is None:
                    titolo = f"Program {program}"
                else:
                    titolo = f"Program {program}, macchina {macchina}"
            else:
                if macchina is None:
                    titolo = f"Program {program}, family {family}"
                else:
                    titolo = f"Program {program}, family {family}, macchina {macchina}"
    # creazione grafico
    if program is not None:
        #filter errors_plus based on parameters
        df_errors_plus = get_df_errors_plus(df_errors_plus_running_true,discard,program,family,macchina)
        # add rango to errors_plus e filtra df_artcode in base all'hash più comune del programma
        df_errors_plus, df_errors_plus_rango_zero,df_artcode_specific_hash = add_rango_to_errors_plus(df_errors_plus, df_artcode, df_artcode_references, program)
        #creo un dataset che per ogni rango conta il numero di errori in base a family code
        errors_per_rango = get_errors_per_rango_e_family_code(df_errors_plus)
        #come prima ma solo per il rango zero
        errors_rango_zero = get_errors_per_rango_e_family_code(df_errors_plus_rango_zero)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # creo il grafico degli errori
        fig_errors = px.bar(errors_per_rango, x="rango", y="count", color="family_code",opacity=1)
        fig.add_traces(fig_errors['data'][:])
        fig.update_layout(barmode='stack')
        # gestione delle linee RPM/step in base alla selezione
        if lines == "RPM" or lines == "Entrambi":
            fig.add_trace(
                go.Scatter(x=df_artcode_specific_hash["compact_course"], y=df_artcode_specific_hash["rpm"],
                           line=dict(color="red",width=1), name="RPM"),
                secondary_y=True,
            )
            if lines == "RPM":
                fig.update_yaxes(title_text="RPM", secondary_y=True, showgrid=False)
            else:
                fig.update_yaxes(title_text="RPM e step", secondary_y=True, showgrid=False)
        if lines == "step" or lines == "Entrambi":
            fig.add_trace(
                go.Scatter(x=df_artcode_specific_hash["compact_course"], y=df_artcode_specific_hash["step"],
                           line=dict(color="blue", width=1), name="Step"),
                secondary_y=True,
            )
            if lines == "step":
                fig.update_yaxes(title_text="step", secondary_y=True, showgrid=False)
            else:
                fig.update_yaxes(title_text="RPM e step", secondary_y=True, showgrid=False)

        # titoli degli assi
        fig.update_yaxes(title_text="Errori per rango", secondary_y=False, showgrid=False)
        fig.update_xaxes(title_text="Rango", showgrid=False)
        #imposta la mdalità "comapre data on hover" di default
        fig.update_layout(hovermode='x')
        #aggiunta del titolo al grafico
        fig.update_layout(
            title_text=titolo,
            title_x=0.5
        )
        #pie chart errori al rango zero
        fig2 = px.pie(errors_rango_zero, values='count', names='family_code')
        fig2.update_layout(
            title_text=f'Errori al rango zero ({errors_rango_zero["count"].sum()} errori)',
            title_x=0.5
        )
        #aggiunta delle tracce di zona/economia
        if layer == "economie":
            lista_economie = get_lista_economie(df_artcode_specific_hash)
            for e in lista_economie:
                fig.add_vrect(x0=e["min"], x1=e["max"], line_width=0, fillcolor="red", opacity=0.2,
                              annotation_text="economia", annotation_position="top left", annotation_textangle=90,
                              layer="below")
        if layer == "zone":
            lista_zone = get_lista_zone(df_artcode_specific_hash)
            for e in lista_zone:
                fig.add_vrect(x0=e["min"], x1=e["max"], line_width=0, fillcolor=e["color"], opacity=0.2,
                              annotation_text="",annotation_position="top left", annotation_textangle = 90,layer="below")
    # per fare apparire i grafici solo dopo averli creati la prima volta, prima ritorno la figure e poi gli modifico lo style display
    return fig,{"display": "block"},fig2,{"display": "block"}, messaggio_errore


if __name__ == '__main__':
    app.run_server(debug=True)
