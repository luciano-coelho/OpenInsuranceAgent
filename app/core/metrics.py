from prometheus_client import Histogram, Counter

LATENCY = Histogram("oi_agent_latency_seconds", "Tempo de resposta do agente")
FALLBACKS = Counter("oi_agent_fallback_total", "Respostas com fallback")

def observe_latency(seconds: float):
    LATENCY.observe(seconds)

def count_fallbacks(answer: str):
    text = (answer or "").lower()
    if "não há informações suficientes" in text or "não tenho essa informação" in text:
        FALLBACKS.inc()
