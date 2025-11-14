from prometheus_client import Histogram, Counter

# Prometheus metrics
LATENCY = Histogram("oi_agent_latency_seconds", "Agent response time in seconds")
FALLBACKS = Counter("oi_agent_fallback_total", "Total responses that used a fallback")


def observe_latency(seconds: float) -> None:
    """Record a latency observation in seconds."""
    LATENCY.observe(seconds)


def count_fallbacks(answer: str) -> None:
    """Increment fallback counter when the answer indicates a fallback response."""
    text = (answer or "").lower()
    if "não há informações suficientes" in text or "não tenho essa informação" in text:
        FALLBACKS.inc()
