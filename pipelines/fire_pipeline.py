"""
Pipeline de transformação dos focos de queimada.

Recebe o DataFrame bruto do provider e aplica:
  - filtros interativos (data, estado, risco mínimo)
  - classificação de risco a partir do FRP
  - agregações para os gráficos
  - cálculo de KPIs
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st


NIVEIS_RISCO = ["Baixo", "Moderado", "Alto", "Crítico"]


def classificar_risco(frp_mw: float) -> str:
    """Converte FRP em uma categoria de risco."""
    if frp_mw < 10:
        return "Baixo"
    if frp_mw < 50:
        return "Moderado"
    if frp_mw < 150:
        return "Alto"
    return "Crítico"


def calcular_score(frp_mw: float) -> int:
    """
    Score contínuo 0–100 derivado do FRP.

    Cada faixa de risco ocupa 25 pontos do slider, e dentro da faixa o
    score varia proporcionalmente ao FRP — isso faz o slider responder
    de forma fluida em todo o intervalo, em vez de saltar entre 4 valores.

        Baixo:    0 – 24    (FRP 0 – 10 MW)
        Moderado: 25 – 49   (FRP 10 – 50 MW)
        Alto:     50 – 74   (FRP 50 – 150 MW)
        Crítico:  75 – 100  (FRP 150+ MW)
    """
    if frp_mw < 10:
        score = (frp_mw / 10) * 25
    elif frp_mw < 50:
        score = 25 + ((frp_mw - 10) / 40) * 25
    elif frp_mw < 150:
        score = 50 + ((frp_mw - 50) / 100) * 25
    else:
        score = 75 + min(25, ((frp_mw - 150) / 350) * 25)
    return int(round(max(0, min(100, score))))


@st.cache_data(show_spinner=False)
def enriquecer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas derivadas ao DataFrame bruto.
    Cacheado: o enriquecimento só roda uma vez.
    """
    df = df.copy()
    df["risco"] = df["frp_mw"].apply(classificar_risco)
    df["risco_score"] = df["frp_mw"].apply(calcular_score)
    return df


@st.cache_data(show_spinner=False)
def filtrar(
    df: pd.DataFrame,
    data_inicio: date,
    data_fim: date,
    estados: tuple[str, ...],
    risco_min_score: int,
) -> pd.DataFrame:
    """
    Aplica os três filtros interativos do dashboard.

    estados é uma tupla (não lista) porque o cache_data precisa de tipos hasheáveis.
    """
    mask = (
        (df["data"].dt.date >= data_inicio)
        & (df["data"].dt.date <= data_fim)
        & (df["risco_score"] >= risco_min_score)
    )
    if estados:
        mask &= df["estado"].isin(estados)
    return df.loc[mask].reset_index(drop=True)


@dataclass
class KPIs:
    total_focos: int
    focos_criticos: int
    estados_afetados: int
    frp_medio: float


def calcular_kpis(df: pd.DataFrame) -> KPIs:
    if df.empty:
        return KPIs(0, 0, 0, 0.0)
    return KPIs(
        total_focos=len(df),
        focos_criticos=int((df["risco"] == "Crítico").sum()),
        estados_afetados=df["estado"].nunique(),
        frp_medio=float(df["frp_mw"].mean()),
    )


def serie_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa focos por dia para o gráfico de linha."""
    if df.empty:
        return pd.DataFrame(columns=["data", "focos"])
    return (
        df.groupby(df["data"].dt.date)
        .size()
        .reset_index(name="focos")
        .rename(columns={"data": "data"})
    )


def ranking_estados(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Top-N estados com mais focos no período filtrado."""
    if df.empty:
        return pd.DataFrame(columns=["estado", "focos"])
    return (
        df.groupby("estado")
        .size()
        .reset_index(name="focos")
        .sort_values("focos", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def focos_criticos_para_alerta(df: pd.DataFrame, limite: int = 10) -> pd.DataFrame:
    """
    Seleciona os focos críticos que vão entrar na fila de aprovação humana.
    Ordena por FRP decrescente para priorizar os mais intensos.
    """
    if df.empty:
        return df
    criticos = df[df["risco"] == "Crítico"].sort_values("frp_mw", ascending=False)
    return criticos.head(limite).reset_index(drop=True)


if __name__ == "__main__":
    from providers.fire_data_provider import carregar_focos_queimada

    df = enriquecer(carregar_focos_queimada())
    print("== KPIs (todos os dados) ==")
    print(calcular_kpis(df))
    print("\n== Série temporal (5 primeiros dias) ==")
    print(serie_temporal(df).head())
    print("\n== Ranking de estados ==")
    print(ranking_estados(df))
    print("\n== Focos críticos para alerta ==")
    print(focos_criticos_para_alerta(df).head())
