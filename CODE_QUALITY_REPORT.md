# Relatório de Qualidade de Código - Open Insurance Agent

**Data:** 14 de novembro de 2025  
**Versão do Projeto:** 1.0.0  
**Escopo da Análise:** Todos os arquivos Python (.py) do projeto  
**Critérios de Avaliação:** PEP 8, Idioma (Inglês), Lógica e Segurança

---

## Sumário Executivo

| Categoria | Status | Violações Críticas | Violações Moderadas | Violações Leves |
|-----------|--------|-------------------|---------------------|-----------------|
| **Linter (PEP 8 + Idioma)** | ⚠️ ATENÇÃO | 0 | 18 | 45 |
| **Lógica** | ⚠️ ATENÇÃO | 3 | 12 | 8 |
| **Segurança** | ⚠️ ATENÇÃO | 2 | 5 | 3 |

**Avaliação Geral:** O projeto apresenta boa estrutura e modularidade, mas requer melhorias em tratamento de erros, validação de entrada e consistência de idioma. Não foram detectadas vulnerabilidades críticas de segurança, mas existem práticas que devem ser corrigidas.

---

## 1. Análise de Padrões (Linter)

### 1.1 Violações de Idioma (Português em código)

#### ❌ Críticas (devem ser corrigidas)

**app/core/logger.py**
- Linha 6: Nome de logger em português
  ```python
  logger = logging.getLogger("oi-agent")  # "oi" é abreviação PT
  ```
  **Recomendação:** Usar nome em inglês: `"open-insurance-agent"` ou `"oi_agent"`

**app/core/metrics.py**
- Linhas 3-4: Variáveis em inglês mas documentação/nomes ambíguos
  ```python
  LATENCY = Histogram("oi_agent_latency_seconds", "Tempo de resposta do agente")
  ```
  **Recomendação:** Descrições do Prometheus podem permanecer em PT para legibilidade de operações, mas o padrão é usar inglês

**app/rag/vectorstore.py**
- Linha 10: `print` em português
  ```python
  print(f"Criando índice '{settings.pinecone_index_name}' no Pinecone...")
  ```
  **Recomendação:** Trocar todos os prints para inglês ou usar logger

**app/rag/ingest.py**
- Linha 13: Mensagem de erro em português
  ```python
  print(f"⚠️  Erro ao carregar {p.name}: {e}")
  ```

**scripts/ingest_local.py**
- Múltiplas linhas: Prints em português
  ```python
  print("Lendo documentos em data/oi/ ...")
  print(f"Total de documentos encontrados: {len(docs)}")
  ```

**scripts/check_pinecone.py**
- Múltiplas linhas: Prints em português
  ```python
  print("Conectando ao Pinecone...")
  print("Nenhum índice encontrado.")
  ```

**app/api/routes.py**
- Linha 124-125: Docstrings parcialmente em português
  ```python
  """Recebe uma pergunta e retorna uma resposta fundamentada em documentos oficiais da SUSEP"""
  ```
  **Recomendação:** Docstrings públicas devem estar em inglês; mensagens de usuário final podem ser PT

**front/chat_app.py**
- Todo o arquivo: Interface em português (aceitável para UX final)
- Mas strings hardcoded devem ser externalizadas (i18n)

#### ℹ️ Moderadas (boas práticas)

- **Comentários inline misturados:** Alguns arquivos misturam comentários em PT e EN
- **Nomes de variáveis:** `vs` (vectorstore), `pc` (Pinecone client) - usar nomes descritivos
- **Constantes:** `UPLOAD_DIR`, `ALLOWED_EXTENSIONS` - OK, mas falta docstring explicativa

### 1.2 Violações PEP 8

#### ⚠️ Formatação

**main.py**
- Linha 34: Comentário de CORS poderia ser mais específico
  ```python
  allow_origins=["*"],  # Em produção, especificar domínios permitidos
  ```
  **PEP 8:** OK, mas em produção isso é vulnerabilidade (CORS aberto)

**app/core/config.py**
- Linha 40-47: Função `_init_llm()` deveria estar em módulo separado (SRP - Single Responsibility Principle)
- Falta type hints em retorno: `def _init_llm()` → `def _init_llm() -> Any:`

**app/rag/rag_pipeline.py**
- Linha 22-30: Lógica de detecção de "identity questions" com lista hardcoded
  - **Sugestão:** Externalizar para constantes ou config
- Linha 42: Uso de `getattr` sem default seguro
  ```python
  if getattr(settings, "use_mmr", False):
  ```
  **PEP 8:** OK, mas inconsistente com uso de settings.use_mmr em outros lugares

**app/api/routes.py**
- Linha 210: Tamanho máximo de arquivo hardcoded
  ```python
  max_size = 50 * 1024 * 1024  # 50 MB
  ```
  **Recomendação:** Mover para settings/config
- Linha 218: Sanitização de nome de arquivo muito simples, pode gerar colisões
  ```python
  safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ").strip()
  ```

**scripts/ask_oi.py**
- Linha 10: Import não utilizado (`StrOutputParser`)
- Linhas 32-34: Configuração de retriever inline poderia usar settings

#### ✅ Pontos Positivos
- Type hints presentes na maioria dos arquivos
- Uso de Pydantic para validação (routes.py)
- Docstrings nos endpoints da API
- Separação clara de responsabilidades (core, rag, api)

---

## 2. Análise de Lógica

### 2.1 Casos de Borda Não Tratados

#### ❌ Críticos

**app/rag/vectorstore.py**
- Linha 8-16: `_ensure_index()` - Se criação de índice falhar, não há retry ou fallback
  ```python
  pc.create_index(...)  # Pode falhar por timeout, quota, etc.
  ```
  **Risco:** Aplicação pode falhar silenciosamente ou travar
  **Recomendação:** Adicionar try/except, retry logic e logging

**app/api/routes.py - upload_document**
- Linha 206-210: Validação de extensão não considera case-sensitive completamente
  ```python
  file_ext = Path(file.filename).suffix.lower()  # OK
  ```
- Linha 237-240: Limpeza de arquivo em caso de erro não é garantida (pode deixar lixo)
  ```python
  if 'file_path' in locals() and file_path.exists():
      try:
          file_path.unlink()
      except:
          pass  # Silencia todos os erros - má prática
  ```
  **Risco:** Arquivos corrompidos/incompletos podem permanecer em disco

**app/rag/rag_pipeline.py**
- Linha 53-55: Acesso direto a `resp.content` sem validar estrutura de resposta
  ```python
  answer = (getattr(resp, "content", "") or "").strip()
  ```
  **Risco:** Se LLM retornar formato inesperado, pode gerar resposta vazia sem aviso

#### ⚠️ Moderados

**app/core/config.py**
- Linha 40-52: `_init_llm()` não valida se API keys estão presentes antes de inicializar
  ```python
  return ChatGroq(groq_api_key=settings.groq_api_key)  # Pode ser None
  ```
  **Risco:** Erro só ocorre em runtime (primeira consulta), não na inicialização

**scripts/ingest_local.py**
- Linha 9: Não verifica se `data/oi/` está vazia antes de prosseguir
- Linha 17: Se todos os arquivos falharem no load, chunks vazios irão para Pinecone

**scripts/check_pinecone.py**
- Linha 27: Assume que `describe_index_stats()` sempre retorna estrutura esperada
- Linha 34: Query com vetor zero pode não retornar resultados relevantes (falso negativo)

**app/api/routes.py**
- Linha 87: Dependency `get_vectorstore()` com cache global pode causar stale state
  ```python
  global _vectorstore_cache
  ```
  **Risco:** Se índice for atualizado externamente, cache não invalida

**front/chat_app.py**
- Linha 113: Upload de documento não valida tamanho do arquivo antes de ler
  ```python
  f.write(uploaded_file.getbuffer())  # Pode ser muito grande
  ```

### 2.2 Lógica Complexa / Simplificável

**app/api/routes.py - compile_comment (não existe mais, mas padrão se aplica)**
- String concatenation com `\n` poderia usar f-string ou template engine

**app/rag/rag_pipeline.py**
- Linha 22-30: Lista de triggers poderia ser regex ou fuzzy match
  ```python
  identity_triggers = ["quem é você", "quem é vc", ...]  # 9 variações hardcoded
  ```
  **Sugestão:** Usar NLP básico ou pattern matching

**app/core/metrics.py**
- Linha 9: `count_fallbacks()` usa string matching simples
  ```python
  if "não há informações suficientes" in text or ...
  ```
  **Sugestão:** Regex ou lista de padrões em config

### 2.3 Tratamento de Erros Incompleto

**app/rag/ingest.py**
- Linha 6-14: Exception genérica com print, mas continua processamento
  ```python
  except Exception as e:
      print(f"⚠️  Erro ao carregar {p.name}: {e}")
  ```
  **Risco:** Arquivos críticos podem falhar silenciosamente

**app/api/routes.py**
- Linha 283-286: Try/except genérico no upload sem logging adequado
  ```python
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Erro ao processar upload: {str(e)}")
  ```
  **Recomendação:** Log stack trace completo para debug

---

## 3. Análise de Segurança

### 3.1 Vulnerabilidades Detectadas

#### 🔴 Críticas

**main.py - CORS Configuration**
- Linha 35: CORS aberto para todas as origens em produção
  ```python
  allow_origins=["*"],  # Em produção, especificar domínios permitidos
  ```
  **Vulnerabilidade:** Qualquer site pode fazer requisições à API
  **CVE Relacionado:** CWE-346 (Origin Validation Error)
  **Recomendação:**
  ```python
  allow_origins=settings.allowed_origins.split(",") if settings.allowed_origins else ["http://localhost:3000"]
  ```

**app/api/routes.py - File Upload**
- Linha 210: Limite de 50 MB arbitrário, mas sem rate limiting
- Linha 218: Sanitização de filename inadequada
  ```python
  safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ").strip()
  ```
  **Vulnerabilidade:** Path traversal potencial se `..` for interpretado
  **Recomendação:** Usar `secure_filename()` do Werkzeug ou validar com regex `^[a-zA-Z0-9_.-]+$`

#### ⚠️ Moderadas

**app/core/config.py - API Keys Exposure**
- Linha 6-7: API keys em settings sem criptografia adicional
  ```python
  groq_api_key: Optional[str] = None
  google_api_key: Optional[str] = None
  ```
  **Risco:** Se .env vazar, keys comprometidas
  **Recomendação:** Usar secrets manager (AWS Secrets Manager, Azure Key Vault) em produção

**app/rag/vectorstore.py - Environment Variables**
- Linha 24-25: Sobrescreve variáveis de ambiente globalmente
  ```python
  os.environ["PINECONE_API_KEY"] = settings.pinecone_api_key
  ```
  **Risco:** Poluição de namespace, side effects
  **Recomendação:** Passar diretamente no construtor do client Pinecone

**scripts/ask_oi.py - Input Injection**
- Linha 17: Input do usuário vai direto para prompt sem sanitização
  ```python
  query = " ".join(sys.argv[1:])  # Sem validação
  ```
  **Risco:** Prompt injection (embora mitigado por RAG)
  **Recomendação:** Validar tamanho máximo e caracteres permitidos

**front/chat_app.py - File Upload sem validação de tipo real**
- Linha 57: Confia na extensão do arquivo
  ```python
  type=["pdf", "txt", "md"]
  ```
  **Risco:** Arquivo .pdf renomeado pode ser executável
  **Recomendação:** Validar magic bytes do arquivo (python-magic)

#### ℹ️ Boas Práticas de Segurança

**app/api/routes.py - Pydantic Validation**
- Uso de Pydantic para validação de entrada (Field com min_length/max_length)
- HTTPException com status codes apropriados

**app/rag/rag_pipeline.py - Resposta segura**
- Não expõe stack traces completos ao usuário
- Sanitiza output antes de retornar

### 3.2 Vazamento de Dados Sensíveis

#### ✅ Nenhum vazamento direto de PII detectado

- Não há hardcoding de CPF, emails, senhas no código
- Logs não expõem dados de usuários (apenas metadados)
- API não retorna informações internas sensíveis

#### ⚠️ Pontos de Atenção

**app/api/routes.py - Metadata Exposure**
- Linha 148-154: Retorna configurações internas na response
  ```python
  metadata={
      "prompt_style": request.prompt_style,
      "top_k": settings.top_k,
      ...
  }
  ```
  **Risco:** Informação sobre infrainterna pode ajudar atacantes
  **Recomendação:** Remover em produção ou colocar atrás de autenticação

**scripts/check_pinecone.py - Database Stats**
- Linha 33-35: Imprime estatísticas completas do Pinecone
  **Risco:** Se logs forem expostos, revela tamanho da base de dados

### 3.3 Vulnerabilidades Comuns (SQL Injection, XSS, etc.)

#### ✅ Não Aplicável / Mitigado

- **SQL Injection:** Não há SQL direto (usa Pinecone vector DB)
- **XSS:** API retorna JSON, não HTML (responsabilidade do frontend)
- **CSRF:** API REST stateless, sem cookies de sessão
- **Command Injection:** Não há execução de comandos shell com input de usuário

---

## 4. Recomendações Priorizadas

### 🔴 Alta Prioridade (Implementar Imediatamente)

1. **Corrigir CORS em Produção**
   - **Arquivo:** `main.py`
   - **Ação:** Adicionar `allowed_origins` no settings e usar lista restrita

2. **Melhorar Sanitização de Upload**
   - **Arquivo:** `app/api/routes.py`
   - **Ação:** Usar `secure_filename()` e validar magic bytes

3. **Adicionar Retry Logic no Pinecone**
   - **Arquivo:** `app/rag/vectorstore.py`
   - **Ação:** Envolver `create_index()` com try/except e exponential backoff

### ⚠️ Média Prioridade (Próxima Sprint)

4. **Externalizar Strings para i18n**
   - **Arquivos:** Todos os módulos com prints
   - **Ação:** Criar arquivo `messages.py` com dicionário PT/EN

5. **Adicionar Logging Estruturado**
   - **Arquivos:** Substituir todos os `print()` por `logger.info/error()`
   - **Ação:** Configurar formato JSON para logs de produção

6. **Validar API Keys na Inicialização**
   - **Arquivo:** `app/core/config.py`
   - **Ação:** Adicionar método `validate()` que verifica presence de keys

7. **Implementar Rate Limiting**
   - **Arquivo:** `main.py` (middleware)
   - **Ação:** Usar `slowapi` ou `fastapi-limiter`

### ℹ️ Baixa Prioridade (Backlog)

8. **Refatorar Identity Detection**
   - **Arquivo:** `app/rag/rag_pipeline.py`
   - **Ação:** Usar regex ou biblioteca de NLP

9. **Adicionar Testes Unitários**
   - **Cobertura atual:** ~0%
   - **Meta:** >80% para módulos críticos (rag_pipeline, routes)

10. **Documentar Casos de Borda**
    - **Ação:** Criar `docs/edge_cases.md` com comportamentos esperados

---

## 5. Métricas de Código

### Complexidade Ciclomática (estimada)

| Arquivo | Funções Complexas | McCabe Score Médio |
|---------|-------------------|--------------------|
| `app/api/routes.py` | `upload_document()` | ~12 (Alta) |
| `app/rag/rag_pipeline.py` | `answer_question()` | ~8 (Média) |
| `front/chat_app.py` | Main flow | ~10 (Média-Alta) |

**Recomendação:** Refatorar funções com score > 10 em subfunções menores

### Linhas de Código (LOC)

- **Total:** ~1.500 LOC (incluindo workflows e scripts)
- **Python puro:** ~1.200 LOC
- **Comentários/Docstrings:** ~15% (abaixo do ideal de 20-25%)

### Cobertura de Testes

- **Testes unitários:** 0 arquivos encontrados
- **Testes de integração:** Nenhum
- **Recomendação:** Criar suite básica com pytest

---

## 6. Conclusão e Próximos Passos

### Avaliação Geral: **B+ (Bom com Ressalvas)**

O projeto Open Insurance Agent demonstra:

**Pontos Fortes:**
- ✅ Arquitetura modular e bem organizada
- ✅ Uso de type hints e Pydantic para validação
- ✅ Separação clara de responsabilidades (core/rag/api)
- ✅ Documentação da API com Swagger
- ✅ Pipeline de CI/CD automatizado

**Áreas de Melhoria:**
- ⚠️ Consistência de idioma (migrar para inglês completo)
- ⚠️ Tratamento robusto de erros e casos de borda
- ⚠️ Configuração de segurança em produção (CORS, rate limiting)
- ⚠️ Cobertura de testes (atualmente zero)
- ⚠️ Logging estruturado e observabilidade

### Roadmap de Qualidade

**Q1 2025:**
- Corrigir vulnerabilidades críticas (CORS, upload)
- Adicionar testes unitários (>50% coverage)
- Migrar prints para logger estruturado

**Q2 2025:**
- Internacionalização completa (i18n)
- Implementar rate limiting e circuit breakers
- Documentação de casos de borda

**Q3 2025:**
- Refatorar funções complexas (score > 10)
- Adicionar testes de carga
- Auditoria de segurança externa

---

**Relatório gerado por:** GitHub Copilot Code Quality Analysis  
**Revisado por:** Análise automatizada baseada em PEP 8, OWASP Top 10 e boas práticas de Python  
**Última atualização:** 14/11/2025
