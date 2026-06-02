"""
Feature 1 — Panorama Geral.

Visão de abertura: KPIs + linha temporal + ranking de estados +
distribuição de risco. É o "panorama" da narrativa de storytelling.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from pipelines.fire_pipeline import (
    calcular_kpis,
    ranking_estados,
    serie_temporal,
)
from ui.charts import (
    grafico_distribuicao_risco,
    grafico_linha_temporal,
    grafico_ranking_estados,
)
from ui.metric_card import metric_card


def _variante_critico(focos_criticos: int, total: int) -> str:
    if total == 0:
        return "neutro"
    proporcao = focos_criticos / total
    if proporcao >= 0.20:
        return "critico"
    if proporcao >= 0.10:
        return "alto"
    if proporcao >= 0.05:
        return "medio"
    return "ok"


def render(df: pd.DataFrame) -> None:
    st.subheader("Panorama operacional")
    st.caption(
        "Visão consolidada dos focos detectados pelo PIROS no período e filtros selecionados."
    )

    kpis = calcular_kpis(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card(
            "Focos detectados",
            f"{kpis.total_focos:,}".replace(",", "."),
            "no período filtrado",
            variante="neutro",
        )
    with col2:
        metric_card(
            "Focos críticos",
            f"{kpis.focos_criticos:,}".replace(",", "."),
            "exigem avaliação humana",
            variante=_variante_critico(kpis.focos_criticos, kpis.total_focos),
        )
    with col3:
        metric_card(
            "Estados afetados",
            kpis.estados_afetados,
            "com pelo menos um foco",
            variante="medio" if kpis.estados_afetados >= 8 else "ok",
        )
    with col4:
        metric_card(
            "FRP médio",
            f"{kpis.frp_medio:.1f} MW",
            "intensidade média do fogo",
            variante="alto" if kpis.frp_medio >= 50 else "ok",
        )

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.plotly_chart(
            grafico_linha_temporal(serie_temporal(df)),
            use_container_width=True,
            key="panorama-linha-temporal",
        )
    with col_b:
        st.plotly_chart(
            grafico_distribuicao_risco(df),
            use_container_width=True,
            key="panorama-distribuicao-risco",
        )

    st.plotly_chart(
        grafico_ranking_estados(ranking_estados(df, top_n=10)),
        use_container_width=True,
        key="panorama-ranking-estados",
    )
