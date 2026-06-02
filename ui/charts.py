"""
Funções de gráficos Plotly com o tema PIROS aplicado.

Centraliza as visualizações para que cor, fonte e layout fiquem coerentes
em todo o dashboard.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ui.theme import (
    COR_FUNDO,
    COR_PRIMARIA,
    COR_SUPERFICIE,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    CORES_RISCO,
    ORDEM_RISCO,
)


_LAYOUT_BASE = dict(
    paper_bgcolor=COR_FUNDO,
    plot_bgcolor=COR_SUPERFICIE,
    font=dict(family="Inter, sans-serif", color=COR_TEXTO, size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(bgcolor=COR_SUPERFICIE, font_family="Inter", font_color=COR_TEXTO),
)


def grafico_mapa_focos(df: pd.DataFrame) -> go.Figure:
    """
    Mapa interativo dos focos de queimada (Plotly).
    Cor = nível de risco. Tamanho = FRP.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Sem focos no filtro atual",
            **_LAYOUT_BASE,
        )
        return fig

    fig = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        color="risco",
        size="frp_mw",
        size_max=22,
        zoom=3,
        center={"lat": -14.5, "lon": -55.0},
        color_discrete_map=CORES_RISCO,
        category_orders={"risco": ORDEM_RISCO},
        hover_data={
            "estado": True,
            "bioma": True,
            "frp_mw": ":.1f",
            "confianca": ":.0f",
            "data": "|%d/%m/%Y",
            "latitude": False,
            "longitude": False,
        },
        map_style="carto-darkmatter",
        height=560,
    )
    fig.update_layout(
        **_LAYOUT_BASE,
        legend=dict(title="Risco", orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def grafico_linha_temporal(serie: pd.DataFrame) -> go.Figure:
    """Evolução de focos no tempo. Plotly interativo (hover + zoom)."""
    if serie.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados no período", **_LAYOUT_BASE)
        return fig

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=serie["data"],
            y=serie["focos"],
            mode="lines+markers",
            line=dict(color=COR_PRIMARIA, width=2.5),
            marker=dict(size=6, color=COR_PRIMARIA),
            fill="tozeroy",
            fillcolor="rgba(255, 107, 53, 0.12)",
            hovertemplate="<b>%{x|%d/%m/%Y}</b><br>%{y} focos<extra></extra>",
            name="Focos por dia",
        )
    )
    fig.update_layout(
        title="Evolução diária de focos",
        height=380,
        xaxis=dict(
            gridcolor="#1F2A36",
            title="",
            tickformat="%d/%m",
            tickangle=-30,
            nticks=12,
        ),
        yaxis=dict(gridcolor="#1F2A36", title="Focos detectados"),
        **_LAYOUT_BASE,
    )
    return fig


def grafico_ranking_estados(ranking: pd.DataFrame) -> go.Figure:
    """Top estados por nº de focos. Barra horizontal."""
    if ranking.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados", **_LAYOUT_BASE)
        return fig

    ranking = ranking.iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=ranking["focos"],
            y=ranking["estado"],
            orientation="h",
            marker=dict(color=COR_PRIMARIA),
            hovertemplate="<b>%{y}</b><br>%{x} focos<extra></extra>",
        )
    )
    fig.update_layout(
        title="Top estados por focos",
        height=380,
        xaxis=dict(gridcolor="#1F2A36", title="Focos"),
        yaxis=dict(title=""),
        **_LAYOUT_BASE,
    )
    return fig


def grafico_distribuicao_risco(df: pd.DataFrame) -> go.Figure:
    """Donut com a distribuição de risco — segunda visualização Plotly."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados", **_LAYOUT_BASE)
        return fig

    contagem = df["risco"].value_counts().reindex(ORDEM_RISCO, fill_value=0)
    fig = go.Figure(
        go.Pie(
            labels=contagem.index,
            values=contagem.values,
            hole=0.6,
            marker=dict(colors=[CORES_RISCO[r] for r in contagem.index]),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value} focos (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(
        title="Distribuição por nível de risco",
        height=380,
        showlegend=False,
        **_LAYOUT_BASE,
    )
    return fig
