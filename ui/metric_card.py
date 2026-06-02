"""
Componente reutilizável: cartão de KPI.

Será chamado em mais de um lugar (Panorama e Alertas), com parâmetros
diferentes — atende ao requisito 3.3 do enunciado ("componentização real").
"""
from __future__ import annotations

import streamlit as st


VARIANTES = {"ok", "medio", "alto", "critico", "neutro"}


def metric_card(
    rotulo: str,
    valor: str | int | float,
    rodape: str = "",
    variante: str = "neutro",
) -> None:
    """
    Renderiza um cartão de KPI no estilo do Design System PIROS.

    variante define a cor da borda esquerda (semântica):
      ok       → verde   (situação controlada)
      medio    → amarelo (atenção)
      alto     → laranja (alerta)
      critico  → vermelho (ação imediata)
      neutro   → sem borda colorida
    """
    if variante not in VARIANTES:
        variante = "neutro"

    classe = f"piros-metric {variante}" if variante != "neutro" else "piros-metric"

    rodape_html = f'<div class="rodape">{rodape}</div>' if rodape else ""

    st.markdown(
        f"""
        <div class="{classe}">
            <div class="rotulo">{rotulo}</div>
            <div class="valor">{valor}</div>
            {rodape_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
