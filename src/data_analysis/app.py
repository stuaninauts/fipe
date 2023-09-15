import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from shiny import App, Inputs, Outputs, Session, render, reactive, ui

path_to_db = Path(__file__).parent.parent.parent / "data" / "database.csv"
df = pd.read_csv(path_to_db, sep=';')


def show_nothing():
    return ""



def show_tam_motor():
        return ui.row(
                    ui.column(
                        6,
                        ui.input_numeric(
                            id="tam_motor_min", 
                            label="Min (L):",
                            min=min(df['tam_motor']),
                            max=max(df['tam_motor']),
                            value=min(df['tam_motor']),
                            step=0.1,
                        ),
                    ),
                    ui.column(
                        6,
                        ui.input_numeric(
                            id="tam_motor_max", 
                            label="Max (L):",
                            min=min(df['tam_motor']),
                            max=max(df['tam_motor']),
                            value=max(df['tam_motor']),
                            step=0.1,
                        ),
                    ),
                ),

def show_tipo_motor():
    return ui.input_checkbox_group(
                    id="tipo_motor",
                    label="Cilindros:",
                    choices=["V12", "V10", "V8", "V6"],
                    selected=["V12", "V10", "V8", "V6"],
            ),

def show_filtrar_marcas_on():
    return ui.input_checkbox_group(
                        id="marcas_selecionadas", 
                        label="Selecionar Marcas", 
                        choices=df['marca'].tolist(),
                        selected=None,
            ),

def show_filtrar_marcas():
    return ui.panel_well (        
                ui.input_switch("switch_marcas", "Filtrar Marcas"),
                # nav filtrar marcas on 
                ui.navset_hidden(
                    ui.nav(None, show_nothing(), value='False'),
                    ui.nav(None, show_filtrar_marcas_on(), value='True'),
                    id="nav_filtrar_marcas_on",
                ),          
            ),



def show_filtros_avancados():
    return  ui.panel_well (
                # quantidade:   slide
                ui.input_slider(
                    "qntd", "Quantidade:", min=5, max=15, value=10, step=1,
                ),
                # combustivel: 	button g / a / d / e 
                ui.input_checkbox_group(
                    id="combustivel", 
                    label="Tipo de combustível", 
                    choices={'g': "Gasolina", 'a': "Álcool", 'd': "Diesel", 'e': "Elétrico"},
                    selected=('g', 'a', 'd', 'e'),
                ),
                # cambio: 	button m / a
                ui.input_checkbox_group(
                    id="cambio", 
                    label="Câmbio", 
                    choices={'m': "Manual", 'a': "Automático"},
                    selected=('m', 'a'),
                ),
                # tam motor: min max
                ui.input_radio_buttons(
                    id="choose_tam_motor", 
                    label="Tamanho do motor:", 
                    choices={'0': "Todos", '1': "Definir intervalo"}, 
                    selected='0',
                ),
                # nav tam motor
                ui.navset_hidden(
                    ui.nav(None, show_nothing(), value='0'),
                    ui.nav(None, show_tam_motor(), value='1'),
                    id="nav_tam_motor",
                ),
                # tipo motor: button v12 v10 v8 v6 outros
                ui.input_radio_buttons(
                    id="choose_tipo_motor", 
                    label="Tipo do motor:", 
                    choices={'0': "Todos", '1': "Escolher específico(s)"},
                    selected='0',
                ),
                # nav tipo motor
                ui.navset_hidden(
                    ui.nav(None, show_nothing(), value='0'),
                    ui.nav(None, show_tipo_motor(), value='1'),
                    id="nav_tipo_motor",
                ),      

                # nav filtrar marcas
                ui.navset_hidden(
                    ui.nav(None, show_nothing(), value='marca'),
                    ui.nav(None, show_filtrar_marcas(), value='modelo'),
                    id="nav_filtrar_marcas",
                ),      
            )           


app_ui = ui.page_fluid(
    ui.h1({"style": "text-align: center;"},"Análise de dados tabela Fipe"),
    ui.h3("Ranking Geral de Valores Marcas/Modelos"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            # anoref: 	slide 2004 --- 2023
            ui.input_select(
                id="ano_ref",
                label="Ano de referência:",
                choices=sorted(df['ano_ref'].unique().tolist()),
                selected=2023,
            ),
            # anofab: 	slide 19xx --- 2023
            ui.input_slider(
                id="ano_fab",
                label="Ano de fabricação:",
                min=min(df['ano_fab']),
                max=2023,
                value=2023,
                sep='',
                animate=True,
            ),
            # tipo: button marca ou modelo
            ui.input_radio_buttons(
                id="analise", 
                label="Análise:", 
                choices={"marca": "Marcas", "modelo": "Modelos"},
                selected="marca",
            ),            
            # ordem: button ascendente / descendente
            ui.input_radio_buttons(
                id="ordem", 
                label="Ordenação dos valores:", 
                choices={'': "Mais Baratas(os)", '1': "Mais caras(os)"}, # '' to bool(str) => False
                selected='',
            ),
            # nav filtros avançados
            ui.input_action_button("btn_filtros", "Mostrar/Esconder Filtros Avançados"),
            ui.navset_hidden(
                ui.nav(None, show_nothing(), value='0'),
                ui.nav(None, show_filtros_avancados(), value='1'),
                id="nav_filtros_avancados",
            ),


            ),
        ui.panel_main(
            ui.output_plot("plot"),
            ui.input_action_button("btn_interacoes", "Mostrar/Esconder Interacoes"),
            # ui.output_ui("show_interacoes"),                    
        ),
    ),
)




def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.btn_filtros)
    def _():
        ui.update_navs("nav_filtros_avancados", selected=str(input.btn_filtros()%2))

    @reactive.Effect
    @reactive.event(input.choose_tam_motor)
    def _():
        ui.update_navs("nav_tam_motor", selected=input.choose_tam_motor())
    
    @reactive.Effect
    @reactive.event(input.choose_tipo_motor)
    def _():
        ui.update_navs("nav_tipo_motor", selected=input.choose_tipo_motor())

    @reactive.Effect
    @reactive.event(input.analise)
    def _():
        ui.update_navs("nav_filtrar_marcas", selected=input.analise())
    
    @reactive.Effect
    @reactive.event(input.switch_marcas)
    def _():
        ui.update_navs("nav_filtrar_marcas_on", selected=str(input.switch_marcas()))

    @output
    @render.plot
    def plot():
        if input.switch_marcas():
            result = df[df['marca'].str.contains('|'.join(input.marcas_selecionadas()))]
        else:
            result = df
        # combustivel (filtro avancado)
        result = result[result['combustivel'].str.contains('|'.join(input.combustivel()))]
        # cambio (filtro avancado)
        result = result[result['cambio'].str.contains('|'.join(input.cambio()))]

        # tam_motor (filtro avancado)
        if input.choose_tam_motor() == '1':
            tam_motor_max = float(input.tam_motor_max())
            tam_motor_min = float(input.tam_motor_min())
            if (tam_motor_max >= tam_motor_min):
                filtro = ((result['tam_motor'] >= tam_motor_min) & (result['tam_motor'] <= tam_motor_max))
                result = result[filtro]
        # tipo_motor (filtro avancado)
        if bool(input.choose_tipo_motor()):
            result = result[result['modelo'].str.contains('|'.join(input.tipo_motor()))]

        # ano_ref
        result = result[result['ano_ref'] == int(input.ano_ref())]
        # ano_fab
        result = result[result['ano_fab'] == int(input.ano_fab())]
        
        
        # agrupa
        result = result.groupby(input.analise())['valor'].mean()

        # ordem
        result = result.sort_values(ascending=bool(input.ordem()))

        # qntd (filtro avancado)
        result = result.tail(int(input.qntd()))

        plt.barh(result.index, result.values, color='royalblue')
        plt.xlabel('Valor')
        plt.ylabel(input.analise())
        plt.gca().xaxis.grid(True)


app = App(app_ui, server)
