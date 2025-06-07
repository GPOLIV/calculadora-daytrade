# Melhorias implementadas para atender aos requisitos do usuário.

import streamlit as st
import pandas as pd
import os
import io
from calculadora.calculadora import calcular_posicao
from calculadora.simulador import simular_risco_retorno
from calculadora.risco_avancado import gerar_alertas

st.set_page_config(page_title="Calculadora Day Trade", layout="centered")

if 'operacoes' not in st.session_state:
    st.session_state.operacoes = []

def salvar_csv(dados, caminho="dados/operacoes_salvas.csv"):
    try:
        df = pd.DataFrame(dados)
        df.to_csv(caminho, index=False)
    except Exception as e:
        st.error(f"Erro ao salvar CSV: {e}")

# === TÍTULO PRINCIPAL COM TAMANHO AJUSTADO ===
st.markdown("<h3>📊 Calculadora de Posição para Day Trade</h3>", unsafe_allow_html=True)
st.caption("💡 Otimizada para Forex, Criptomoedas e XAUUSD")

# === BARRA LATERAL DE CONFIGURAÇÃO ===
with st.sidebar:
    st.header("⚙️ Configurações da Operação")

    capital_total = st.number_input(
        "💰 Capital Total (USD)", 
        min_value=0.0, 
        value=1000.0, 
        help="Valor disponível na conta da corretora."
    )
    risco_pct = st.slider(
        "🎯 Risco por operação (%)", 
        0.1, 
        10.0, 
        1.0, 
        0.1, 
        help="Quanto você deseja arriscar do seu capital em %."
    )

    # === STOP LOSS COM EXPLICAÇÃO ===
    stop_loss = st.number_input(
        "🛑 Stop Loss (em pontos/pips — ex: 50 = 5.0 pips)", 
        min_value=0.1, 
        value=50.0, 
        help="Use pontos, e lembre-se: 10 pontos = 1 pip para muitos pares."
    )

    take_profit = st.number_input(
        "🎯 Take Profit (em pontos/pips)", 
        min_value=0.1, 
        value=100.0, 
        help="Distância alvo para lucro. 10 pontos = 1 pip."
    )
    ativo = st.text_input(
        "📈 Ativo (ex: EURUSD, BTCUSD, XAUUSD)", 
        value="XAUUSD"
    )

    modo_manual = st.checkbox("📝 Inserir lote manualmente?", value=False)

    # === VALOR AUTOMATIZADO POR ATIVO ===
    if modo_manual:
        lote_manual = st.number_input(
            "✍️ Lote manual", 
            min_value=0.01, 
            value=0.1, 
            step=0.01
        )
        if ativo[:3] == "XAU":
            valor_pip = 1.0 * lote_manual
        elif ativo[:3] == "BTC":
            valor_pip = 5.0 * lote_manual
        else:
            valor_pip = 10.0 * lote_manual
        st.info(f"💵 Valor estimado por pip: ${valor_pip:.2f}")
    else:
        # Definir valor automaticamente com base no ativo
        valor_pip = {
            "EURUSD": 10.0,
            "XAUUSD": 1.0,
            "BTCUSD": 5.0
        }.get(ativo.upper(), 10.0)
        st.number_input("💵 Valor por pip (USD)", value=valor_pip, disabled=True)


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
st.write(f"⚖️ Risco/Retorno: `1 para {simulacao['rr']:.2f}`")

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
    with st.expander("📁 Histórico de Operações"):
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
    with st.expander("📊 Relatório e Análise Avançada"):
        df = pd.DataFrame(st.session_state.operacoes)

        col1, col2 = st.columns(2)
        filtro_ativo = col1.selectbox("Filtrar por ativo", options=["Todos"] + sorted(df["Ativo"].unique().tolist()))
        filtro_rr = col2.slider("Filtrar por R/R mínimo", min_value=0.0, max_value=5.0, value=0.0, step=0.1)

        df_filtrado = df.copy()
        if filtro_ativo != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Ativo"] == filtro_ativo]
        df_filtrado = df_filtrado[df_filtrado["R/R"] >= filtro_rr]

        st.dataframe(df_filtrado)

        st.markdown("### 📈 Estatísticas Gerais")
        st.write(f"📌 Total de operações: {len(df_filtrado)}")
        st.write(f"💸 Risco médio: ${df_filtrado['Risco ($)'].mean():.2f}")
        st.write(f"🟢 Retorno médio: ${df_filtrado['Retorno ($)'].mean():.2f}")
        st.write(f"⚖️ R/R médio: {df_filtrado['R/R'].mean():.2f}")

        st.markdown("### 📊 Gráfico Risco vs Retorno")
        chart_data = df_filtrado[["Risco ($)", "Retorno ($)"]]
        st.bar_chart(chart_data)

        buffer = io.BytesIO()
        df_filtrado.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar relatório em Excel",
            data=buffer,
            file_name="relatorio_daytrade.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# === SANDBOX: SIMULAÇÃO COM CAPITAL VIRTUAL ===
st.markdown("---")
sandbox_expander = st.expander("🧪 Modo Sandbox – Simulação com Capital Virtual", expanded=True)
with sandbox_expander:
    st.header("🧪 Simulador de Trade com Capital Virtual")

    if 'sandbox_saldo' not in st.session_state:
        st.session_state.sandbox_saldo = 1000.0
        st.session_state.sandbox_historico = []

    capital_virtual = st.number_input("💼 Capital Inicial Virtual", min_value=100.0, value=st.session_state.sandbox_saldo,
                                      help="Você pode redefinir o valor inicial de simulação se quiser recomeçar.")

    if st.button("🔄 Redefinir Saldo"):
        st.session_state.sandbox_saldo = capital_virtual
        st.session_state.sandbox_historico = []
        st.success(f"Saldo virtual redefinido para ${capital_virtual:.2f}")

    st.markdown("### 🎯 Simular Trade")

    sandbox_direcao = st.selectbox("📊 Direção do trade", ["Compra", "Venda"])
    sandbox_resultado = st.selectbox("📈 Resultado da operação", ["Hit TP (Lucro)", "Hit SL (Prejuízo)"])

    if st.button("✅ Executar Simulação"):
        resultado = simular_risco_retorno(capital_virtual, lote, stop_loss, take_profit, valor_pip)
        ganho = resultado["retorno_total"] if sandbox_resultado == "Hit TP (Lucro)" else -resultado["risco_total"]
        st.session_state.sandbox_saldo += ganho

        nova_linha = {
            "Direção": sandbox_direcao,
            "Resultado": sandbox_resultado,
            "Lucro/Prejuízo": round(ganho, 2),
            "Saldo Atual": round(st.session_state.sandbox_saldo, 2)
        }

        st.session_state.sandbox_historico.append(nova_linha)
        st.success(f"Simulação registrada. Saldo atual: ${st.session_state.sandbox_saldo:.2f}")

    if st.session_state.sandbox_historico:
        st.markdown("### 📜 Histórico da Simulação")
        df_sandbox = pd.DataFrame(st.session_state.sandbox_historico)
        st.dataframe(df_sandbox)

        buffer = io.BytesIO()
        df_sandbox.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar histórico do Sandbox (Excel)",
            data=buffer,
            file_name="historico_sandbox.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
