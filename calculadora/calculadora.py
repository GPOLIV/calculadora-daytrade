# calculadora.py

def calcular_posicao(capital, risco_percentual, stop_pontos, valor_ponto):
    """
    Calcula o tamanho de lote fracionado com base no risco.
    Específico para Forex, Criptomoedas e XAUUSD.
    """
    try:
        if stop_pontos == 0 or valor_ponto == 0:
            raise ValueError("Stop ou valor do ponto não pode ser zero.")

        risco_reais = capital * (risco_percentual / 100)
        lote = risco_reais / (stop_pontos * valor_ponto)
        lote = round(lote, 2)

        return {
            "lote": lote,
            "risco_financeiro": round(lote * stop_pontos * valor_ponto, 2)
        }

    except Exception as e:
        print(f"[DEBUG] Erro no cálculo da posição: {e}")
        return {
            "lote": 0,
            "risco_financeiro": 0
        }
