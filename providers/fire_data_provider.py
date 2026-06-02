"""
Provider de dados de focos de queimada.

Simula a resposta de uma API de satélite (ex.: INPE/BDQueimadas).
Os dados são mockados, mas com distribuição geográfica e estatística
coerente com o padrão real observado no Brasil.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st


ESTADOS_BBOX = {
    "AC": {"lat": (-11.0, -7.1), "lon": (-73.9, -66.6), "peso": 6},
    "AM": {"lat": (-9.8, 2.2), "lon": (-73.8, -56.1), "peso": 18},
    "AP": {"lat": (-1.0, 4.4), "lon": (-54.9, -50.0), "peso": 3},
    "BA": {"lat": (-18.3, -8.5), "lon": (-46.6, -37.3), "peso": 7},
    "GO": {"lat": (-19.5, -12.4), "lon": (-53.3, -45.9), "peso": 6},
    "MA": {"lat": (-10.3, -1.0), "lon": (-48.8, -41.8), "peso": 8},
    "MT": {"lat": (-18.0, -7.4), "lon": (-61.6, -50.2), "peso": 16},
    "MS": {"lat": (-24.1, -17.2), "lon": (-58.2, -50.9), "peso": 5},
    "PA": {"lat": (-9.8, 2.6), "lon": (-58.9, -46.0), "peso": 17},
    "RO": {"lat": (-13.7, -7.9), "lon": (-66.8, -59.8), "peso": 7},
    "RR": {"lat": (-1.6, 5.3), "lon": (-64.8, -58.9), "peso": 3},
    "TO": {"lat": (-13.5, -5.2), "lon": (-50.7, -45.7), "peso": 4},
}

BIOMAS = ["Amazônia", "Cerrado", "Pantanal", "Caatinga", "Mata Atlântica"]


@st.cache_data(show_spinner=False)
def carregar_focos_queimada(n_focos: int = 700, semente: int = 42) -> pd.DataFrame:
    """
    Gera o dataset de focos de queimada.

    Cacheado: a função só roda na primeira vez. Nos reruns seguintes,
    o Streamlit reusa o DataFrame em memória — sem isso, cada interação
    do usuário regeraria 500 linhas.
    """
    rng = np.random.default_rng(semente)

    estados = list(ESTADOS_BBOX.keys())
    pesos = np.array([ESTADOS_BBOX[s]["peso"] for s in estados], dtype=float)
    pesos /= pesos.sum()

    estados_sorteados = rng.choice(estados, size=n_focos, p=pesos)

    lats = np.zeros(n_focos)
    lons = np.zeros(n_focos)
    for i, uf in enumerate(estados_sorteados):
        bbox = ESTADOS_BBOX[uf]
        lats[i] = rng.uniform(bbox["lat"][0], bbox["lat"][1])
        lons[i] = rng.uniform(bbox["lon"][0], bbox["lon"][1])

    hoje = datetime.now().date()
    dias_atras = rng.integers(0, 90, size=n_focos)
    datas = [hoje - timedelta(days=int(d)) for d in dias_atras]

    # FRP (Fire Radiative Power, MW) — distribuição log-normal aproxima o real,
    # ajustada para gerar uma quantidade significativa de focos Altos e Críticos
    # (necessário para demonstrar o filtro e a aba de alertas).
    frp = rng.lognormal(mean=3.2, sigma=1.4, size=n_focos)
    frp = np.clip(frp, 1, 600)

    # Confiabilidade da detecção
    confianca = rng.uniform(50, 100, size=n_focos)

    biomas = rng.choice(BIOMAS, size=n_focos, p=[0.40, 0.30, 0.10, 0.10, 0.10])

    df = pd.DataFrame({
        "data": pd.to_datetime(datas),
        "estado": estados_sorteados,
        "latitude": lats.round(4),
        "longitude": lons.round(4),
        "frp_mw": frp.round(2),
        "confianca": confianca.round(1),
        "bioma": biomas,
    })

    df = df.sort_values("data").reset_index(drop=True)
    return df


if __name__ == "__main__":
    # Permite rodar o provider isolado (útil para conferir os dados sem subir a interface)
    df = carregar_focos_queimada()
    print(f"Total de focos gerados: {len(df)}")
    print(f"Período: {df['data'].min().date()} → {df['data'].max().date()}")
    print(f"Estados: {df['estado'].nunique()}")
    print(df.head(10))
