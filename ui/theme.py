"""
Design System PIROS.

Concentra paleta de cores, tipografia, CSS global e o cabeçalho com logo.
Qualquer ajuste visual passa por aqui — nenhuma cor cravada no resto do projeto.
"""
from __future__ import annotations

import streamlit as st


COR_FUNDO = "#0B0F14"
COR_SUPERFICIE = "#141A22"
COR_BORDA = "#1F2A36"
COR_TEXTO = "#E6EDF3"
COR_TEXTO_SUAVE = "#8B98A5"

COR_PRIMARIA = "#FF6B35"

# Cores semânticas — usadas em todo o app para classificar risco.
CORES_RISCO = {
    "Baixo": "#3FB950",
    "Moderado": "#F0B429",
    "Alto": "#DC2626",
    "Crítico": "#9333EA",
}

ORDEM_RISCO = ["Baixo", "Moderado", "Alto", "Crítico"]


CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, sans-serif !important;
}}

.stApp {{
    background-color: {COR_FUNDO};
    color: {COR_TEXTO};
}}

section[data-testid="stSidebar"] {{
    background-color: {COR_SUPERFICIE};
    border-right: 1px solid {COR_BORDA};
}}

h1, h2, h3, h4 {{
    color: {COR_TEXTO} !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}}

.piros-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 8px 24px 8px;
    border-bottom: 1px solid {COR_BORDA};
    margin-bottom: 16px;
}}

.piros-header .logo {{
    width: 44px; height: 44px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, {COR_PRIMARIA} 0%, #E5484D 100%);
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(255, 107, 53, 0.35);
}}

.piros-header .titulo {{
    display: flex; flex-direction: column; line-height: 1.1;
}}

.piros-header .nome {{
    font-size: 22px; font-weight: 700; color: {COR_TEXTO};
    letter-spacing: -0.02em;
}}

.piros-header .tagline {{
    font-size: 12px; color: {COR_TEXTO_SUAVE};
    letter-spacing: 0.04em; text-transform: uppercase;
}}

.piros-metric {{
    background: {COR_SUPERFICIE};
    border: 1px solid {COR_BORDA};
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
}}

.piros-metric .rotulo {{
    font-size: 12px; color: {COR_TEXTO_SUAVE};
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-bottom: 8px;
}}

.piros-metric .valor {{
    font-size: 30px; font-weight: 700; color: {COR_TEXTO};
    line-height: 1;
}}

.piros-metric .rodape {{
    font-size: 12px; color: {COR_TEXTO_SUAVE}; margin-top: 8px;
}}

.piros-metric.critico {{ border-left: 4px solid {CORES_RISCO['Crítico']}; }}
.piros-metric.alto    {{ border-left: 4px solid {CORES_RISCO['Alto']}; }}
.piros-metric.medio   {{ border-left: 4px solid {CORES_RISCO['Moderado']}; }}
.piros-metric.ok      {{ border-left: 4px solid {CORES_RISCO['Baixo']}; }}

.piros-alerta-card {{
    background: {COR_SUPERFICIE};
    border: 1px solid {COR_BORDA};
    border-left: 4px solid {CORES_RISCO['Crítico']};
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
}}

.piros-alerta-card .id {{
    font-size: 11px; color: {COR_TEXTO_SUAVE};
    text-transform: uppercase; letter-spacing: 0.08em;
}}

.piros-alerta-card .info {{
    font-size: 14px; color: {COR_TEXTO}; margin-top: 4px;
}}

.piros-status-pendente {{ color: {CORES_RISCO['Moderado']}; font-weight: 600; }}
.piros-status-aprovado {{ color: {CORES_RISCO['Baixo']}; font-weight: 600; }}
.piros-status-rejeitado {{ color: {COR_TEXTO_SUAVE}; font-weight: 600; }}

div[data-testid="stMetricValue"] {{ font-family: 'Inter', sans-serif !important; }}

.stTabs [data-baseweb="tab-list"] {{
    gap: 6px; border-bottom: 1px solid {COR_BORDA};
}}
.stTabs [data-baseweb="tab"] {{
    color: {COR_TEXTO_SUAVE}; padding: 10px 18px;
}}
.stTabs [aria-selected="true"] {{
    color: {COR_PRIMARIA} !important;
    border-bottom: 2px solid {COR_PRIMARIA} !important;
}}
</style>
"""


LOGO_SVG = """
<svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2C12 2 6 8 6 14C6 17.3137 8.68629 20 12 20C15.3137 20 18 17.3137 18 14C18 12 17 10 16 9C15.5 11 14 12 13 12C14 9 12 5 12 2Z"
        fill="white"/>
  <path d="M12 14C12 14 10 16 10 17.5C10 18.8807 10.8954 20 12 20C13.1046 20 14 18.8807 14 17.5C14 16 12 14 12 14Z"
        fill="#FFD4B0"/>
</svg>
"""


def aplicar_tema() -> None:
    """Injeta o CSS global. Chamar uma vez no app.py, logo após o set_page_config."""
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


def cabecalho() -> None:
    """Renderiza o header com logo + nome do sistema. Compõe a identidade PIROS."""
    st.markdown(
        f"""
        <div class="piros-header">
            <div class="logo">{LOGO_SVG}</div>
            <div class="titulo">
                <span class="nome">PIROS</span>
                <span class="tagline">Plataforma Inteligente de Resposta a Ocorrências de queimadaS</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
