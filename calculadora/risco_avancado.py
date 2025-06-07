# calculadora/risco_avancado.py

from datetime import datetime

def calcular_risco_total(operacoes):
    """Soma o risco ($) de todas as operações salvas."""
    total_risco = sum(op["Risco ($)"] for op in operacoes)
    return round(total_risco, 2)

def contar_operacoes_por_ativo(operacoes, ativo):
    """Conta quantas operações existem para o mesmo ativo."""
    return sum(1 for op in operacoes if op["Ativo"].upper() == ativo.upper())

def gerar_alertas(operacoes, ativo, capital, limite_pct=5.0, limite_operacoes_ativo=3):
    """Gera alertas caso os limites de risco ou ativo sejam ultrapassados."""
    alertas = []
    risco_total = calcular_risco_total(operacoes)
    risco_pct = (risco_total / capital) * 100 if capital > 0 else 0

    if risco_pct > limite_pct:
        alertas.append(f"🚨 Risco acumulado do dia é {risco_pct:.2f}% (> {limite_pct}%) do capital!")

    qtd_ativo = contar_operacoes_por_ativo(operacoes, ativo)
    if qtd_ativo >= limite_operacoes_ativo:
        alertas.append(f"⚠️ Já existem {qtd_ativo} operações no ativo {ativo}.")

    return alertas
