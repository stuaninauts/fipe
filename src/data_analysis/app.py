import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import asyncio
import re
from pathlib import Path
from shiny import App, Inputs, Outputs, Session, render, reactive, ui
import shiny.experimental as x
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

path_to_db = Path(__file__).parent.parent.parent / "data" / "database.csv"
df = pd.read_csv(path_to_db, sep=';')

dict_combustivel = {'g': "Gasolina", 'a': "Álcool", 'd': "Diesel", 'e': "Elétrico"}
dict_cambio = {'m': "Manual", 'a': "Automático"}

ano_modelo_placa = 0

def show_nothing():
    return ""

def show_tam_motor():
        return [
            ui.row(
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
        ]

def show_tipo_motor():
    return [
        ui.input_checkbox_group(
            id="tipo_motor",
            label="Cilindros:",
            choices=["V12", "V10", "V8", "V6"],
            selected=["V12", "V10", "V8", "V6"],
        ),
    ]

def show_filtrar_marcas_on():
    return [
        ui.input_checkbox_group(
            id="marcas_selecionadas", 
            label="Selecionar Marcas", 
            choices=df['marca'].tolist(),
            selected=None,
        ),
    ]

def show_filtrar_marcas():
    return [
        ui.panel_well (        
            ui.input_switch("switch_marcas", "Filtrar Marcas"),
            # nav filtrar marcas on 
            ui.navset_hidden(
                ui.nav(None, show_nothing(), value='False'),
                ui.nav(None, show_filtrar_marcas_on(), value='True'),
                id="nav_filtrar_marcas_on",
            ),          
        ),
    ]

def show_filtros_avancados():
    return  [
        ui.panel_well (
            # quantidade:   slide
            ui.input_slider(
                "qntd", "Quantidade:", min=5, max=15, value=10, step=1,
            ),
            # combustivel: 	button g / a / d / e 
            ui.input_checkbox_group(
                id="combustivel", 
                label="Tipo de combustível", 
                choices=dict_combustivel,
                selected=tuple(dict_combustivel.keys()),
            ),
            # cambio: 	button m / a
            ui.input_checkbox_group(
                id="cambio", 
                label="Câmbio", 
                choices=dict_cambio,
                selected=tuple(dict_cambio.keys()),
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
    ]

def nav_ranking():
    return [
        ui.row(
            ui.column(
                12,
                ui.div({"class": "titulo"},
                    ui.h3("Ranking Geral de Valores Marcas/Modelos"),
                    ui.input_action_button("btn_titulo", "Mostrar/Enconder Título do Plot"),
                    ui.download_button("download_ranking_plot", "Download Plot"),
                )
            ),
        ),
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
                x.ui.accordion(
                    x.ui.accordion_panel(
                        "Filtros avançados",
                        show_filtros_avancados(),                    
                    ),  
                ),   
            ),
            ui.panel_main(
                ui.output_plot("plot_ranking"),
                ui.input_action_button("btn_interacoes", "Mostrar/Esconder Interacoes (em desenvolvimento)"),
                # ui.output_ui("show_interacoes"),                    
            ),
        ),
    ]

def nav_historico():
    return [
        ui.row(
            ui.column(
                12,
                ui.div({"class": "titulo"},
                    ui.h3("Histórico da Tabela Fipe de um Modelo Individual"),
                    ui.download_button("download_historico_plot", "Download Plot"),
                ),
            ),
        ),
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.navset_tab_card(
                    ui.nav("Por Veículo", nav_historico_veiculo()),
                    # section commented because have to fix port settings on the website fipe.stuaninauts.com
                    # if you uncomment will work locally!
                    ui.nav("Por Placa", nav_historico_placa()),
                ),
            ),
            ui.panel_main(
                ui.navset_hidden(
                    ui.nav(None, ui.output_plot("plot_historico_veiculo"), value='veiculo'),
                    ui.nav(None, ui.output_plot("plot_historico_placa"), value='placa'),
                    id="nav_plot_veiculo_ou_placa",
                ),
                
            ),
        ),
    ]

def nav_historico_veiculo():
    return [
        ui.input_select(
            id="modelo_ano_fab",
            label="Ano de fabricação:",
            choices=list(range(2023, min(df['ano_fab'])-1, -1)),
            selected=2023,
            multiple=False,
        ),
        ui.input_selectize(
            "modelo_index",
            "Digite/Escolha o Modelo:",
            [],
            multiple=False,
        ),
        ui.input_action_button("btn_veiculo_exibir", "Exibir Gráfico", class_="btn-success"),
    ]

def show_placa_modelos():
    return [
        ui.input_selectize(
            "modelo_placa_selecionado",
            "Selecione o modelo:",
            [],
            multiple=False,
        ),
        ui.input_action_button("btn_placa_exibir", "Exibir Gráfico", class_="btn-success"),   
    ]

def nav_historico_placa():
    return [
        ui.input_text("modelo_placa", "Digite a Placa:"),
        ui.input_action_button("btn_buscar_placa", "Buscar Placa", class_="btn-success"),   
        ui.navset_hidden(
            ui.nav(None, show_nothing(), value='0'),
            ui.nav(None, show_placa_modelos(), value='1'),
            id="nav_modelos_placa",
        ),
        ui.output_text_verbatim("placa_mensagem", ""),
    ]

app_ui = ui.page_fluid(
    ui.tags.html(
        {
            "data-bs-theme": "dark"
        },
        ui.include_css("custom.css"),
        ui.h1({"style": "text-align: center;"}, "Análise de dados tabela Fipe"),
        ui.navset_tab_card(
            ui.nav("Ranking de Valores", nav_ranking()),
            ui.nav("Histórico Modelo Individual", nav_historico()),
        )
    ),

)
def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect
    @reactive.event(input.ano_ref)
    def _():
        ui.update_slider("ano_fab", max=input.ano_ref())

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

    @reactive.Effect
    @reactive.event(input.tam_motor_min, input.tam_motor_max)
    def _():
        ui.update_numeric(
            id="tam_motor_min",
            max=input.tam_motor_max(),
        ),
        ui.update_numeric(
            id="tam_motor_max",
            min=input.tam_motor_min(),
        ),
    
    def build_ranking_title(input):
        analise = ''
        ordenacao = ''
        genero = ''
        filtros = ''
        if input.analise() == 'marca':
            analise = 'Marcas'
            genero = 'a'
        else:
            analise = 'Modelos'
            genero = 'o'

        if input.ordem() == '':
            ordenacao = f'mais barat{genero}s'
        else:
            ordenacao = f'mais car{genero}s'


        filtros = []
        if len(input.combustivel()) < 4:
            combustiveis = [dict_combustivel[comb].lower() for comb in input.combustivel()]
            combustiveis = ', '.join(combustiveis)
            filtros.append(f'com tipo de combustível: {combustiveis}')

        if len(input.cambio()) < 2:
            filtros.append(f'com câmbio {dict_cambio[input.cambio()[0]].lower()}')

        if input.choose_tam_motor() == '1':
            filtros.append(f'com tamanho do motor de {input.tam_motor_min()} a {input.tam_motor_max()}')

        if input.choose_tipo_motor() == '1':
            motores = [str(motor) for motor in input.tipo_motor()]
            motores = ', '.join(motores)
            if not input.tipo_motor():
                motores = 'qualquer'
            filtros.append(f'com motor {motores}')

        if input.switch_marcas() and input.marcas_selecionadas():
            marcas = list(input.marcas_selecionadas())
            marcas = ', '.join(marcas)
            filtros.append(f'das marcas: {marcas}')

        if filtros:
            filtros = ', \n'.join(filtros)
            filtros = '\n' + filtros
        else:
            filtros = ''

        title = f'{analise} {ordenacao} fabricad{genero}s em {input.ano_fab()}{filtros}\n (ref. {input.ano_ref()})'
        return title

    def build_ranking_plot():
        plt.style.use('dark_background')
        plt.rcParams.update({
            'axes.facecolor': '#1e1e1e',
            'axes.edgecolor': '#f4f4f4',
            'axes.labelcolor': '#f4f4f4',
            'xtick.color': '#f4f4f4',
            'ytick.color': '#f4f4f4',
            'grid.color': '#494949',
            'text.color': '#f4f4f4',
            'figure.facecolor': '#1e1e1e',
            'figure.edgecolor': '#1e1e1e',
            'savefig.facecolor': '#1e1e1e',
            'savefig.edgecolor': '#1e1e1e'
        })

        if input.switch_marcas():
            result = df[df['marca'].str.contains('|'.join(input.marcas_selecionadas()))]
        else:
            result = df

        # ano_ref
        result = result[result['ano_ref'] == int(input.ano_ref())]

        # ano_fab
        result = result[result['ano_fab'] == int(input.ano_fab())]

        # combustivel (filtro avancado)
        result = result[result['combustivel'].str.contains('|'.join(input.combustivel()))]
        
        # cambio (filtro avancado)
        result = result[result['cambio'].str.contains('|'.join(input.cambio()))]

        # tam_motor (filtro avancado)
        if input.choose_tam_motor() == '1':            
            tam_motor_max = float(input.tam_motor_max())
            tam_motor_min = float(input.tam_motor_min())
            if (tam_motor_max >= tam_motor_min):
                result = result[(result['tam_motor'] <= tam_motor_max)]
                result = result[(result['tam_motor'] >= tam_motor_min)]
                print(result['tam_motor'])
        
        # tipo_motor (filtro avancado)
        if input.choose_tipo_motor() == '1':
            result = result[result['modelo'].str.contains('|'.join(input.tipo_motor()))]

        # agrupa
        result = result.groupby(input.analise())['valor'].mean()

        # ordem
        result = result.sort_values(ascending=bool(input.ordem()))

        # qntd (filtro avancado)
        result = result.tail(int(input.qntd()))

        if input.btn_titulo() % 2 == 0:
            title = build_ranking_title(input)
        else:
            title = ''
        
        plt.title(title)        
        plt.barh(result.index, result.values, color='#e64729') 
        plt.xlabel('valor')
        plt.ylabel(input.analise())
        plt.gca().xaxis.grid(True, color='#494949') 
        
        return plt

    @output
    @render.plot
    def plot_ranking():
        plt = build_ranking_plot()

    @session.download(filename="ranking.png")
    async def download_ranking_plot():      
        await asyncio.sleep(0.25)   
        plt = build_ranking_plot()

        with io.BytesIO() as buf:
            plt.savefig(buf, format="png")
            yield buf.getvalue()
    # -------------------------------------------------------------------------------------------
    @reactive.Effect
    @reactive.event(input.btn_veiculo_exibir)
    def _():
        ui.update_navs("nav_plot_veiculo_ou_placa", selected='veiculo')
    
    @reactive.Effect
    @reactive.event(input.btn_placa_exibir)
    def _():
        ui.update_navs("nav_plot_veiculo_ou_placa", selected='placa')

    @reactive.Effect
    @reactive.event(input.modelo_ano_fab)
    def _():
        modelo_ano_fab = int(input.modelo_ano_fab())
        modelos = df[df["ano_ref"] == 2023]
        modelos = modelos[modelos["ano_fab"] == modelo_ano_fab]
        ui.update_selectize("modelo_index", choices=modelos["modelo"])

    @reactive.Effect
    @reactive.event(input.btn_buscar_placa)
    def _():
        global ano_modelo_placa
        padrao = r"[a-zA-Z]{3}\d([a-zA-Z]|\d)\d{2}"
        if re.fullmatch(padrao, input.modelo_placa()):
            url = f'https://placafipe.com/placa/{input.modelo_placa()}'
            req = Request(
                url=url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response = urlopen(req)
            status_code = response.getcode()

            if status_code == 200:
                soup = BeautifulSoup(response, 'html.parser')
                aviso_placa_nao_encontrada = soup.select_one('.template-middle > div:nth-child(1) > p:nth-child(2)')
                if aviso_placa_nao_encontrada == None:
                    modelos_por_placa = []
                    tabela = soup.select_one('.fipe-desktop')
                    for linha in tabela.find_all('tr')[1:]:
                        modelos_por_placa.append(linha.find_all('td')[1].text)
                    ano_modelo_placa = int(soup.select_one('.fipeTablePriceDetail').find_all('tr')[5].find_all('td')[1].text)
                    ui.update_navs("nav_modelos_placa", selected='1')
                    ui.update_selectize("modelo_placa_selecionado", choices=modelos_por_placa)
                else:
                    m = ui.modal(
                        aviso_placa_nao_encontrada.text,
                        title="Placa Incorreta",
                        easy_close=True,
                        footer=None,
                    )
                    ui.modal_show(m)
                    ui.update_navs("nav_modelos_placa", selected='0')
            else:
                m = ui.modal(
                    "Recarregue e tente novamente! Se o erro persistir contate o desenvolvedor",
                    title="Erro ao abrir o site",
                    easy_close=True,
                    footer=None,
                )
                ui.modal_show(m)
        else:
            m = ui.modal(
                "Digite a placa no formato ABC1234 ou ABC1D23",
                title="Padrão incorreto da placa",
                easy_close=True,
                footer=None,
            )
            ui.modal_show(m)
            ui.update_navs("nav_modelos_placa", selected='0')
       

    def build_historico_plot(por_modalidade):
        plt.style.use('dark_background')
        plt.rcParams.update({
            'axes.facecolor': '#1e1e1e',
            'axes.edgecolor': '#f4f4f4',
            'axes.labelcolor': '#f4f4f4',
            'xtick.color': '#f4f4f4',
            'ytick.color': '#f4f4f4',
            'grid.color': '#494949',
            'text.color': '#f4f4f4',
            'figure.facecolor': '#1e1e1e',
            'figure.edgecolor': '#1e1e1e',
            'savefig.facecolor': '#1e1e1e',
            'savefig.edgecolor': '#1e1e1e'
        })

        global ano_modelo_placa
        if por_modalidade == 'veiculo':
            modelo_nome = df.iloc[int(input.modelo_index())]["modelo"]
            ano_fab = int(input.modelo_ano_fab())
        else: # por_modalidade == 'placa'
            modelo_nome = input.modelo_placa_selecionado()
            ano_fab = ano_modelo_placa
        
        result = df[df["modelo"] == modelo_nome]
        result = result[result["ano_fab"] == ano_fab]
        plt.title(modelo_nome)
        plt.barh(result["ano_ref"], result["valor"], color='#e64729')
        plt.xlabel('valor')
        plt.ylabel('ano ref.')

    
        plt.yticks(range(int(min(result["ano_ref"])), int(max(result["ano_ref"]))+1))
        plt.gca().xaxis.grid(True, color='#494949')


        return plt

    @output
    @render.plot
    @reactive.event(input.btn_placa_exibir, ignore_none=True)
    def plot_historico_placa():
        plt = build_historico_plot('placa')

    @output
    @render.plot
    @reactive.event(input.btn_veiculo_exibir, ignore_none=True)
    def plot_historico_veiculo():
        plt = build_historico_plot('veiculo')
    
    @session.download(filename="historico.png")
    async def download_historico_plot():      
        await asyncio.sleep(0.25)   
        plt = build_historico_plot()

        with io.BytesIO() as buf:
            plt.savefig(buf, format="png")
            yield buf.getvalue()

app = App(app_ui, server)
