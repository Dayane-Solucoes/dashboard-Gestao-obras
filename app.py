import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Configuração da página para modo escuro e layout largo
st.set_page_config(
    page_title="Smart Obra - Dashboard Financeiro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILO CSS PERSONALIZADO (Idêntico ao Layout Dark Moderno das Imagens)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Fundo geral e fontes */
    .stApp {
        background-color: #0d091e;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background-color: #130f26;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Cartões de Indicadores (KPI Cards com gradiente e borda neon) */
    .metric-card {
        background: linear-gradient(135deg, rgba(27, 23, 54, 0.8) 0%, rgba(18, 15, 38, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 14px;
        color: #a0aec0;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
    }
    
    /* Estilização de Containers de Gráficos e Seções */
    .custom-container {
        background: linear-gradient(135deg, rgba(27, 23, 54, 0.6) 0%, rgba(18, 15, 38, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CARREGAMENTO DOS DADOS (EXCEL)
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        df_custo = pd.read_excel("Base de custo.xlsx")
        df_faturamento = pd.read_excel("Base faturamento.xlsx")
        df_contratos = pd.read_excel("Base contratos.xlsx")
    except Exception:
        # Gerando dados fictícios caso os arquivos ainda não estejam na pasta do GitHub
        # para que o aplicativo não quebre na primeira execução de teste.
        df_custo = pd.DataFrame({
            'Obra': ['Residencial Horizon', 'Torre Corporate', 'Residencial Horizon'],
            'Data': ['2026-01-15', '2026-02-10', '2026-03-05'],
            'Valor': [45000, 120000, 32000],
            'Categoria': ['Material', 'Mão de Obra', 'Equipamentos'],
            'Fornecedor': ['Construmax', 'Empreiteira Silva', 'Locadora Máquinas']
        })
        df_faturamento = pd.DataFrame({
            'Obra': ['Residencial Horizon', 'Torre Corporate', 'Residencial Horizon'],
            'Data': ['2026-01-20', '2026-02-15', '2026-03-10'],
            'Valor': [80000, 200000, 50000],
            'Status': ['Pago', 'Pendente', 'Pago']
        })
        df_contratos = pd.DataFrame({
            'Obra': ['Residencial Horizon', 'Torre Corporate'],
            'Cliente': ['Vertex Development', 'Alpha Group'],
            'Endereco': ['Av. Paulista, 1000 - SP', 'Rua das Flores, 500 - RJ'],
            'Gerente': ['Sarah Chen', 'Carlos Mendes'],
            'Orcamento_Total': [125000000, 85000000],
            'Inicio': ['2025-01-15', '2025-06-10'],
            'Termino': ['2028-12-20', '2027-11-30'],
            'Progresso': [45, 60],
            'Status_Obra': ['On Track', 'Delayed']
        })
    return df_custo, df_faturamento, df_contratos

df_custo, df_faturamento, df_contratos = carregar_dados()

# -----------------------------------------------------------------------------
# SIDEBAR (Menu e Navegação idêntica à referência)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔷 **SMART OBRA**")
    st.markdown("---")
    st.markdown("**Menu Principal**")
    pagina = st.radio(
        "Navegação",
        ["Financial Overview", "Project Budgets", "Cash Flow", "Revenue Analytics", "Cost Analytics", "Project Details (Aba da Obra)"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**Ferramentas Avançadas**")
    st.button("🔓 Unlock Advanced Tools", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# FILTROS GLOBAIS NO TOPO (Período e Obra)
# -----------------------------------------------------------------------------
col_f1, col_f2, col_f3 = st.columns([2, 2, 2])

with col_f1:
    lista_obras = ["Todas as Obras"] + list(df_contratos['Obra'].unique())
    obra_selecionada = st.selectbox("🏗️ Selecionar Obra", lista_obras)

with col_f2:
    periodo_analise = st.selectbox("📅 Período de Análise", ["Este Mês", "Últimos 30 Dias", "Último Trimestre", "Este Ano", "Todo o Período"])

with col_f3:
    status_filtro = st.selectbox("⚙️ Filtro por Status", ["Todos", "On Track", "Delayed", "AI Risk"])

st.markdown("---")

# Filtrando os DataFrames conforme a seleção da Obra
if obra_selecionada != "Todas as Obras":
    df_c_filtered = df_custo[df_custo['Obra'] == obra_selecionada]
    df_f_filtered = df_faturamento[df_faturamento['Obra'] == obra_selecionada]
    df_o_filtered = df_contratos[df_contratos['Obra'] == obra_selecionada].iloc[0]
else:
    df_c_filtered = df_custo
    df_f_filtered = df_faturamento
    df_o_filtered = df_contratos.iloc[0] # Padrão para visualização geral

# -----------------------------------------------------------------------------
# ABA 1: PROJECT DETAILS / DADOS DA OBRA (Solicitado pelo Usuário)
# -----------------------------------------------------------------------------
if pagina == "Project Details (Aba da Obra)":
    st.markdown("### 🏢 Ficha Completa da Obra e Contrato")
    
    col_det1, col_det2 = st.columns([1, 2])
    
    with col_det1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(27, 23, 54, 0.9) 0%, rgba(18, 15, 38, 0.95) 100%);
                    border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 16px; padding: 25px; text-align: center;">
            <div style="width: 100%; height: 220px; background-color: #1b1736; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.2); 
                        display: flex; align-items: center; justify-content: center; margin-bottom: 15px; color: #a0aec0;">
                📷 [Espaço para Foto da Obra]
            </div>
            <p style="font-size: 13px; color: #a0aec0;">Carregue ou atualize a imagem principal do projeto.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_det2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(27, 23, 54, 0.9) 0%, rgba(18, 15, 38, 0.95) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 30px;">
            <h3 style="color: #00f2fe; margin-top: 0; margin-bottom: 20px;">{df_o_filtered['Obra']}</h3>
            <p style="font-size: 16px; margin: 8px 0;"><strong>👤 Nome do Cliente:</strong> {df_o_filtered['Cliente']}</p>
            <p style="font-size: 16px; margin: 8px 0;"><strong>📍 Endereço Físico:</strong> {df_o_filtered['Endereco']}</p>
            <p style="font-size: 16px; margin: 8px 0;"><strong>👷 Gestor Responsável:</strong> {df_o_filtered['Gerente']}</p>
            <p style="font-size: 16px; margin: 8px 0;"><strong>💰 Orçamento Total:</strong> R$ {df_o_filtered['Orcamento_Total']:,.2f}</p>
            <p style="font-size: 16px; margin: 8px 0;"><strong>🚀 Início do Projeto:</strong> {df_o_filtered['Inicio']}</p>
            <p style="font-size: 16px; margin: 8px 0;"><strong>🎯 Término Previsto:</strong> {df_o_filtered['Termino']}</p>
            <p style="font-size: 16px; margin: 8px 0;"><strong>📊 Status Atual:</strong> <span style="color: #00f2fe;">{df_o_filtered['Status_Obra']} ({df_o_filtered['Progresso']}% Concluído)</span></p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA PRINCIPAL: FINANCIAL OVERVIEW & DASHBOARD
# -----------------------------------------------------------------------------
else:
    # 1. LINHA DE KPIS SUPERIORES (Estilo Gradiente da Imagem)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_fat = df_f_filtered['Valor'].sum() if not df_f_filtered.empty else 58947
    total_cust = df_c_filtered['Valor'].sum() if not df_c_filtered.empty else 315120
    saldo_caixa = total_fat - total_cust
    
    with kpi1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 3px solid #00f2fe;">
            <div class="metric-title">Total Revenue (Entradas)</div>
            <div class="metric-value">R$ {total_fat:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi2:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 3px solid #7928ca;">
            <div class="metric-title">Active Projects</div>
            <div class="metric-value">{len(df_contratos)} Obras</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi3:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 3px solid #ff007f;">
            <div class="metric-title">Cost Efficiency</div>
            <div class="metric-value">0.98</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi4:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 3px solid #00f2fe;">
            <div class="metric-title">Overdue Payments</div>
            <div class="metric-value">R$ 18,400</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. BLOCO CENTRAL: GRÁFICOS DE FLUXO DE CAIXA E ANÁLISE DE CUSTOS
    col_g1, col_g2 = st.columns([1, 1])
    
    with col_g1:
        st.markdown("""<div class="custom-container">""", unsafe_allow_html=True)
        st.subheader("Cash Flow Balance (Entradas vs Saídas)")
        
        # Gráfico de linhas simulando o fluxo da referência
        fig_cash = go.Figure()
        fig_cash.add_trace(go.Scatter(x=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'], y=[400, 600, 500, 700, 650, 900],
                                     mode='lines+markers', name='Cash In', line=dict(color='#00f2fe', width=3)))
        fig_cash.add_trace(go.Scatter(x=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'], y=[200, 350, 300, 450, 400, 600],
                                     mode='lines+markers', name='Cash Out', line=dict(color='#7928ca', width=3)))
        
        fig_cash.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_cash, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown("""<div class="custom-container">""", unsafe_allow_html=True)
        st.subheader("Revenue & Cost Analytics")
        
        # Gráfico de barras combinadas
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], y=[400, 600, 800, 300, 500, 700],
                                marker_color='#00f2fe', name='Faturamento'))
        fig_bar.add_trace(go.Bar(x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], y=[200, 300, 400, 150, 250, 350],
                                marker_color='#7928ca', name='Custos NFs'))
        
        fig_bar.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. BLOCO INFERIOR: TABELAS E PROJETOS ATIVOS
    col_b1, col_b2 = st.columns([1, 1])
    
    with col_b1:
        st.markdown("""
        <div class="custom-container">
            <h3>Active Projects Overview</h3>
            <p style="color: #a0aec0; font-size: 13px;">Status de andamento e risco das obras cadastradas.</p>
        """, unsafe_allow_html=True)
        
        for idx, row in df_contratos.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div>
                    <span style="color: #00f2fe; font-weight: 600;">{row['Obra']}</span><br>
                    <span style="font-size: 12px; color: #a0aec0;">Cliente: {row['Cliente']}</span>
                </div>
                <div style="text-align: right;">
                    <span style="background: rgba(0, 242, 254, 0.1); color: #00f2fe; padding: 4px 8px; border-radius: 6px; font-size: 12px;">{row['Status_Obra']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b2:
        st.markdown("""
        <div class="custom-container">
            <h3>Revenue History (Notas Fiscais Recentes)</h3>
            <p style="color: #a0aec0; font-size: 13px;">Histórico de faturamentos e custos processados pelas bases.</p>
        """, unsafe_allow_html=True)
        
        # Tabela limpa simulando o histórico
        df_historico = pd.DataFrame({
            'Marketplaces / Fornecedor': ['Construmax NFs', 'Empreiteira Silva', 'Locadora Máquinas', 'Aço & Cia'],
            'Date': ['Oct 16, 2026', 'Oct 15, 2026', 'Oct 14, 2026', 'Oct 12, 2026'],
            'Payouts': ['$844.68', '$1,400.1k', '$182.99', '$138.4k'],
            'Status': ['Paid', 'Pending', 'Paid', 'Pending']
        })
        st.dataframe(df_historico, use_container_width=True, hide_index=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
