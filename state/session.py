"""
Gerenciamento centralizado de st.session_state.

Toda a memória da sessão do usuário passa por aqui:
  - filtros ativos
  - decisões do feedback humano (alertas aprovados / rejeitados)
"""
from __future__ import annotations

import streamlit as st


DEFAULTS = {
    "filtro_periodo": "Últimos 30 dias",
    "filtro_estados": [],
    "filtro_risco_min": 0,
    "alertas_aprovados": [],
    "alertas_rejeitados": [],
    "alertas_pendentes_ids": None,
}


def init_state() -> None:
    """
    Garante que todas as chaves esperadas existem em st.session_state.
    Chamado uma vez no app.py, antes de qualquer feature.
    """
    for chave, valor in DEFAULTS.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def aprovar_alerta(alerta_id: str) -> None:
    if alerta_id not in st.session_state["alertas_aprovados"]:
        st.session_state["alertas_aprovados"].append(alerta_id)
    if alerta_id in st.session_state["alertas_rejeitados"]:
        st.session_state["alertas_rejeitados"].remove(alerta_id)


def rejeitar_alerta(alerta_id: str) -> None:
    if alerta_id not in st.session_state["alertas_rejeitados"]:
        st.session_state["alertas_rejeitados"].append(alerta_id)
    if alerta_id in st.session_state["alertas_aprovados"]:
        st.session_state["alertas_aprovados"].remove(alerta_id)


def status_alerta(alerta_id: str) -> str:
    if alerta_id in st.session_state["alertas_aprovados"]:
        return "aprovado"
    if alerta_id in st.session_state["alertas_rejeitados"]:
        return "rejeitado"
    return "pendente"
