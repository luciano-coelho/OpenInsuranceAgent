# Open Insurance Agent

### Um agente de IA modular e auditável para análise normativa do Open Insurance Brasil

---

## Visão Geral

O Open Insurance Agent é um projeto de pesquisa aplicada desenvolvido por Luciano Coelho, doutorando em Ciência da Computação pela UFSC, vinculado ao Laboratório de Segurança em Computação (LabSEC), sob orientação do Prof. Ricardo Custódio.

A solução combina técnicas de RAG (Retrieval-Augmented Generation) e embeddings regulatórios com modelos de linguagem auditáveis, oferecendo um protótipo inovador para análise automatizada e segura de normas do Open Insurance Brasil. Essa abordagem permite rastreabilidade das fontes, auditoria das respostas e avaliação contínua de métricas de precisão e aderência normativa, garantindo maior confiabilidade nas interpretações automatizadas de documentos oficiais.

A iniciativa integra esforços de inovação regulatória, inteligência artificial e cibersegurança no contexto do Open Insurance Brasil (OPIN) — programa supervisionado pela Superintendência de Seguros Privados (SUSEP) e vinculado ao ecossistema Open Finance Brasil.

**O projeto propõe um agente inteligente especializado em normas, diretrizes e padrões técnicos do Open Insurance, capaz de:**

- interpretar documentos oficiais da SUSEP, CNSP e CMN;

- responder a consultas técnicas e regulatórias de forma fundamentada;

- gerar análises rastreáveis, explicáveis e auditáveis.  

---

## Arquitetura do Sistema

O sistema é baseado em uma **arquitetura RAG (Retrieval-Augmented Generation)**, permitindo que as respostas da IA sejam sempre **fundamentadas em documentos oficiais**.  
O fluxo completo é dividido em cinco camadas:

```bash
┌───────────────────────────────────────────────────────┐
│                    User Interface                     │
│     (CLI, API REST ou Chat Interface)                 │
├───────────────────────────────────────────────────────┤
│                        RAG Layer                      │
│  • Recuperação vetorial (Pinecone)                    │
│  • Chunks semânticos (LangChain)                      │
│  • Controle de contexto e histórico de consultas       │
├───────────────────────────────────────────────────────┤
│                 Embedding & LLM Layer                 │
│  • HuggingFace Embeddings                             │
│  • LLM Modular (Groq, Gemini, Ollama, OpenAI, etc.)   │
├───────────────────────────────────────────────────────┤
│                     Ingest Layer                      │
│  • Extração de dados de PDFs, TXT e MD                │
│  • Normalização de documentos SUSEP/Open Finance      │
│  • Tokenização e chunking regulatório                 │
├───────────────────────────────────────────────────────┤
│                   Monitoring Layer                    │
│  • Métricas (Prometheus)                              │
│  • Avaliação (RAGAs + MLflow)                         │
└───────────────────────────────────────────────────────┘
```

## Características Principais

### 1. Modularidade da IA

O agente não está vinculado a uma IA específica.
Ele opera sob um modelo de acoplamento dinâmico, aceitando qualquer provedor de modelo de linguagem (LLM) que possua API Key válida e suporte ao endpoint compatível com o padrão OpenAI-like.

**Atualmente, são suportados:**

- Groq API (mixtral, llama3, gemma2);

- Google Gemini (vía Vertex ou REST);

- OpenAI (gpt-4o, gpt-4-turbo);

- Ollama (modelos llama3, mistral, phi3);

Essa modularidade garante portabilidade, redundância e independência tecnológica, permitindo continuidade operacional mesmo diante de descontinuações de modelos.

### 2. Base Regulamentar

**Os documentos utilizados são fontes oficiais, públicas e auditáveis, incluindo:**

- Circulares, Resoluções e RDDs da SUSEP;

- Documentos técnicos da OPIN (Diretório de Participantes, Certificação, Glossário, etc.);

- Manuais e guias publicados no Portal da SUSEP e no repositório público do Open Insurance Brasil.

Esses materiais são armazenados localmente em */data/oi* e ingeridos via *scripts/ingest_local.py*.

### 3. Ingestão e Indexação

**A pipeline de ingestão realiza:**

- Extração e normalização de documentos (PyPDFLoader, UnstructuredMarkdownLoader);

- Divisão em blocos semânticos (chunks) configuráveis via .env;

- Criação e sincronização de embeddings (all-MiniLM-L6-v2) no Pinecone;

- Monitoramento de volume e latência para cada ciclo de ingestão.

O resultado é um índice vetorial consistente, capaz de responder a consultas com precisão contextual.

### 4. Consultas Inteligentes

As consultas podem ser realizadas via CLI:

```bash
python -m scripts.ask_oi "Quais são os requisitos de certificados para clientes e servidores no Open Insurance Brasil?"
```
**O agente realiza:**

- Recuperação dos 5 trechos mais relevantes (Top-K);

- Consolidação do contexto em prompt estruturado;

- Geração de resposta fundamentada e rastreável, com metadados da fonte.

### 5. Base Conceitual e Pesquisa

**O projeto está ancorado em princípios acadêmicos e regulatórios sólidos:**

```bash
“A solução proposta combina técnicas de RAG e embeddings regulatórios com modelos de linguagem auditáveis, oferecendo um protótipo inovador para análise automatizada e segura de normas do Open Insurance Brasil.”
```
**Essa estrutura visa:**

- Reduzir erros humanos em consultas normativas;

- Acelerar a conformidade regulatória;

- Garantir rastreabilidade das respostas e explicabilidade algorítmica;

- Fortalecer a interoperabilidade entre Open Finance e Open Insurance;

- Apoiar a SUSEP e instituições participantes na supervisão e implementação de fases do Opin.

### 6. Riscos e Cuidados

- O sistema deve ser constantemente atualizado para refletir mudanças regulatórias.

- É essencial manter mecanismos de auditoria e logging completo.

- As conexões externas (Pinecone, LLM APIs) devem seguir padrões de criptografia TLS 1.3.

*O uso institucional requer validação prévia da SUSEP e acompanhamento técnico de conformidade.*

### 7. Pipeline de Qualidade e Segurança Automatizado

**O projeto conta com um pipeline de CI/CD inteligente que garante a qualidade, segurança e conformidade do código em cada Pull Request.**

A cada mudança proposta, o sistema executa automaticamente:

- **Análise de Padrões (Linter)**: Verifica aderência ao PEP 8, nomenclaturas em inglês e boas práticas de código;

- **Análise de Lógica**: Identifica casos de borda não tratados, potenciais bugs e oportunidades de simplificação;

- **Análise de Segurança**: Detecta vulnerabilidades, vazamento de dados sensíveis (PII) e práticas inseguras (hardcoded paths, injection risks);

- **Auditoria Consolidada**: Gera um relatório estruturado em Markdown com resumo, riscos identificados e recomendações categorizadas.

**Características do Pipeline:**

- Análise multi-perspectiva executada em paralelo por especialistas de IA independentes;

- Comentários automáticos no PR consolidando as três análises em formato legível;

- Rastreabilidade completa via artefatos do GitHub Actions;

- Integração com segredos seguros (AI_API_KEY) e sanitização de diff antes da análise.

Esse fluxo automatizado fortalece a confiabilidade do código, reduz erros humanos e acelera a revisão técnica, mantendo altos padrões de segurança e qualidade ao longo do desenvolvimento.

### 8. Métricas e Observabilidade

**O agente coleta métricas em tempo real via Prometheus, permitindo monitorar:**

- Latência média de consulta;

- Taxa de acerto semântico (via RAGAs);

- Consumo de tokens e custo operacional;

- Disponibilidade e tempo de resposta das APIs conectadas.

Os experimentos são versionados via MLflow e avaliados sob metodologia A/B com diferentes LLMs.

## Configuração do Ambiente

### 1. Pré-requisitos

Certifique-se de ter instalado:

- Python **3.10+**
- Git
- Virtualenv (recomendado)
- Conta ativa no [Pinecone](https://www.pinecone.io/)
- API Key válida para o provedor de LLM (Groq, Gemini, OpenAI, etc.)

---

### 2. Clonar o repositório

```bash
git clone https://github.com/luciano-coelho/OpenInsuranceAgent.git
cd open-insurance-agent
```

### 3. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
# Ativar o ambiente

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente
Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

```bash
# ---- LLM / Embeddings ----
GROQ_API_KEY=your_groq_key
GEN_MODEL=llama3-8b-8192
EMBED_MODEL=all-MiniLM-L6-v2

# ---- Pinecone ----
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=open-insurance-index

# ---- RAG ----
TOP_K=5
CHUNK_SIZE=600
CHUNK_OVERLAP=80
```

⚠️ Observação:
O agente é modular — ele não está vinculado a uma IA específica.
Basta trocar a chave e o nome do modelo no .env para usar Groq, Gemini, OpenAI, Ollama ou qualquer outro LLM compatível com API REST no padrão OpenAI-like.

### 6. Adicionar os documentos oficiais
Coloque os arquivos normativos e técnicos em:
```bash
/data/oi/
```

**Suporta os formatos:**

- .pdf
- .txt
- .md

**Exemplo:**
Circulares SUSEP, Resoluções CNSP, RDDs, perfis de segurança do Open Finance, etc.

### 7. Executar a ingestão de documentos

```bash
python -m scripts.ingest_local
```

**Este comando irá:**

- Ler e processar os documentos;

- Gerar chunks semânticos;

- Criar embeddings e enviar para o Pinecone.

### 8. Verificar o status do índice

```bash
python -m scripts.check_pinecone
```
Exibe o total de vetores, status do índice e amostra de metadados armazenados.

### 9. Realizar consultas

```bash
python -m scripts.ask_oi "Quais são os requisitos de certificados para clientes e servidores no Open Insurance Brasil?"
```

---

## API REST (Swagger/OpenAPI)

O sistema expõe uma **API REST completa** com documentação interativa Swagger.

### Iniciar o servidor API

```powershell
python -m uvicorn main:app --reload --port 8000
```

Acesse a documentação interativa: **http://127.0.0.1:8000/docs**

### Endpoints Disponíveis

#### POST `/api/v1/ask` - Consultar agente
Envia uma pergunta e recebe resposta fundamentada em documentos oficiais.

#### GET `/api/v1/health` - Health check
Verifica status da API e serviços.

#### GET `/api/v1/metrics` - Métricas do sistema
Retorna configurações e parâmetros do sistema.

### POST `/api/v1/upload` - Upload de documentos
Permite que a equipe faça upload de novos documentos oficiais.

### Recursos da API

- ✅ **Documentação interativa** Swagger UI (`/docs`) e ReDoc (`/redoc`)
- ✅ **Validação automática** de requests com Pydantic
- ✅ **CORS habilitado** para integração com frontends
- ✅ **Upload de documentos** com ingestão automática no Pinecone
- ✅ **Múltiplos estilos de prompt** (concise, detailed, bullet_points, yes_no)
- ✅ **Retorno opcional de contextos** recuperados do vectorstore
- ✅ **Métricas de latência** em todas as respostas
- ✅ **Health check** para monitoramento
- ✅ **Endpoints versionados** (`/api/v1/`)

---

###  Autores e Colaboradores

Luciano Coelho — Doutorando em Ciência da Computação (UFSC / LabSEC)

Prof. Ricardo Custódio — Orientador (UFSC / LabSEC)

Manuel Matos — Coautor (Câmara e-net)

Drª. Priscila Figueiredo - Seleção de documentos normativos (Open Power Corretora de Seguros SA)