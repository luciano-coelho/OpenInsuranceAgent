from langchain_core.prompts import PromptTemplate


class PromptTemplates:
    
    @staticmethod
    def get_concise_rag_prompt() -> PromptTemplate:

        return PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Você é um assistente especializado em Open Insurance Brasil.\n"
                "Contexto:\n{context}\n\n"
                "Pergunta: {question}\n\n"
                "Instruções: Responda em 2-3 frases curtas. Use apenas o contexto. Seja direto.\n"
                "Resposta:"
            ),
        )
    
    @staticmethod
    def get_detailed_rag_prompt() -> PromptTemplate:

        return PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Você é um assistente especializado em Open Insurance Brasil.\n"
                "Responda à pergunta de forma completa e fundamentada, usando APENAS as informações do contexto.\n"
                "Organize sua resposta de forma clara e estruturada quando apropriado.\n\n"
                "Contexto:\n{context}\n\n"
                "Pergunta: {question}\n\n"
                "Resposta detalhada:"
            ),
        )
    
    @staticmethod
    def get_bullet_points_prompt() -> PromptTemplate:

        return PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Você é um assistente especializado em Open Insurance Brasil.\n"
                "Contexto:\n{context}\n\n"
                "Pergunta: {question}\n\n"
                "Instruções: Responda com bullet points (•). Use apenas o contexto. Máximo 5 pontos.\n"
                "Resposta:"
            ),
        )
    
    @staticmethod
    def get_yes_no_prompt() -> PromptTemplate:

        return PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Você é um assistente especializado em Open Insurance Brasil.\n"
                "Contexto:\n{context}\n\n"
                "Pergunta: {question}\n\n"
                "Instruções: Responda 'Sim' ou 'Não' seguido de 1 frase explicativa usando o contexto.\n"
                "Resposta:"
            ),
        )
    
    @staticmethod
    def get_cli_prompt() -> PromptTemplate:

        return PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Você é um assistente especializado em Open Insurance Brasil.\n"
                "Contexto:\n{context}\n\n"
                "Pergunta: {question}\n\n"
                "Instruções: Responda em 2-3 frases curtas. Use apenas o contexto. Seja direto, mas, sem deixar de ser claro.\n"
                "Resposta:"
            ),
        )
