import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from shiny import App, reactive, render, ui
# from plotnine import ggplot, aes, geom_bar, coord_flip, theme_minimal


df = pd.read_csv(Path(__file__).parent / "../database.csv")
# ui interface
app_ui = ui.page_fluid(    
    ui.h1({"style": "text-align: center;"},"Análise de dados tabela Fipe"),
    ui.row(
        ui.h3("Ranking Geral de Valores Marcas/Modelos"),
        ui.layout_sidebar(
            # filters
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
                    choices={'1': "Mais Baratas(os)", '': "Mais caras(os)"}, # '' to bool(str) => False
                    selected='1',
                ),

                # filtros avançados
                ui.input_action_button("btn_filtros", "Mostrar/Esconder Filtros Avançados"),
                ui.output_ui("show_filtros_avancados"),
        
            ),
            # plot
            ui.panel_main(
                ui.output_plot("plot"),
                ui.input_action_button("btn_interacoes", "Mostrar/Esconder Interacoes"),
                # ui.output_ui("show_interacoes"),
                         
            ),
        ),
    ),
)


# server and logics
def server(input, output, session):
    @reactive.Effect
    def _():
        ui.update_slider("ano_fab", max=int(input.ano_ref()))

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
        if (bool(input.choose_tam_motor())):
            tam_motor_max = float(input.tam_motor_max())
            tam_motor_min = float(input.tam_motor_min())
            if (tam_motor_max >= tam_motor_min):
                filtro = ((result['tam_motor'] >= tam_motor_min) & (result['tam_motor'] <= tam_motor_max))
                result = result[filtro]
        # tipo_motor (filtro avancado)
        if (bool(input.choose_tipo_motor())):
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
        result = result.head(int(input.qntd()))


        plt.barh(result.index, result.values, color='royalblue')
        plt.xlabel('Valor')
        plt.ylabel(input.analise())
        plt.gca().xaxis.grid(True)

    @output
    @render.ui
    def show_filtros_avancados():
        if input.btn_filtros() % 2 == 1:
            return ui.panel_well (
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
                        choices={'': "Todos", '1': "Definir intervalo"}, # '' to bool(str) => False
                        selected='',
                    ),
                    ui.output_ui("show_tam_motor"),

                    # tipo motor: button v12 v10 v8 v6 outros
                    ui.input_radio_buttons(
                        id="choose_tipo_motor", 
                        label="Tipo do motor:", 
                        choices={'': "Todos", '1': "Escolher específico(s)"}, # '' to bool(str) => False
                        selected='',
                    ),
                    ui.output_ui("show_tipo_motor"),       
                    ui.output_ui("show_filtrar_marcas"),
    )           

    @output
    @render.ui
    def show_tam_motor():
        if input.choose_tam_motor():
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

    @output
    @render.ui
    def show_tipo_motor():
        if input.choose_tipo_motor():
            return ui.input_checkbox_group(
                            id="tipo_motor",
                            label="Cilindros:",
                            choices=["V12", "V10", "V8", "V6"],
                            selected=["V12", "V10", "V8", "V6"],
    ),

    @output
    @render.ui
    def show_filtrar_marcas():
        if input.analise() == 'modelo':

            return ui.panel_well (        
                ui.input_switch("switch_marcas", "Filtrar Marcas"),          
                ui.output_ui("show_marcas_selecionadas"),
    ),


    @output
    @render.ui
    def show_marcas_selecionadas():
        if input.switch_marcas():
            return  ui.input_checkbox_group(
                        id="marcas_selecionadas", 
                        label="Selecionar Marcas", 
                        choices=df['marca'].tolist(),
                        selected=None,

    ),

        
    # @output
    # @render.ui
    # def show_interacoes():
    #     return

app = App(app_ui, server)

