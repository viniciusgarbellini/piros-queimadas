"""
Feature 3 — Central de Alertas (Feedback Humano / Human-in-the-loop).

Atende ao requisito 3.4: o sistema sugere alertas críticos a partir da
análise dos dados, e o usuário aprova/rejeita o envio ao campo.
"""
from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from pipelines.fire_pipeline import focos_criticos_para_alerta
from state.session import aprovar_alerta, rejeitar_alerta, status_alerta
from ui.metric_card import metric_card


def _alerta_id(linha: pd.Series) -> str:
    """ID estável por foco — não muda entre reruns."""
    return f"{linha['data'].strftime('%Y%m%d')}-{linha['estado']}-{linha['latitude']:.3f}-{linha['longitude']:.3f}"


def _simular_envio_alerta() -> None:
    """Simula a latência de envio para as equipes de brigada."""
    barra = st.progress(0, text="Notificando brigadistas...")
    for pct in range(0, 101, 20):
        time.sleep(0.08)
        barra.progress(pct, text=f"Notificando brigadistas... {pct}%")
    barra.empty()
    st.toast("Alerta enviado às equipes de campo", icon="✅")


def render(df: pd.DataFrame) -> None:
    st.subheader("Central de Alertas")
    st.caption(
        "O PIROS identifica os focos críticos e sugere o envio de alerta. "
        "Cada alerta exige aprovação humana antes de notificar as brigadas — "
        "isso evita falsos positivos e mantém o operador no controle."
    )

    criticos = focos_criticos_para_alerta(df, limite=10)

    aprovados_total = len(st.session_state["alertas_aprovados"])
    rejeitados_total = len(st.session_state["alertas_rejeitados"])
    pendentes_total = sum(
        1 for _, linha in criticos.iterrows()
        if status_alerta(_alerta_id(linha)) == "pendente"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Pendentes", pendentes_total, "aguardam decisão", variante="medio")
    with col2:
        metric_card("Aprovados", aprovados_total, "alertas enviados", variante="ok")
    with col3:
        metric_card("Rejeitados", rejeitados_total, "descartados pelo operador", variante="neutro")

    st.markdown("---")

    if criticos.empty:
        st.success("Nenhum foco crítico identificado nos filtros atuais.")
        return

    st.markdown("#### Alertas sugeridos pelo sistema")
    st.caption("Ordenados por intensidade do fogo (FRP).")

    for _, linha in criticos.iterrows():
        alerta_id = _alerta_id(linha)
        status = status_alerta(alerta_id)

        status_html = {
            "pendente": '<span class="piros-status-pendente">● Aguardando decisão</span>',
            "aprovado": '<span class="piros-status-aprovado">● Alerta enviado</span>',
            "rejeitado": '<span class="piros-status-rejeitado">● Descartado</span>',
        }[status]

        st.markdown(
            f"""
            <div class="piros-alerta-card">
                <div class="id">ID {alerta_id}</div>
                <div class="info">
                    <b>{linha['estado']}</b> · {linha['bioma']} ·
                    FRP <b>{linha['frp_mw']:.1f} MW</b> ·
                    Confiança {linha['confianca']:.0f}% ·
                    {linha['data'].strftime('%d/%m/%Y')}
                </div>
                <div class="info" style="margin-top:6px;">{status_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if status == "pendente":
            c1, c2, _ = st.columns([1, 1, 4])
            with c1:
                if st.button("Aprovar envio", key=f"aprovar-{alerta_id}", type="primary"):
                    with st.spinner("Processando aprovação..."):
                        _simular_envio_alerta()
                    aprovar_alerta(alerta_id)
                    st.rerun()
            with c2:
                if st.button("Rejeitar", key=f"rejeitar-{alerta_id}"):
                    rejeitar_alerta(alerta_id)
                    st.rerun()
