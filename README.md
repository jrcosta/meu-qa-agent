# QAgent

> **Novo:** Sistema de memórias — captura comentários de revisão em PRs de testes
> e extrai lições aprendidas para melhorar execuções futuras. Detalhes em
> [`docs/memories.md`](docs/memories.md).

Agente de IA com foco em **QA** para analisar mudanças de código, identificar riscos e sugerir cenários de teste de forma automatizada.

![Python](https://img.shields.io/badge/Python-3.14.7+-3776AB?logo=python&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Agent%20Orchestration-6B46C1)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions&logoColor=white)

## O que ele faz

O QAgent analisa alterações de código a partir do **diff entre commits**, busca contexto adicional no repositório e gera um relatório com foco em QA, incluindo:

- Tipo da mudança
- Riscos identificados
- Impacto provável
- Cenários de testes manuais
- Sugestões de testes automatizados
- Pontos que precisam de esclarecimento

## Como funciona

1. Um repositório principal dispara um workflow ao receber push.
2. O workflow chama o repositório do **QAgent**.
3. O QAgent faz checkout do repositório alvo.
4. Ele compara `base_sha` e `head_sha` para descobrir o que mudou.
5. O agente usa o diff + contexto do repositório para gerar o relatório.
6. O resultado é salvo em Markdown.

## Stack

- **Python** — orquestração
- **CrewAI** — agentes e tasks
- **Groq** — LLM provider (configurável via variáveis de ambiente)
- **GitHub Actions** — automação CI

## Estrutura do projeto

```text
src/
├─ agent/        # Definição do agente de QA
├─ config/       # Settings e variáveis de ambiente
├─ crew/         # Orquestração CrewAI
├─ prompts/      # Prompt de sistema
├─ schemas/      # Schemas Pydantic de resultado
├─ services/     # Context builder e client LLM
├─ tasks/        # Definição de tasks
├─ tools/        # Ferramentas do agente (leitura de repo)
├─ utils/        # Utilitários (git, debug logger)
└─ main.py       # Ponto de entrada CLI
```

## Instalação

1. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:

```bash
cp .env.example .env
# Edite .env e preencha suas chaves (LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, etc.)
```

## Execução local

```bash
python -m src.main --repo-path . --output-file outputs/analysis.md
```

Com range de commits:

```bash
python -m src.main --repo-path . --output-file outputs/analysis.md --base-sha COMMIT_BASE --head-sha COMMIT_HEAD
```

## Roadmap

- Agentes especializados por tipo de teste
- Investigação mais profunda de contexto
- Revisão mais específica por stack

## Status

Projeto em evolução — base para automatizar análises de QA com agentes de IA.
