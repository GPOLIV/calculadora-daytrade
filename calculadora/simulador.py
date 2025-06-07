# simulador.py

def simular_risco_retorno(capital, lote, stop_pontos, tp_pontos, valor_ponto):
    """
    Simula risco/retorno com base no SL/TP.
    """
    try:
        risco = lote * stop_pontos * valor_ponto
        retorno = lote * tp_pontos * valor_ponto
        rr = retorno / risco if risco != 0 else 0

        return {
            "risco_total": round(risco, 2),
            "retorno_total": round(retorno, 2),
            "rr": round(rr, 2)
        }

    except Exception as e:
        print(f"[DEBUG] Erro na simulação de risco/retorno: {e}")
        return {
            "risco_total": 0,
            "retorno_total": 0,
            "rr": 0
        }
