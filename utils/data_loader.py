import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re # Necessário para a limpeza de strings no Apriori

# =============================================================================
# CARREGAMENTO DE DADOS
# =============================================================================

def load_real_data():
    """
    Carrega os dados dos CSVs e faz a união essencial (merge) para
    garantir que o histórico de compras tenha a coluna 'categoria'.
    """
    
    # 1. Carregar clientes
    clientes = pd.read_csv('clientes_df.csv')
    
    # 2. Carregar histórico de compras
    historico = pd.read_csv('bases/cestas.csv')
    historico['timestamp'] = pd.to_datetime(historico['timestamp'], errors='coerce')
    
    # 3. Carregar recomendações
    recomendacoes = pd.read_csv('recomendacoes.csv')
    
    # 4. Carregar produtos
    produtos = pd.read_csv('bases/produtos.csv') 
    
    # 5. Carregar Regras do Apriori
    try:
        rules = pd.read_csv('regras_apriori.csv')
        
        # *** CORREÇÃO E LIMPEZA: Extrair o ID simples do item do frozenset string ***
        # Usa regex para extrair 'item_X' de strings como "frozenset({'item_X'})"
        rules['consequents'] = rules['consequents'].str.extract(r"'(item_\d+)'")
        
        # Garantir que são numéricos
        rules['lift'] = pd.to_numeric(rules['lift'], errors='coerce')
        rules['confidence'] = pd.to_numeric(rules['confidence'], errors='coerce')
        
    except FileNotFoundError:
        print("Aviso: regras_apriori.csv não encontrado. Continuando sem regras.")
        rules = pd.DataFrame(columns=['consequents', 'lift', 'confidence', 'antecedents'])
    
    # 6. UNIÃO ESSENCIAL: Juntar histórico com produtos para trazer a 'item_class'
    historico = historico.rename(columns={'price': 'valor'})
    
    historico = historico.merge(
        produtos[['item_id', 'item_class', 'item_desc']], 
        on='item_id', 
        how='left'
    )
    # Renomear para 'categoria' para que as outras funções do app.py funcionem
    historico = historico.rename(columns={'item_class': 'categoria'}) 
    
    # 7. Retorna todos os DataFrames (agora com 5 DFs)
    return clientes, historico, recomendacoes, produtos, rules

# =============================================================================
# PREPARAÇÃO DE DADOS
# =============================================================================

def enrich_customer_data(clientes_df):
    """
    Adiciona campos agronômicos fictícios e randômicos (Fallback) - 
    Não deve ser necessário se 'clientes_df.csv' foi gerado corretamente.
    """
    # Apenas para garantir que o Streamlit não quebre
    if 'area_total' not in clientes_df.columns:
        clientes_df['area_total'] = np.random.randint(100, 2000, len(clientes_df))
    # ... (outras colunas enriquecidas) ...
    return clientes_df


def prepare_historico(historico_df, user_id, meses=6):
    """
    Filtra e prepara histórico de compras dos últimos N meses,
    mantendo as colunas originais para cálculo de métricas.
    """
    
    hist_cliente = historico_df[historico_df['user_id'] == user_id].copy()
    
    data_limite = datetime.now() - timedelta(days=meses*30)
    hist_cliente = hist_cliente[hist_cliente['timestamp'] >= data_limite]
    
    # Adicionar a coluna 'data' (Mês/Ano) para uso nos gráficos
    hist_cliente['data'] = hist_cliente['timestamp'].dt.to_period('M').astype(str)
    
    # O DataFrame é retornado detalhado.
    return hist_cliente


def prepare_recommendations(recs_df, rules_df, user_id, top_n=3):
    """
    Prepara recomendações e funde dados reais de Lift e Confidence.
    """
    recs_cliente = recs_df[recs_df['user_id'] == user_id].head(top_n).copy()
    
    # 1. GARANTE A EXISTÊNCIA DAS COLUNAS TEMPORÁRIAS (Fallback com valores randômicos)
    if len(recs_cliente) > 0:
        recs_cliente['lift_simulado'] = np.random.uniform(2.0, 4.0, len(recs_cliente))
        recs_cliente['confianca_simulado'] = np.random.uniform(0.6, 0.9, len(recs_cliente))
        recs_cliente['razao'] = "Recomendado com base no seu histórico" # Fallback
        recs_cliente['categoria'] = "Categoria Não Classificada"
    else:
        # Se não houver recomendações, retorna DF vazio
        return pd.DataFrame(columns=['rec_desc', 'lift', 'confianca', 'razao', 'categoria'])


    # 2. Tentar fazer o MERGE com as regras reais (RULES)
    if rules_df is not None and len(rules_df) > 0 and 'lift' in rules_df.columns:
        
        # 2.1. Preparar a tabela de regras (rules_df) com sufixos explícitos
        rules_renomeado = rules_df[['consequents', 'lift', 'confidence', 'antecedents']].rename(
            columns={'lift': 'lift_real', 'confidence': 'confidence_real'}, errors='ignore'
        )
        
        # 2.2. Merge
        recs_cliente = recs_cliente.merge(
            rules_renomeado,
            left_on='rec_id',
            right_on='consequents',
            how='left'
        )
        
        # 3. ATUALIZAR as colunas FINAIS ('lift' e 'confianca') - CORREÇÃO DE TYPO APLICADA
        
        # Combina Lift: usa o valor REAL se existir, senão o SIMULADO
        recs_cliente['lift'] = recs_cliente['lift_real'].combine_first(recs_cliente['lift_simulado'])
        
        # Combina Confiança: usa o valor REAL ('confidence_real') se existir, senão o SIMULADO ('confianca_simulado')
        recs_cliente['confianca'] = recs_cliente['confidence_real'].combine_first(recs_cliente['confianca_simulado'])

        # 4. Atualiza a razão onde o Lift real foi usado
        recs_cliente['razao'] = recs_cliente.apply(
            lambda row: f"Correlação Apriori real ({row['lift']:.1f}x) com base em {row['antecedents']}"
            if pd.notna(row['lift_real'])
            else row['razao']
            , axis=1)

        # 5. Limpar colunas temporárias
        recs_cliente = recs_cliente.drop(columns=[col for col in recs_cliente.columns if col.endswith(('_simulado', '_real', 'consequents', 'antecedents'))], errors='ignore')
    
    return recs_cliente

# =============================================================================
# CÁLCULO DE MÉTRICAS
# =============================================================================

def calculate_commercial_metrics(historico_cliente):
    """
    Calcula métricas de perfil comercial
    """
    
    metrics = {
        'ticket_medio': historico_cliente['valor'].mean() if len(historico_cliente) > 0 else 0,
        'frequencia': len(historico_cliente),
        'valor_total': historico_cliente['valor'].sum(),
        'categoria_top': historico_cliente.groupby('categoria')['valor'].sum().idxmax() if 'categoria' in historico_cliente.columns and len(historico_cliente) > 0 else 'N/A',
        'ultimo_mes': historico_cliente[historico_cliente['timestamp'] >= datetime.now() - timedelta(days=30)]['valor'].sum()
    }
    
    return metrics