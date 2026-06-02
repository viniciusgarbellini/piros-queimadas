"""
PIROS — Plataforma Inteligente de Resposta a Ocorrências de queimadaS

Ponto de entrada do dashboard Streamlit.
Responsabilidades:
  - configurar a página
  - inicializar o tema (Design System PIROS) e o estado da sessão
  - renderizar a sidebar com os 3 filtros interativos
  - rotear as 3 features em abas
"""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from features import alertas, mapa, panorama
from pipelines.fire_pipeline import enriquecer, filtrar
from providers.fire_data_provider import (
    ESTADOS_BBOX,
    carregar_focos_queimada,
)
from state.session import init_state
from ui.theme import aplicar_tema, cabecalho


st.set_page_config(
    page_title="PIROS — Monitoramento de Queimadas",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)


aplicar_tema()
init_state()
cabecalho()


PERIODOS = {
    "Últimos 7 dias": 7,
    "Últimos 15 dias": 15,
    "Últimos 30 dias": 30,
    "Últimos 60 dias": 60,
    "Últimos 90 dias": 90,
}


def sidebar_filtros() -> tuple[date, date, tuple[str, ...], int]:
    """Renderiza os 3 filtros obrigatórios e devolve seus valores."""
    with st.sidebar:
        st.markdown("### Filtros")
        st.caption("Ajuste os filtros para refinar a análise. Tudo se atualiza automaticamente.")

        periodo_label = st.selectbox(
            "Período",
            options=list(PERIODOS.keys()),
            key="filtro_periodo",
        )
        dias = PERIODOS[periodo_label]
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias)

        estados_disponiveis = sorted(ESTADOS_BBOX.keys())
        estados = st.multiselect(
            "Estados (UF)",
            options=estados_disponiveis,
            default=st.session_state["filtro_estados"],
            key="filtro_estados",
            help="Vazio = todos os estados",
        )

        risco_min = st.slider(
            "Risco mínimo (score)",
            min_value=0,
            max_value=100,
            value=st.session_state["filtro_risco_min"],
            step=5,
            key="filtro_risco_min",
            help="0 = mostra tudo · 25 = a partir de Moderado · 50 = a partir de Alto · 75 = só Crítico",
        )

        st.markdown("---")
        st.caption(
            "**Origem dos dados:** simulação inspirada no BDQueimadas/INPE. "
            "Dataset gerado uma única vez e mantido em cache."
        )

        return data_inicio, data_fim, tuple(estados), risco_min


data_inicio, data_fim, estados, risco_min = sidebar_filtros()

with st.spinner("Carregando focos detectados pelo satélite..."):
    df_bruto = carregar_focos_queimada()
    df_enriquecido = enriquecer(df_bruto)

df_filtrado = filtrar(df_enriquecido, data_inicio, data_fim, estados, risco_min)


tab_panorama, tab_mapa, tab_alertas = st.tabs([
    "🗺️  Panorama",
    "📍  Mapa",
    "🚨  Alertas",
])

with tab_panorama:
    panorama.render(df_filtrado)

with tab_mapa:
    mapa.render(df_filtrado)

with tab_alertas:
    alertas.render(df_filtrado)
