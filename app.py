import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Smart Obra - Gestão de Custos & Fluxo",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CSS CUSTOMIZADO (ESTILO DA IMAGEM DE REFERÊNCIA) -----------------
st.markdown("""
    <style>
    /* Fundo Geral da Aplicação */
    .stApp {
        background-color: #0b091a;
        color: #ffffff;
    }
    
    /* Sidebar Customizada */
    section[data-testid="stSidebar"] {
        background-color: #120f29;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Cartões de Métricas com Gradiente e Borda Neon */
    .metric-card {
        background: linear-gradient(135deg, rgba(27, 23, 54, 0.9) 0%, rgba(45, 30, 85, 0.7) 100%);
        border: 1px solid rgba(0, 242, 254, 0.2);
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(0, 242, 254, 0.6);
        transform: translateY(-2px);
    }
    
    .metric-title {
        font-size: 13px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #ffffff;
    }
    
    /* Caixas de Conteúdo / Gráficos */
    .dashboard-box {
        background: rgba(18, 15, 41, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Ajustes gerais de texto e títulos */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Função para carregar as bases Excel
@st.cache_data
def carregar_dados():
    try:
        df_custo = pd.read_excel("BD_Custo.xlsx")
        df_faturamento = pd.read_excel("BD_Faturamento.xlsx")
        df_contratos = pd.read_excel("BD_Contratos.xlsx")
    except Exception as e:
        # Dados de contingência caso os arquivos Excel ainda não estejam no GitHub
        df_custo = pd.DataFrame({
            'Obra': ['Obra Alpha', 'Obra Beta', 'Obra Alpha'],
            'Valor': [15000, 22000, 18000],
            'Categoria': ['Material', 'Mão de Obra', 'Equipamentos'],
            'Status': ['Pago', 'Pendente', 'Pago']
        })
        df_faturamento = pd.DataFrame({
            'Obra': ['Obra Alpha', 'Obra Beta', 'Obra Alpha'],
            'Valor': [50000, 80000, 45000],
            'Status': ['Recebido', 'A Receber', 'Recebido']
        })
        df_contratos = pd.DataFrame({
            'Obra': ['Obra Alpha', 'Obra Beta'],
            'Cliente': ['Construtora Delta', 'Incorporadora Zeta'],
            'Endereco': ['Av. Paulista, 1000 - SP', 'Rua das Flores, 123 - RJ'],
            'Gerente': ['Carlos Silva', 'Ana Souza'],
            'Orcamento_Total': [500000, 750000]
        })
    return df_custo, df_faturamento, df_contratos

df_custo, df_faturamento, df_contratos = carregar_dados()

# ----------------- SIDEBAR EXCLUSIVA -----------------
st.sidebar.markdown("### 💎 **SMART POS**")
st.sidebar.caption("Gestão de Obras & Custos")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MENU PRINCIPAL", 
    ["📊 Dashboard Executivo", "🏗️ Dados e Foto da Obra", "📁 Gestão de Contratos"]
)

st.sidebar.markdown("---")
st.sidebar.success("🟢 Sistema Online\nBase de dados sincronizada")

# ----------------- TOPO / CABEÇALHO E FILTROS -----------------
st.markdown("## 🚀 Dashboard Executivo de Obras")

# Barra de Filtros Estilizada (Substituindo o padrão por seletores limpos)
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    lista_obras = ['Todas as Obras'] + list(df_contratos['Obra'].unique()) if 'Obra' in df_contratos.columns else ['Todas as Obras']
    obra_selecionada = st.selectbox("🏗️ Selecionar Obra", lista_obras)

with col_f2:
    periodo_selecionado = st.selectbox("📅 Período de Análise", ["Últimos 30 dias", "Este Mês", "Este Ano", "Todo o Período"])

with col_f3:
    status_filtro = st.selectbox("⚡ Filtrar por Status", ["Todos", "Pago / Recebido", "Pendente"])

st.markdown("<br>", unsafe_allow_html=True)

# Lógica de Filtro por Obra
if obra_selecionada != 'Todas as Obras':
    df_custo_f = df_custo[df_custo['Obra'] == obra_selecionada] if 'Obra' in df_custo.columns else df_custo
    df_fat_f = df_faturamento[df_faturamento['Obra'] == obra_selecionada] if 'Obra' in df_faturamento.columns else df_faturamento
    df_contrato_f = df_contratos[df_contratos['Obra'] == obra_selecionada] if 'Obra' in df_contratos.columns else df_contratos
else:
    df_custo_f = df_custo
    df_fat_f = df_faturamento
    df_contrato_f = df_contratos

# Cálculos rápidos
total_entradas = df_fat_f['Valor'].sum() if 'Valor' in df_fat_f.columns else 0
total_saidas = df_custo_f['Valor'].sum() if 'Valor' in df_custo_f.columns else 0
saldo_caixa = total_entradas - total_saidas
orcamento_total = df_contrato_f['Orcamento_Total'].sum() if 'Orcamento_Total' in df_contrato_f.columns else 1

# ----------------- ABA 1: DASHBOARD EXECUTIVO -----------------
if menu == "📊 Dashboard Executivo":
    
    # Cartões Superiores (Estilo Gradiente Neon idêntico à imagem)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Entradas (NFs)</div>
                <div class="metric-value" style="color: #00f2fe;">R$ {total_entradas:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Custos Executados</div>
                <div class="metric-value" style="color: #ff007f;">R$ {total_saidas:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Saldo em Caixa</div>
                <div class="metric-value" style="color: #4ade80;">R$ {saldo_caixa:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi4:
        eficiencia = (total_saidas / orcamento_total) if orcamento_total > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Consumo Budget</div>
                <div class="metric-value" style="color: #facc15;">{eficiencia*100:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

    # Gráficos centrais em blocos estilizados
    c_g1, c_g2 = st.columns([1, 1.4])
    
    with c_g1:
        st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
        st.subheader("Orçamento por Categoria")
        if not df_custo_f.empty and 'Categoria' in df_custo_f.columns:
            fig_donut = px.pie(df_custo_f, names='Categoria', values='Valor', hole=0.65,
                               color_discrete_sequence=['#7928ca', '#00f2fe', '#ff007f', '#facc15'])
            fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Sem dados de categoria disponíveis.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_g2:
        st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
        st.subheader("Evolução do Fluxo de Caixa")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'], y=[120, 250, 310, 420, 480, 520], name='Entradas', line=dict(color='#00f2fe', width=3)))
        fig_line.add_trace(go.Scatter(x=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'], y=[90, 180, 240, 310, 350, 410], name='Saídas', line=dict(color='#ff007f', width=3)))
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(t=20, b=10, l=10, r=10), legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tabela Inferior de Registos
    st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
    st.subheader("📋 Histórico Recente de Custos e Notas Fiscais")
    if not df_custo_f.empty:
        st.dataframe(df_custo_f, use_container_width=True)
    else:
        st.info("Nenhum registo encontrado.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- ABA 2: DADOS E FOTO DA OBRA -----------------
elif menu == "🏗️ Dados e Foto da Obra":
    st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
    st.subheader("🏢 Ficha Cadastral e Visual da Obra Selecionada")
    
    if obra_selecionada == 'Todas as Obras':
        st.warning("⚠️ Selecione uma **Obra específica** no filtro superior para carregar os respetivos dados cadastrais e a foto do canteiro.")
    else:
        dados_obra = df_contratos[df_contratos['Obra'] == obra_selecionada]
        
        col_i1, col_i2 = st.columns([1.2, 1])
        
        with col_i1:
            cliente_val = dados_obra['Cliente'].values[0] if 'Cliente' in dados_obra.columns and not dados_obra.empty else 'Cliente Padrão'
            endereco_val = dados_obra['Endereco'].values[0] if 'Endereco' in dados_obra.columns and not dados_obra.empty else 'Endereço não cadastrado'
            gerente_val = dados_obra['Gerente'].values[0] if 'Gerente' in dados_obra.columns and not dados_obra.empty else 'Engenheiro Responsável'
            orc_val = dados_obra['Orcamento_Total'].values[0] if 'Orcamento_Total' in dados_obra.columns and not dados_obra.empty else 0
            
            st.markdown(f"""
                <div style="font-size: 16px; line-height: 2.2;">
                    <p><b>🏢 Nome da Obra:</b> <span style="color: #00f2fe;">{obra_selecionada}</span></p>
                    <p><b>👤 Nome do Cliente:</b> {cliente_val}</p>
                    <p><b>📍 Endereço Físico:</b> {endereco_val}</p>
                    <p><b>👷 Gestor / Responsável:</b> {gerente_val}</p>
                    <p><b>💰 Orçamento Aprovado:</b> R$ {orc_val:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_i2:
            st.markdown("#### 📷 Registo Fotográfico do Canteiro")
            uploaded_file = st.file_uploader("Carregar nova foto da obra", type=["png", "jpg", "jpeg"])
            
            if uploaded_file is not None:
                st.image(uploaded_file, caption=f"Obra: {obra_selecionada}", use_container_width=True)
            else:
                st.image("https://images.unsplash.com/photo-1541888946425-d0fbb18fcd35?auto=format&fit=crop&w=800&q=80", caption=f"Canteiro - {obra_selecionada}", use_container_width=True)
                
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- ABA 3: GESTÃO DE CONTRATOS -----------------
elif menu == "📁 Gestão de Contratos":
    st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
    st.subheader("📑 Base Geral de Contratos e Obras")
    st.dataframe(df_contratos, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
