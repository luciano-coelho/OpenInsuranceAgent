import os
import sys
from groq import Groq

# Groq model (updated; previous model deprecated)
MODEL_NAME = "llama-3.3-70b-versatile"

# Prompt adicional para modo "audit" (sem persona explícita)
AUDIT_PROMPT = """
Contexto: Você é um Engenheiro de Qualidade Sênior realizando uma auditoria técnica de um Pull Request.
Objetivo: Gerar uma análise clara e bem formatada em Markdown, com seções delimitadas.

INSTRUÇÕES DE FORMATAÇÃO (STRICT):
1. Use exatamente estas seções nesta ordem:
    ### Resumo
    ### Riscos
    ### Recomendações
2. Em "Resumo": 1–3 frases objetivas sobre a mudança.
3. Em "Riscos": lista numerada (1., 2., 3.) de possíveis fragilidades ou pontos de atenção. Se não houver, escreva "Nenhum risco relevante identificado.".
4. Em "Recomendações":
    - Cada item deve iniciar com "- [R#]" onde # é contador iniciando em 1.
    - Agrupe por tema se aplicável usando subcabeçalhos em negrito (**Validação**, **Erro**, etc.).
    - Seja específico: indique função/linha se possível.
5. NÃO repita conteúdo entre seções.
6. Linguagem: Português claro, evitar jargões excessivos.
7. Nunca inclua código completo repetido; apenas trechos relevantes inline entre crases.
"""

PROMPT_PERSONAS = {
    "linter": """
    Contexto: Você é um Engenheiro de Software Sênior focado em padrões de código.
    Tarefa: Analise o diff e verifique a aderência a padrões.
    Regras:
    1.  Idioma: TODO o código, comentários, e nomes de variáveis devem estar em Inglês.
    2.  Padrão: O código segue as convenções do PEP 8.
    Formato: Responda APENAS com as violações, linha por linha, ou "Nenhuma violação de padrão encontrada."
    """,
    
    "logic": """
    Contexto: Você é um Arquiteto de Software Sênior. Ignore estilo.
    Tarefa: Encontrar fragilidades lógicas e bugs em potencial.
    Procure por:
    1.  Casos de Borda (Edge Cases) Não Tratados (null, listas vazias, negativos).
    2.  Lógica complexa que pode ser simplificada.
    Formato: Responda com um resumo dos riscos lógicos.
    """,
    
    "security": """
    Contexto: Você é um Analista de SecOps.
    Tarefa: Encontrar vulnerabilidades e dados sensíveis.
    Procure por:
    1.  Vazamento de PII (CPF, E-mail, etc.).
    2.  Vulnerabilidades comuns (SQL Injection, XSS, Hardcoding de Paths).
    Formato: Responda APENAS com as falhas de segurança. Se nada for encontrado, responda "Nenhuma vulnerabilidade detectada."
    """
}

def main():
    try:
        api_key = os.environ["AI_API_KEY"]
        diff_content = os.environ["PR_DIFF"]
        persona_key = sys.argv[1] if len(sys.argv) > 1 else "audit"
    except KeyError:
        print("Erro Crítico: AI_API_KEY ou PR_DIFF não definidos.")
        sys.exit(1)

    if not diff_content.strip():
        print("Diff vazio.")
        sys.exit(0)

    # Seleciona o prompt de sistema correto (fallback para AUDIT_PROMPT)
    if persona_key == "audit":
        system_prompt = AUDIT_PROMPT
    else:
        system_prompt = PROMPT_PERSONAS.get(persona_key)
        if not system_prompt:
            print(f"Erro: Persona '{persona_key}' desconhecida.")
            sys.exit(1)

    user_prompt = f"--- Git Diff para Análise ---\n```diff\n{diff_content}\n```"

    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # Modelo atualizado (o anterior foi descontinuado)
            model=MODEL_NAME,
        )
        response_text = chat_completion.choices[0].message.content
        print(response_text)

    except Exception as e:
        print(f"Erro ao contatar a API do Groq: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()