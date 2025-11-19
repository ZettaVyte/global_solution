from utils import data_loader as dl
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="RecomendaIAgro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E7D32;
        margin-bottom: 1rem;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    .action-button {
        background-color: #2E7D32;
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        border: none;
        width: 100%;
        margin-top: 0.5rem;
    }
    .section-title {
        color: #2E7D32;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2E7D32;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

@st.cache_data
def load_data():
    # Carregar dados reais
    clientes, historico, recomendacoes, produtos, rules = dl.load_real_data()
    
    # Enriquecer dados de clientes
    clientes = dl.enrich_customer_data(clientes)
    
    # Merge recomendações com produtos para ter descrição
    recomendacoes = recomendacoes.merge(
        produtos[['item_id', 'item_desc', 'item_class']], 
        left_on='rec_id', 
        right_on='item_id', 
        how='left'
    )
    
    return clientes, historico, recomendacoes, rules

def calcular_abc(historico):
    """Calcula curva ABC de categorias"""
    abc = historico.groupby('categoria')['valor'].sum().sort_values(ascending=False)
    abc_percent = (abc / abc.sum() * 100).cumsum()
    
    curva = []
    for idx, val in enumerate(abc_percent):
        if val <= 80:
            curva.append('A')
        elif val <= 95:
            curva.append('B')
        else:
            curva.append('C')
    
    return pd.DataFrame({
        'categoria': abc.index,
        'valor': abc.values,
        'curva': curva
    })

# =============================================================================
# CARREGAMENTO DOS DADOS
# =============================================================================

clientes_df, historico_df, recomendacoes_df, rules_df = load_data()

# =============================================================================
# SIDEBAR - SELEÇÃO DE CLIENTE
# =============================================================================

st.sidebar.image("placeholder_RecomendaIAgro.jpg", use_column_width=True)

st.sidebar.markdown("### 🎯 Selecione o Cliente")
cliente_selecionado = st.sidebar.selectbox(
    "Cliente:",
    clientes_df['user_id'].tolist(),
    format_func=lambda x: clientes_df[clientes_df['user_id'] == x]['nome'].values[0]
)

# Filtrar dados do cliente selecionado

cliente = clientes_df[clientes_df['user_id'] == cliente_selecionado].iloc[0]
historico_cliente = dl.prepare_historico(historico_df, cliente_selecionado, meses=6)
recs_cliente = dl.prepare_recommendations(
    recomendacoes_df, 
    rules_df,
    cliente_selecionado, 
    top_n=3
)
metrics = dl.calculate_commercial_metrics(historico_cliente)
recs_cliente.drop_duplicates(subset=['item_desc'], inplace=True)
recs_cliente.sort_values(by='lift', ascending=False, inplace=True)

# Métricas sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Resumo Rápido")
st.sidebar.metric("Ticket Médio", f"R$ {metrics['ticket_medio']:,.2f}")
st.sidebar.metric("Compras (6 meses)", len(historico_cliente))
st.sidebar.metric("Total Investido", f"R$ {historico_cliente['valor'].sum():,.2f}")

# =============================================================================
# HEADER PRINCIPAL
# =============================================================================

st.markdown('<div class="main-header">🌾 RecomendaIAgro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">IA que fortalece a comunicação humana no agronegócio</div>', unsafe_allow_html=True)

# =============================================================================
# SEÇÃO 1: INFORMAÇÕES DO CLIENTE
# =============================================================================

st.markdown('<div class="section-title">👤 Informações do Cliente</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h2 style='color: #2E7D32; margin-bottom: 0.5rem;'>{cliente['nome']}</h2>
        <p style='font-size: 1.1rem; color: #333; margin: 0.3rem 0;'><strong>{cliente['responsavel']}</strong></p>
        <p style='color: #666; margin: 0.3rem 0;'>{cliente['documento']} - CNPJ</p>
        <p style='color: #666; margin: 0.3rem 0;'>📍 {cliente['cidade']}, {cliente['uf']} - {cliente['regiao']}</p>
        <p style='color: #666; margin: 0.5rem 0;'>🌱 <strong>Culturas:</strong> {cliente['culturas']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p style='margin: 0.5rem 0;'><strong>📞 Contatos</strong></p>
        <p style='color: #666; margin: 0.3rem 0;'>{cliente['telefone']}</p>
        <p style='color: #666; margin: 0.3rem 0;'>{cliente['email']}</p>
        <p style='margin: 1rem 0 0.5rem 0;'><strong>🏆 Classificação</strong></p>
        <span class="info-badge">{cliente['cluster']} Cliente</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Badge de classificação grande
    cluster_colors = {'DIAMOND': '#9C27B0', 'GOLD': '#FFD700', 'SILVER': '#C0C0C0'}
    cluster_color = cluster_colors.get(cliente['cluster'], '#4CAF50')
    
    st.markdown(f"""
    <div style='background-color: {cluster_color}; color: white; padding: 2rem; 
                border-radius: 15px; text-align: center; height: 100%;
                display: flex; flex-direction: column; justify-content: center;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>💎</div>
        <div style='font-size: 1.5rem; font-weight: bold;'>{cliente['cluster']}</div>
        <div style='font-size: 0.9rem; margin-top: 0.3rem;'>Cliente Premium</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SEÇÃO 2: PERFIL COMERCIAL
# =============================================================================

st.markdown('<div class="section-title">💼 Perfil Comercial</div>', unsafe_allow_html=True)

# Calcular métricas
ticket_medio = historico_cliente['valor'].mean()
frequencia = len(historico_cliente)
valor_total = historico_cliente['valor'].sum()
categoria_top = historico_cliente.groupby('categoria')['valor'].sum().idxmax()

# Métricas em cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Valor Potencial", f"R$ {valor_total:,.2f}", 
             delta=f"+{(valor_total/6)*12:,.0f} anual")

with col2:
    st.metric("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}")

with col3:
    st.metric("📊 Frequência", f"{frequencia} compras", 
             delta="Últimos 6 meses")

with col4:
    st.metric("⭐ Categoria Top", categoria_top)

# Gráficos
col1, col2 = st.columns(2)

with col1:
    # Evolução de compras
    df_evolucao = historico_cliente.groupby('data')['valor'].sum().reset_index()
    
    fig_evolucao = px.line(
        df_evolucao,
        x='data', 
        y='valor',
        title='📈 Evolução de Compras (6 meses)',
        labels={'valor': 'Valor (R$)', 'data': 'Mês'}
    )
    fig_evolucao.update_traces(line_color='#2E7D32', line_width=3)
    fig_evolucao.update_layout(height=300)
    st.plotly_chart(fig_evolucao, use_container_width=True)

with col2:
    # Curva ABC
    abc_df = calcular_abc(historico_cliente)
    fig_abc = px.bar(
        abc_df,
        x='categoria',
        y='valor',
        color='curva',
        title='📊 Curva ABC - Categorias',
        labels={'valor': 'Valor (R$)', 'categoria': 'Categoria'},
        color_discrete_map={'A': '#2E7D32', 'B': '#FFA726', 'C': '#EF5350'}
    )
    fig_abc.update_layout(height=300)
    st.plotly_chart(fig_abc, use_container_width=True)

# =============================================================================
# SEÇÃO 3: COMPORTAMENTO AGRONÔMICO
# =============================================================================

st.markdown('<div class="section-title">🌾 Comportamento Agronômico</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style='color: #2E7D32; font-size: 1rem; margin-bottom: 0.5rem;'>🗺️ Área Total</h3>
        <p style='font-size: 1.8rem; font-weight: bold; color: #333; margin: 0;'>{cliente['area_total']:,}</p>
        <p style='color: #666; font-size: 0.9rem;'>hectares</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style='color: #2E7D32; font-size: 1rem; margin-bottom: 0.5rem;'>🌍 Tipo de Solo</h3>
        <p style='font-size: 1.2rem; font-weight: bold; color: #333; margin: 0;'>{cliente['tipo_solo']}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style='color: #2E7D32; font-size: 1rem; margin-bottom: 0.5rem;'>🐛 Pragas Comuns</h3>
        <p style='font-size: 1.2rem; font-weight: bold; color: #333; margin: 0;'>{cliente['praga_comum']}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style='color: #2E7D32; font-size: 1rem; margin-bottom: 0.5rem;'>📅 Safra Principal</h3>
        <p style='font-size: 1.2rem; font-weight: bold; color: #333; margin: 0;'>{cliente['safra_principal']}</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SEÇÃO 4: RECOMENDAÇÕES DA IA ⭐
# =============================================================================

st.markdown('<div class="section-title">🤖 Recomendações da IA (Algoritmo Apriori)</div>', unsafe_allow_html=True)

st.markdown("""
<div style='background-color: #E8F5E9; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem;'>
    <p style='color: #2E7D32; margin: 0;'>
        <strong>💡 Insight:</strong> Produtos com alta correlação de compra identificados pelo algoritmo Apriori. 
        O <strong>Lift</strong> indica quantas vezes mais provável o cliente comprará o produto recomendado.
    </p>
</div>
""", unsafe_allow_html=True)

for idx, rec in recs_cliente.iterrows():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="recommendation-card">
            <div style='display: flex; justify-content: space-between; align-items: start;'>
                <div style='flex: 1;'>
                    <h3 style='margin: 0 0 0.5rem 0; font-size: 1.5rem;'>🎯 {rec['rec_desc']}</h3>
                    <p style='margin: 0 0 0.5rem 0; opacity: 0.9;'><strong>{rec['item_class']}</strong></p>
                    <p style='margin: 0; font-size: 0.95rem; line-height: 1.5;'>{rec['razao']}</p>
                </div>
                <div style='text-align: right; margin-left: 1rem;'>
                    <div style='background-color: rgba(255,255,255,0.3); padding: 0.8rem; border-radius: 10px;'>
                        <div style='font-size: 2rem; font-weight: bold;'>{round(rec['lift'],2)}x</div>
                        <div style='font-size: 0.8rem; opacity: 0.9;'>Lift Score</div>
                    </div>
                </div>
            </div>
            <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.3);'>
                <small> 🎲 Baseado em padrões de {int(rec['confianca']*1000)} clientes similares</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button(f"📋 Ver Detalhes", key=f"btn_{idx}"):
            st.info(f"Abrindo ficha técnica de {rec['rec_desc']}...")

# =============================================================================
# SEÇÃO 5: HISTÓRICO DETALHADO
# =============================================================================

with st.expander("📜 Ver Histórico Completo de Compras", expanded=False):
    st.dataframe(
        historico_cliente[['data', 'item_desc', 'categoria', 'valor']].rename(columns={
            'data': 'Data',
            'item_desc': 'Produto',
            'categoria': 'Categoria',
            'valor': 'Valor (R$)'
        }),
        use_container_width=True,
        hide_index=True
    )

# =============================================================================
# SEÇÃO 6: PRÓXIMAS AÇÕES
# =============================================================================

st.markdown('<div class="section-title">🎯 Próximas Ações</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📞 Ligar Agora", use_container_width=True):
        st.success(f"📞 Discando para {cliente['telefone']}...")
        st.balloons()

with col2:
    if st.button("💬 WhatsApp", use_container_width=True):
        st.success(f"💬 Abrindo WhatsApp para {cliente['telefone']}...")
        st.info("Mensagem sugerida: Olá! Identificamos produtos que podem otimizar sua safra. Posso apresentar?")

with col3:
    if st.button("📅 Agendar Visita", use_container_width=True):
        st.success("📅 Abrindo agenda...")
        
        # Mini formulário de agendamento
        with st.form("agendar_visita"):
            data_visita = st.date_input("Data da visita")
            hora_visita = st.time_input("Horário")
            observacoes = st.text_area("Observações", placeholder="Motivo da visita, tópicos a discutir...")
            
            submitted = st.form_submit_button("✅ Confirmar Agendamento")
            if submitted:
                st.success(f"✅ Visita agendada para {data_visita} às {hora_visita}!")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>RecomendaIAgro</strong> - IA que fortalece a comunicação humana no agronegócio</p>
    <p style='font-size: 0.9rem;'>Powered by Machine Learning | Algoritmo Apriori | Versão 1.0</p>
</div>
""", unsafe_allow_html=True)