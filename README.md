# QAgent

Agente de IA com foco em **QA** para analisar mudanças de código, identificar riscos e sugerir cenários de teste de forma automatizada.

![Python](https://img.shields.io/badge/Python-3.14.7+-3776AB?logo=python&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Agent%20Orchestration-6B46C1)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-History-222222?logo=githubpages&logoColor=white)

## O que ele faz

O QAgent analisa alterações de código a partir do **diff entre commits**, busca contexto adicional no repositório e gera um relatório com foco em QA, incluindo:

- tipo da mudança
- riscos identificados
- impacto provável
- cenários de testes manuais
- sugestões de testes unitários
- sugestões de testes de integração
- pontos que precisam de esclarecimento

## Como funciona

1. Um repositório principal dispara um workflow ao receber push.
2. O workflow chama o repositório do **QAgent**.
3. O QAgent faz checkout do repositório alvo.
4. Ele compara `base_sha` e `head_sha` para descobrir o que mudou.
5. O agente usa o diff + contexto do repositório para gerar o relatório.
6. O resultado é salvo em Markdown e publicado com histórico no **GitHub Pages**.

## Stack

- **Python** para orquestração
- **CrewAI** para agentes e tasks
- **Groq** como provedor de LLM
- **GitHub Actions** para automação
- **GitHub Pages** para histórico dos relatórios

## Estrutura

```text
src/
├─ agent/
├─ config/
├─ crew/
├─ prompts/
├─ tasks/
├─ tools/
├─ utils/
└─ main.py
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

- agentes especializados por tipo de teste
- investigação mais profunda de contexto
- revisão mais específica por stack
- expansão para unit, integration, e2e e performance

## Status

Projeto em evolução, construído em pequenas etapas para aprendizado e aprofundamento em automação de QA com IA.
