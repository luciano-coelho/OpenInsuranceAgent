# scripts/call_ai_model.py

import os
import sys
from groq import Groq

def main():
    # 1. Obter a API Key e o Diff das variáveis de ambiente
    try:
        # Pega a chave do Secret do GitHub
        api_key = os.environ["AI_API_KEY"]
    except KeyError:
        print("Erro Crítico: A variável de ambiente AI_API_KEY não foi definida.")
        sys.exit(1)

    diff_content = os.environ.get("PR_DIFF", "")

    if not diff_content.strip():
        print("Diff vazio ou não fornecido. Nenhum código para analisar.")
        sys.exit(0) # Termina com sucesso, mas sem ação

    # 2. Montar o Prompt de Engenharia (dividido em System e User)
    
    # O 'system_prompt' define o papel da IA
    system_prompt = """
    Contexto: Você é um Engenheiro de Qualidade de Software (QA) Sênior e um especialista em testes unitários.
    
    Tarefa: Analise o 'git diff' de um Pull Request e forneça uma análise técnica focada em testes.
    
    Formato de Resposta:
    A resposta DEVE ser em Markdown e seguir esta estrutura:
    
    **Resumo da Mudança:**
    (Descreva brevemente a lógica principal que foi alterada ou adicionada.)
    
    **Pontos de Atenção e Riscos:**
    (Identifique lógicas complexas, potenciais 'breaking changes' ou código sem tratamento de erros.)
    
    **Sugestões de Testes Unitários:**
    (Liste casos de borda (edge cases) e cenários de teste que precisam ser cobertos. Se possível, sugira pseudocódigo para 2-3 testes.)
    """

    # O 'user_prompt' contém os dados específicos da tarefa
    user_prompt = f"""
    ---
    **Git Diff para Análise:**
    ```diff
    {diff_content}
    ```
    """

    # 3. Chamar a API do Groq
    try:
        client = Groq(api_key=api_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            # Usamos o Llama 3 de 8B, que é extremamente rápido no Groq e ótimo para esta tarefa
            model="llama3-8b-8192", 
        )
        
        # 4. Imprimir a resposta para o stdout
        # O GitHub Action irá capturar esta saída
        response_text = chat_completion.choices[0].message.content
        print(response_text)

    except Exception as e:
        print(f"Erro ao contatar a API do Groq: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()