# PIROS — Plataforma Inteligente de Resposta a Ocorrências de queimadaS

Dashboard interativo para monitoramento de focos de queimada no Brasil, construído como Prova de Conceito da Global Solution **Front-End e Mobile Development em Sistemas de IA — FIAP 2026/1**.

> O PIROS transforma dados massivos de detecção satelital em **decisões acionáveis** para equipes de combate, mantendo o operador humano no centro do processo de envio de alertas.

---

## 👥 Integrantes

| Nome | RM |
| --- | --- |
| Vinicius Alef Araujo Cruz | RM564504 |
| Ian Nobres Azevedo | RM561681 |

Turma: **2TIAPY**

---

## 🔥 O problema

Eventos climáticos extremos e queimadas exigem ferramentas que transformem volumes massivos de dados satelitais em informação **acionável para tomadores de decisão não-técnicos** (coordenadores de brigadas, gestores de defesa civil).

Um modelo de IA por mais preciso que seja é inútil se a interface for confusa, lenta ou pouco confiável. O PIROS resolve isso entregando:

- **Visão consolidada** em segundos (panorama operacional).
- **Localização geográfica precisa** dos focos detectados.
- **Fluxo de aprovação humana** antes de qualquer alerta ser enviado às equipes de campo, evitando falsos positivos e mantendo o operador no controle.

---

## 📦 Fonte de dados

A POC consome um dataset **simulado** que imita a resposta do [BDQueimadas / INPE](https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/), com:

- Distribuição geográfica ponderada por estado (AM, PA, MT, MA concentram a maioria dos focos, refletindo o padrão histórico real).
- **FRP (Fire Radiative Power, MW)** — métrica usada de fato pelo INPE — em distribuição log-normal.
- Confiabilidade da detecção (50–100%).
- Bioma associado.
- Janela de 90 dias móveis a partir da data atual.

O dataset é gerado com semente fixa (`semente=42`), garantindo reprodutibilidade na apresentação. Em uma evolução, basta substituir o `providers/fire_data_provider.py` por uma chamada HTTP real — o restante do pipeline não muda.

---

## 🛠️ Framework escolhido: Streamlit

**Por quê?**

| Critério | Streamlit | Gradio |
| --- | --- | --- |
| Curva de aprendizado | Mais baixa | Maior |
| Layout (sidebar, tabs, colunas) | Nativos e flexíveis | Mais limitado |
| Cache (`@st.cache_data`) | Estável e simples | Não tem equivalente direto |
| `session_state` | Centralizado e claro | `gr.State` funciona bem para Q&A, menos para dashboards multi-tela |
| Ecossistema Plotly | Excelente (`st.plotly_chart`) | Bom |

Streamlit foi escolhido por **alinhar melhor com o padrão arquitetural exigido pelo enunciado** (5 camadas, cache + session_state) e por permitir um layout multi-aba com sidebar persistente — essencial para a jornada do usuário do panorama ao detalhe.

---

## 🏗️ Arquitetura

```
FRONT/
├── app.py                          # Entrada: configura página, sidebar e abas
├── requirements.txt
├── README.md
│
├── providers/                      # Acesso a dados externos
│   └── fire_data_provider.py       # Simula API do INPE (cacheado)
│
├── pipelines/                      # Transformação de dados
│   └── fire_pipeline.py            # Filtros, agregações, KPIs, classificação de risco
│
├── features/                       # Telas (uma por arquivo)
│   ├── panorama.py                 # KPIs + linha temporal + ranking + donut
│   ├── mapa.py                     # Mapa Plotly interativo
│   └── alertas.py                  # Feedback humano (aprovar/rejeitar)
│
├── state/                          # Estado da sessão
│   └── session.py                  # init_state, alertas aprovados/rejeitados
│
└── ui/                             # Componentes visuais reutilizáveis
    ├── theme.py                    # Design System PIROS (CSS, paleta, logo)
    ├── metric_card.py              # Componente de KPI (usado em 2 telas)
    └── charts.py                   # 4 funções de gráficos Plotly
```

### Diagrama de fluxo

```
┌──────────────┐
│   Usuário    │  ajusta filtros na sidebar
└──────┬───────┘
       │
       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  providers/      │ →  │  pipelines/      │ →  │  features/       │
│  (cache_data)    │    │  (cache_data)    │    │  (renderização)  │
└──────────────────┘    └──────────────────┘    └────────┬─────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────────┐
                                              │  ui/  (cards,       │
                                              │  charts, tema)      │
                                              └─────────────────────┘

       state/session.py  ←  guarda decisões do usuário (alertas)
```

### Por que essa divisão?

- **providers/** isola I/O. Trocar de dados mockados para a API real do INPE = trocar 1 arquivo.
- **pipelines/** é puramente lógica de dados. Pode ser testado/executado **sem o Streamlit** (veja `python -m pipelines.fire_pipeline`).
- **features/** mantém cada tela autônoma e legível.
- **state/** centraliza `session_state` — nada de chave mágica espalhada pelo código.
- **ui/** força reuso visual e consistência do design system.

---

## ✅ Checklist dos requisitos da disciplina

### 3.1 Ciclo de execução e estado

- ✅ `@st.cache_data` em `providers/fire_data_provider.py` → o dataset só é gerado uma vez.
- ✅ `@st.cache_data` em `pipelines/fire_pipeline.py` → o enriquecimento e a filtragem são cacheados.
- ✅ `st.session_state` centralizado em `state/session.py` (filtros + alertas aprovados/rejeitados).

### 3.2 Arquitetura

- ✅ Código componentizado nas **5 camadas exigidas** (providers, pipelines, features, state, ui).
- ✅ Nada de arquivo monolítico.

### 3.3 Funcionalidades

- ✅ **3 filtros interativos:** intervalo de datas, estado (UF) e risco mínimo (slider).
- ✅ **2 visualizações com Plotly:** mapa de focos + linha temporal + donut de distribuição + ranking de estados (4 ao todo).
- ✅ **Componente reutilizável:** `metric_card()` é invocado em `features/panorama.py` (4 vezes) e em `features/alertas.py` (3 vezes).

### 3.4 Teoria do Design e UX/UI

- ✅ **Layout organizado:** sidebar persistente + 3 abas + colunas internas.
- ✅ **Design para latência:** `st.spinner` no carregamento de dados, `st.progress` no envio simulado de alerta.
- ✅ **Cores semânticas:** verde (Baixo) → amarelo (Moderado) → laranja (Alto) → vermelho (Crítico). Aplicado no mapa, donut, cartões de KPI e cards de alerta.
- ✅ **Feedback humano:** aba **Alertas** lista focos críticos; cada um exige **Aprovar / Rejeitar** antes de ir para o campo.

### Diferencial implementado

- ✅ **Design system próprio:** identidade "PIROS" com logo SVG, tipografia Inter, paleta consistente, componentes reutilizáveis. Tudo centralizado em `ui/theme.py`.

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.10 ou superior
- pip atualizado

### Instalação

```bash
git clone https://github.com/<seu-usuario>/<seu-repo>.git
cd <seu-repo>
pip install -r requirements.txt
```

### Executar o dashboard

```bash
streamlit run app.py
```

Se o comando `streamlit` não for reconhecido (PATH do Windows), use:

```bash
python -m streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

### Executar provider e pipeline isolados (sem UI)

A arquitetura permite rodar as camadas de dados sem o Streamlit — útil para debug:

```bash
python -m providers.fire_data_provider
python -m pipelines.fire_pipeline
```

---

## 🎬 Vídeo de apresentação

Disponível em: https://www.youtube.com/watch?v=PxtyJO-xIPI

---

## 📋 Stack

- **Streamlit 1.40** — framework de UI
- **Plotly 5.24** — gráficos interativos (mapa, linha, donut, barras)
- **Pandas 2.2** — manipulação de dados
- **NumPy 2.1** — geração dos dados mockados
