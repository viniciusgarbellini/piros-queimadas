"""
Feature 2 — Mapa interativo.

Localiza geograficamente cada foco. Cor = risco. Tamanho = FRP.
Atende ao requisito de gráfico Plotly com hover e zoom.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.charts import grafico_mapa_focos


def render(df: pd.DataFrame) -> None:
    st.subheader("Mapa de focos ativos")
    st.caption(
        "Cada ponto é um foco detectado. A cor indica o nível de risco "
        "e o tamanho representa a potência do fogo (FRP em MW). "
        "Use o scroll para dar zoom e o cursor para inspecionar."
    )

    if df.empty:
        st.warning("Nenhum foco encontrado com os filtros atuais. Ajuste a sidebar.")
        return

    st.plotly_chart(
        grafico_mapa_focos(df),
        use_container_width=True,
        key="mapa-focos-brasil",
    )

    with st.expander("Ver detalhamento tabular dos focos exibidos"):
        st.dataframe(
            df[["data", "estado", "bioma", "risco", "frp_mw", "confianca"]]
            .rename(columns={
                "data": "Data",
                "estado": "UF",
                "bioma": "Bioma",
                "risco": "Risco",
                "frp_mw": "FRP (MW)",
                "confianca": "Confiança (%)",
            }),
            use_container_width=True,
            hide_index=True,
        )
