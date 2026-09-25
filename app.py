from pathlib import Path
from datetime import datetime, timedelta
import io
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "dados"

st.set_page_config(
    page_title="Smart Obra | Dashboard Financeiro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Visual system inspired by the supplied HTML
# -----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root { --bg:#0b0d19; --sidebar:#121528; --card:#181b34; --border:#272b52; --cyan:#00f2fe; --purple:#7928ca; --pink:#ff007f; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at 80% 0%, rgba(121,40,202,.12), transparent 32%), #0b0d19; color:#f3f4f6; }
section[data-testid="stSidebar"] { background: rgba(18,21,40,.96); border-right:1px solid rgba(255,255,255,.06); }
section[data-testid="stSidebar"] > div { padding-top: 1rem; }
.block-container { padding: 1.25rem 2rem 3rem; max-width: 100%; }
.brand { display:flex; align-items:center; gap:.75rem; padding:.4rem 0 1.25rem; border-bottom:1px solid rgba(255,255,255,.06); margin-bottom:1rem; }
.brand-icon { width:42px; height:42px; border-radius:14px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#22d3ee,#7c3aed); box-shadow:0 0 22px rgba(0,242,254,.25); font-size:22px; }
.brand-name { font-size:1.05rem; font-weight:700; letter-spacing:.12em; background:linear-gradient(90deg,#fff,#a5f3fc,#22d3ee); -webkit-background-clip:text; color:transparent; }
.brand-sub { color:#22d3ee; opacity:.8; font-size:.68rem; }
.side-label { color:#6b7280; font-size:.68rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin:.9rem 0 .35rem; }
.side-note { margin-top:2rem; padding:1rem; border-radius:16px; background:linear-gradient(180deg,rgba(88,28,135,.35),rgba(30,27,75,.5)); border:1px solid rgba(168,85,247,.22); }
.topbar { display:flex; align-items:center; justify-content:space-between; padding: .7rem 0 1rem; border-bottom:1px solid rgba(255,255,255,.06); margin-bottom:1.1rem; }
.title { font-size:1.35rem; font-weight:700; color:#fff; }
.subtitle, .muted { color:#9ca3af; font-size:.76rem; }
.live { display:inline-block; margin-left:.4rem; padding:.17rem .55rem; border-radius:999px; color:#67e8f9; background:rgba(6,182,212,.1); border:1px solid rgba(6,182,212,.22); font-size:.68rem; font-weight:600; }
.section-title { color:#fff; font-size:1rem; font-weight:700; margin:0; }
.section-sub { color:#9ca3af; font-size:.72rem; margin-top:.25rem; }
.kpi { min-height:160px; padding:1.05rem; border-radius:16px; background:linear-gradient(145deg,rgba(24,27,52,.88),rgba(20,23,45,.68)); border:1px solid rgba(255,255,255,.08); box-shadow:0 0 24px rgba(0,242,254,.04); }
.kpi:hover { border-color:rgba(0,242,254,.35); }
.kpi-icon { font-size:1.35rem; width:40px; height:40px; display:flex; align-items:center; justify-content:center; border-radius:12px; background:rgba(0,242,254,.12); border:1px solid rgba(0,242,254,.25); }
.kpi-label { color:#9ca3af; font-size:.67rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase; margin-top:.9rem; }
.kpi-value { color:#fff; font-size:1.55rem; font-weight:700; margin:.25rem 0 .65rem; }
.kpi-foot { border-top:1px solid rgba(255,255,255,.06); padding-top:.55rem; display:flex; justify-content:space-between; gap:.4rem; color:#9ca3af; font-size:.68rem; }
.pill { display:inline-block; padding:.2rem .5rem; border-radius:999px; font-size:.67rem; font-weight:600; }
.pill-green { color:#34d399; background:rgba(16,185,129,.11); }
.pill-amber { color:#fbbf24; background:rgba(245,158,11,.11); }
.card { padding:1.2rem; border-radius:16px; background:rgba(24,27,52,.72); border:1px solid rgba(255,255,255,.08); }
div[data-testid="stMetric"] { background:transparent; }
.stButton > button, .stDownloadButton > button { border-radius:10px; border:1px solid rgba(255,255,255,.10); background:rgba(255,255,255,.05); color:#d1d5db; }
.stButton > button:hover, .stDownloadButton > button:hover { color:#fff; border-color:rgba(0,242,254,.35); }
[data-baseweb="select"] > div { background:#181b34; border-color:rgba(255,255,255,.10); }
[data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,.08); }
hr { border-color:rgba(255,255,255,.07); }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Data layer
# -----------------------------
@st.cache_data(show_spinner=False)
def read_bases():
    contratos = pd.read_excel(DATA_DIR / "BD_Contratos.xlsx", sheet_name="Base_Contratos")
    custos = pd.read_excel(DATA_DIR / "BD_Custo.xlsx", sheet_name="Base_Custo")
    faturamento = pd.read_excel(DATA_DIR / "BD_Faturamento.xlsx", sheet_name="Base_Faturamento")
    return contratos, custos, faturamento


def num(df, col):
    return pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)


def brl(value):
    value = float(value or 0)
    s = f"R$ {value:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def compact_brl(value):
    value = float(value or 0)
    if abs(value) >= 1_000_000:
        return f"R$ {value/1_000_000:.1f} mi".replace(".", ",")
    if abs(value) >= 1_000:
        return f"R$ {value/1_000:.0f} mil".replace(".", ",")
    return brl(value)


def clean_key(series):
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def prepare_data():
    contratos, custos, faturamento = read_bases()
    contratos["obra_id"] = clean_key(contratos["N° Obra"])
    custos["obra_id"] = clean_key(custos["Filial AJUST"])
    faturamento["obra_id"] = clean_key(faturamento["OBRA"])
    custos["data"] = pd.to_datetime(custos["Comp. C"], errors="coerce")
    faturamento["data"] = pd.to_datetime(faturamento["Competência"], errors="coerce")
    contratos["Fim Contrato"] = pd.to_datetime(contratos["Fim Contrato"], errors="coerce")
    contratos["Valor Final Contratual"] = num(contratos, "Valor Final Contratual")
    contratos["Custo Previsto"] = num(contratos, "Custo Previsto")
    custos["valor"] = num(custos, "Vr. Rateio")
    custos["valor_liquido"] = num(custos, "Vr. Líquido")
    faturamento["valor_bruto"] = num(faturamento, "Valor Bruto")
    faturamento["valor_liquido"] = num(faturamento, "Valor Líquido NF")
    return contratos, custos, faturamento


contratos, custos, faturamento = prepare_data()

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">🏗️</div><div><div class="brand-name">SMART OBRA</div><div class="brand-sub">Gestão de NFs & Custos</div></div></div>', unsafe_allow_html=True)
    busca = st.text_input("Buscar projeto, NF...", placeholder="Digite obra, cliente ou NF")
    st.markdown('<div class="side-label">Navegação</div>', unsafe_allow_html=True)
    pagina = st.radio("Navegação", ["Dashboard Geral", "Notas Fiscais (NFs)", "Fluxo de Caixa", "Análise de Custos", "Obras & Canteiros"], label_visibility="collapsed")
    st.markdown('<div class="side-label">Administração</div>', unsafe_allow_html=True)
    st.radio("Administração", ["Fornecedores", "Configurações"], label_visibility="collapsed")
    st.markdown('<div class="side-note"><div style="font-size:1.25rem">🛡️</div><b style="color:#fff;font-size:.78rem">Módulo Avançado IA</b><div style="color:#9ca3af;font-size:.68rem;margin:.35rem 0 .75rem">Previsão de estouro de orçamento baseada nos dados atuais.</div></div>', unsafe_allow_html=True)

# -----------------------------
# Controls
# -----------------------------
obra_options = {"Todas as obras": None}
for _, r in contratos.sort_values("N° Obra").iterrows():
    obra_options[f"{int(r['N° Obra'])} · {str(r.get('NM Contrato',''))[:42]}"] = r["obra_id"]
obra_label = st.selectbox("Obra Selecionada", list(obra_options.keys()))
obra_id = obra_options[obra_label]

valid_dates = pd.concat([custos["data"].dropna(), faturamento["data"].dropna()])
min_date = valid_dates.min().date() if len(valid_dates) else datetime.now().date()
max_date = valid_dates.max().date() if len(valid_dates) else datetime.now().date()
periodo = st.radio("Período", ["Todo período", "Mensal", "Trimestral", "Personalizado"], horizontal=True, index=1)
if periodo == "Mensal":
    ultimo = pd.Timestamp(max_date).to_period("M")
    start_date, end_date = ultimo.start_time.date(), ultimo.end_time.date()
elif periodo == "Trimestral":
    ultimo = pd.Timestamp(max_date).to_period("Q")
    start_date, end_date = ultimo.start_time.date(), ultimo.end_time.date()
elif periodo == "Personalizado":
    start_date, end_date = st.date_input("Intervalo", (min_date, max_date), min_value=min_date, max_value=max_date)
else:
    start_date, end_date = min_date, max_date

if obra_id is not None:
    c = contratos[contratos["obra_id"] == obra_id]
    custos_f = custos[custos["obra_id"] == obra_id]
    fat_f = faturamento[faturamento["obra_id"] == obra_id]
else:
    c, custos_f, fat_f = contratos.copy(), custos.copy(), faturamento.copy()

custos_f = custos_f[(custos_f["data"].dt.date >= start_date) & (custos_f["data"].dt.date <= end_date)]
fat_f = fat_f[(fat_f["data"].dt.date >= start_date) & (fat_f["data"].dt.date <= end_date)]

if busca:
    q = busca.lower()
    mask_c = c.astype(str).apply(lambda col: col.str.lower().str.contains(q, na=False)).any(axis=1)
    mask_k = custos_f.astype(str).apply(lambda col: col.str.lower().str.contains(q, na=False)).any(axis=1)
    mask_f = fat_f.astype(str).apply(lambda col: col.str.lower().str.contains(q, na=False)).any(axis=1)
    c, custos_f, fat_f = c[mask_c], custos_f[mask_k], fat_f[mask_f]

receita = fat_f["valor_liquido"].sum()
custo = custos_f["valor"].sum()
saldo = receita - custo
contratual = c["Valor Final Contratual"].sum()
previsto = c["Custo Previsto"].sum()
mar = (saldo / receita * 100) if receita else 0
orc = (custo / previsto * 100) if previsto else 0

# -----------------------------
# Header
# -----------------------------
st.markdown(f'<div class="topbar"><div><div class="title">{pagina} <span class="live">Live Sync</span></div><div class="subtitle">Acompanhamento em tempo real de notas fiscais, custos e fluxo de caixa.</div></div><div style="text-align:right"><b style="color:#fff;font-size:.8rem">Mariana Costa</b><br><span style="color:#22d3ee;font-size:.68rem">Engenheira Gestora</span></div></div>', unsafe_allow_html=True)
st.caption(f"Dados carregados: {len(contratos):,} contratos · {len(custos):,} lançamentos de custo · {len(faturamento):,} notas fiscais".replace(",", "."))

# -----------------------------
# KPI cards
# -----------------------------
def kpi(icon, label, value, foot_left, foot_right, tone="cyan"):
    colors = {"cyan":"#67e8f9", "blue":"#93c5fd", "purple":"#c4b5fd", "pink":"#f9a8d4"}
    col = colors.get(tone, colors["cyan"])
    return f'''<div class="kpi"><div class="kpi-icon" style="color:{col};border-color:{col}55;background:{col}1a">{icon}</div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-foot"><span>{foot_left}</span><span style="color:{col}">{foot_right}</span></div></div>'''

kpi_cols = st.columns(4)
with kpi_cols[0]: st.markdown(kpi("↙", "Entradas (Receitas NFs)", compact_brl(receita), f"Previsto: {compact_brl(contratual)}", f"{(receita/contratual*100 if contratual else 0):.1f}% realizado", "cyan"), unsafe_allow_html=True)
with kpi_cols[1]: st.markdown(kpi("↗", "Custos Executados (Saídas)", compact_brl(custo), f"Orçamento: {compact_brl(previsto)}", f"{orc:.1f}% orçamento", "blue"), unsafe_allow_html=True)
with kpi_cols[2]: st.markdown(kpi("◈", "Saldo em Caixa da Obra", compact_brl(saldo), "Faturamento líquido - custo", "Positivo" if saldo >= 0 else "Atenção", "purple"), unsafe_allow_html=True)
with kpi_cols[3]: st.markdown(kpi("◌", "Margem Realizada", f"{mar:.1f}%", f"Contratual: {compact_brl(contratual)}", "Saudável" if mar >= 0 else "Negativa", "pink"), unsafe_allow_html=True)

st.write("")

# -----------------------------
# Charts
# -----------------------------
left, right = st.columns([2, 1])
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Evolução do Fluxo de Caixa (Entradas vs. Saídas)</div><div class="section-sub">Consolidação mensal das notas fiscais e lançamentos de custo.</div>', unsafe_allow_html=True)
    monthly_f = fat_f.dropna(subset=["data"]).groupby(fat_f.loc[fat_f["data"].notna(), "data"].dt.to_period("M"))["valor_liquido"].sum().rename("Entradas")
    monthly_c = custos_f.dropna(subset=["data"]).groupby(custos_f.loc[custos_f["data"].notna(), "data"].dt.to_period("M"))["valor"].sum().rename("Saídas")
    flow = pd.concat([monthly_f, monthly_c], axis=1).fillna(0).sort_index().reset_index()
    flow["Mês"] = flow["data"].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=flow["Mês"], y=flow["Entradas"], name="Entradas", mode="lines+markers", line=dict(color="#00f2fe", width=3), fill="tozeroy", fillcolor="rgba(0,242,254,.10)"))
    fig.add_trace(go.Scatter(x=flow["Mês"], y=flow["Saídas"], name="Saídas", mode="lines+markers", line=dict(color="#7928ca", width=3), fill="tozeroy", fillcolor="rgba(121,40,202,.10)"))
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=15,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#9ca3af", legend=dict(orientation="h", y=1.1), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.08)", tickprefix="R$ ", separatethousands=True))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(f'<div class="muted">Pico de faturamento: <b style="color:#fff">{flow.loc[flow["Entradas"].idxmax(), "Mês"] if len(flow) else "—"}</b> · Maior custo mensal: <b style="color:#fff">{flow.loc[flow["Saídas"].idxmax(), "Mês"] if len(flow) else "—"}</b></div></div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Custos por Categoria</div><div class="section-sub">Distribuição dos gastos executados por grupo DRE.</div>', unsafe_allow_html=True)
    cat_col = "DEPARA DRE" if "DEPARA DRE" in custos_f.columns else "GRUPO 1"
    cats = custos_f.groupby(cat_col, dropna=False)["valor"].sum().sort_values(ascending=False).head(6).reset_index()
    cats.columns = ["Categoria", "Valor"]
    cats["Categoria"] = cats["Categoria"].fillna("Não classificado").astype(str).str.slice(0, 34)
    fig2 = px.bar(cats.sort_values("Valor"), x="Valor", y="Categoria", orientation="h", color="Valor", color_continuous_scale=[[0,"#7928ca"],[.5,"#4facfe"],[1,"#00f2fe"]])
    fig2.update_layout(height=300, margin=dict(l=0,r=0,t=15,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#9ca3af", coloraxis_showscale=False, xaxis=dict(showgrid=False, tickprefix="R$ "), yaxis=dict(showgrid=False))
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown(f'<div class="muted">Total executado: <b style="color:#fff">{brl(custo)}</b></div></div>', unsafe_allow_html=True)

# -----------------------------
# Lower panels
# -----------------------------
left2, right2 = st.columns([1, 2])
with left2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Status das Obras <span class="pill pill-green">{len(c)} selecionadas</span></div><div class="section-sub">Acompanhamento financeiro por canteiro.</div>', unsafe_allow_html=True)
    for _, row in c.head(6).iterrows():
        nome = str(row.get("NM Contrato", "Obra sem nome"))
        obra = row.get("N° Obra", "—")
        valor_f = float(row.get("Valor Final Contratual", 0) or 0)
        custo_p = float(row.get("Custo Previsto", 0) or 0)
        pct = min(100, custo_p / valor_f * 100) if valor_f else 0
        status = str(row.get("Status", "—"))
        st.markdown(f'<div style="padding:.7rem 0;border-bottom:1px solid rgba(255,255,255,.06)"><div style="display:flex;justify-content:space-between;gap:.5rem"><b style="font-size:.75rem;color:#fff">#{obra} · {nome[:31]}</b><span class="pill pill-green">{status}</span></div><div class="muted" style="margin:.35rem 0">Custo previsto: {brl(custo_p)} · Contrato: {brl(valor_f)}</div><div style="height:6px;background:rgba(255,255,255,.06);border-radius:99px"><div style="width:{pct:.1f}%;height:100%;background:linear-gradient(90deg,#00f2fe,#7928ca);border-radius:99px"></div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    top_a, top_b = st.columns([3,1])
    with top_a:
        st.markdown('<div class="section-title">Histórico de Notas Fiscais Recentes</div><div class="section-sub">Últimas entradas processadas na base de faturamento.</div>', unsafe_allow_html=True)
    with top_b:
        csv = fat_f.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⇩ Exportar CSV", csv, "notas_fiscais_filtradas.csv", "text/csv")
    if len(fat_f):
        show = fat_f.sort_values("data", ascending=False).head(8).copy()
        show["NF / Cliente"] = show["Notas Emitidas"].astype(str) + " · " + show["CLIENTE"].astype(str).str.slice(0,28)
        show["Tipo"] = "Entrada"
        show["Data"] = show["data"].dt.strftime("%d/%m/%Y")
        show["Valor líquido"] = show["valor_liquido"].map(brl)
        st.dataframe(show[["NF / Cliente", "Tipo", "Data", "Valor líquido", "OBRA"]], use_container_width=True, hide_index=True, height=300)
    else:
        st.info("Nenhuma nota fiscal encontrada para os filtros atuais.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Extra pages / downloads
# -----------------------------
if pagina == "Notas Fiscais (NFs)":
    st.subheader("Notas Fiscais")
    st.dataframe(fat_f, use_container_width=True, hide_index=True)
elif pagina == "Análise de Custos":
    st.subheader("Análise detalhada de custos")
    st.dataframe(custos_f.sort_values("valor", ascending=False), use_container_width=True, hide_index=True)
elif pagina == "Obras & Canteiros":
    st.subheader("Obras e contratos")
    st.dataframe(c, use_container_width=True, hide_index=True)
elif pagina == "Fluxo de Caixa":
    st.subheader("Fluxo de caixa por competência")
    st.dataframe(flow if 'flow' in locals() else pd.DataFrame(), use_container_width=True, hide_index=True)

st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} · Fonte: arquivos Excel locais em /dados")
