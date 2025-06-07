# app.py

import streamlit as st
import pandas as pd
import os
import io
from calculadora.calculadora import calcular_posicao
from calculadora.simulador import simular_risco_retorno
from calculadora.risco_avancado import gerar_alertas

# === CONFIG INICIAL ===
st.set_page_config(page_title="Calculadora Day Trade", layout="centered")

if 'operacoes' not in st.session_state:
    st.session_state.operacoes = []

# === FUNÇÃO AUXILIAR PARA SALVAR CSV ===
def salvar_csv(dados, caminho="dados/operacoes_salvas.csv"):
    try:
        df = pd.DataFrame(dados)
        df.to_csv(caminho, index=False)
    except Exception as e:
        st.error(f"Erro ao salvar CSV: {e}")

# === TÍTULO PRINCIPAL ===
st.title("📊 Calculadora de Posição para Day Trade")
st.caption("💡 Otimizada para Forex, Criptomoedas e XAUUSD")

# === BARRA LATERAL DE CONFIGURAÇÃO ===
with st.sidebar:
    st.header("⚙️ Configurações da Operação")

    capital_total = st.number_input("💰 Capital Total (USD)", min_value=0.0, value=1000.0, help="Valor disponível na conta da corretora.")
    risco_pct = st.slider("🎯 Risco por operação (%)", 0.1, 10.0, 1.0, 0.1, help="Quanto você deseja arriscar do seu capital em %.")
    stop_loss = st.number_input("🛑 Stop Loss (em pips/pontos)", min_value=0.1, value=50.0, help="Distância do preço até o stop.")
    take_profit = st.number_input("🎯 Take Profit (em pips/pontos)", min_value=0.1, value=100.0, help="Distância alvo para lucro.")
    ativo = st.text_input("📈 Ativo (ex: EURUSD, BTCUSD, XAUUSD)", value="XAUUSD")

    modo_manual = st.checkbox("📝 Inserir lote manualmente?", value=False)

    if modo_manual:
        lote_manual = st.number_input("✍️ Lote manual", min_value=0.01, value=0.1, step=0.01)
        if ativo[:3] == "XAU":
            valor_pip = 1.0 * lote_manual
        elif ativo[:3] == "BTC":
            valor_pip = 5.0 * lote_manual
        else:
            valor_pip = 10.0 * lote_manual
        st.info(f"💵 Valor estimado por pip: ${valor_pip:.2f}")
    else:
        valor_pip = st.number_input("💵 Valor por pip (USD)", min_value=0.01, value=0.10)

# === CÁLCULOS ===
st.subheader("📌 Resultado da Operação")

risco_valor = capital_total * (risco_pct / 100)

if not modo_manual:
    resultado = calcular_posicao(capital_total, risco_pct, stop_loss, valor_pip)
    lote = resultado["lote"]
    risco_valor = resultado["risco_financeiro"]
else:
    lote = lote_manual

simulacao = simular_risco_retorno(capital_total, lote, stop_loss, take_profit, valor_pip)

st.write(f"🔢 Lote recomendado: `{lote:.2f}`")

if lote > 1:
    st.warning("⚠️ Lote acima de 1.0 pode ser arriscado para contas pequenas!")

st.write(f"💸 Risco estimado: `${risco_valor:.2f}`")
st.write(f"🟢 Retorno esperado: `${simulacao['retorno_total']:.2f}`")
st.write(f"⚖️ Relação R/R: `{simulacao['rr']} : 1`")

# === BOTÃO SALVAR ===
if st.button("💾 Salvar operação"):
    nova_op = {
        "Ativo": ativo,
        "Lote": round(lote, 2),
        "Risco ($)": round(risco_valor, 2),
        "Retorno ($)": round(simulacao["retorno_total"], 2),
        "R/R": simulacao["rr"]
    }
    st.session_state.operacoes.append(nova_op)
    salvar_csv(st.session_state.operacoes)
    st.success("✅ Operação salva com sucesso!")
    
    alertas = gerar_alertas(st.session_state.operacoes, ativo, capital_total)

    if alertas:
        st.warning("⚠️ Alertas de risco detectados:")
        for alerta in alertas:
            st.write(alerta)

# === HISTÓRICO DE OPERAÇÕES ===
if st.session_state.operacoes:
    st.subheader("📁 Histórico de Operações")
    df_ops = pd.DataFrame(st.session_state.operacoes)
    st.dataframe(df_ops)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Exportar CSV"):
            salvar_csv(st.session_state.operacoes)
            st.success("Exportado para dados/operacoes_salvas.csv")

    with col2:
        if st.button("🗑️ Limpar histórico"):
            st.session_state.operacoes = []
            if os.path.exists("dados/operacoes_salvas.csv"):
                os.remove("dados/operacoes_salvas.csv")
            st.warning("Histórico apagado!")

# === RELATÓRIO AVANÇADO ===
if st.session_state.operacoes:
    st.subheader("📊 Relatório e Análise Avançada")

    df = pd.DataFrame(st.session_state.operacoes)

    # Filtros
    col1, col2 = st.columns(2)
    filtro_ativo = col1.selectbox("Filtrar por ativo", options=["Todos"] + sorted(df["Ativo"].unique().tolist()))
    filtro_rr = col2.slider("Filtrar por R/R mínimo", min_value=0.0, max_value=5.0, value=0.0, step=0.1)

    df_filtrado = df.copy()
    if filtro_ativo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Ativo"] == filtro_ativo]
    df_filtrado = df_filtrado[df_filtrado["R/R"] >= filtro_rr]

    st.dataframe(df_filtrado)

    # Estatísticas básicas
    st.markdown("### 📈 Estatísticas Gerais")
    st.write(f"📌 Total de operações: {len(df_filtrado)}")
    st.write(f"💸 Risco médio: ${df_filtrado['Risco ($)'].mean():.2f}")
    st.write(f"🟢 Retorno médio: ${df_filtrado['Retorno ($)'].mean():.2f}")
    st.write(f"⚖️ R/R médio: {df_filtrado['R/R'].mean():.2f}")

    # Gráfico de barras
    st.markdown("### 📊 Gráfico Risco vs Retorno")
    chart_data = df_filtrado[["Risco ($)", "Retorno ($)"]]
    st.bar_chart(chart_data)

    # Exportar CSV novamente, se desejar
    buffer = io.BytesIO()
    df_filtrado.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="⬇️ Baixar relatório em Excel",
        data=buffer,
        file_name="relatorio_daytrade.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )