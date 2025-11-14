import os
import sys
from groq import Groq

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
        
        persona_key = sys.argv[1]
        
    except KeyError:
        print("Erro Crítico: AI_API_KEY ou PR_DIFF não definidos.")
        sys.exit(1)
    except IndexError:
        print("Erro Crítico: Nenhuma 'persona' (ex: linter, logic) foi fornecida ao script.")
        sys.exit(1)

    if not diff_content.strip():
        print("Diff vazio.")
        sys.exit(0)

    # Seleciona o prompt de sistema correto
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
            model="llama-3.3-70b-versatile", 
        )
        response_text = chat_completion.choices[0].message.content
        print(response_text)

    except Exception as e:
        print(f"Erro ao contatar a API do Groq: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()