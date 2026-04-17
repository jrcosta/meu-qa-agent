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

# QAgent

Agente de IA com foco em **QA** para analisar mudanças de código, identificar riscos e sugerir cenários de teste de forma automatizada.

![Python](https://img.shields.io/badge/Python-3.14.7+-3776AB?logo=python&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Agent%20Orchestration-6B46C1)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions&logoColor=white)

Uma ferramenta que compara commits (diff) e gera relatórios com foco em qualidade (riscos, impactos e sugestões de testes).

## Principais recursos

- Classifica o tipo de mudança
- Identifica riscos e impactos prováveis
- Gera cenários de teste manuais e sugestões de testes automatizados
- Salva o resultado em Markdown para publicação/histórico

## Stack

- Python (orquestração)
- CrewAI (agentes e tasks)
- Groq (LLM provider) — configurável via variáveis de ambiente
- GitHub Actions (CI)

## Instalação

1. Crie e ative um ambiente virtual (recomendado).

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

3. Copie o arquivo de exemplo de variáveis de ambiente e ajuste as chaves:

```powershell
copy .env.example .env
```

## Execução local

O ponto de entrada principal é `src/main.py`. Exemplo básico:

```powershell
python -m src.main --repo-path . --output-file outputs/analysis.md
```

Comparando um range de commits:

```powershell
python -m src.main --repo-path . --output-file outputs/analysis.md --base-sha COMMIT_BASE --head-sha COMMIT_HEAD
```

## Estrutura do projeto

```text
src/
├─ agent/
├─ config/
├─ crew/
├─ prompts/
├─ schemas/
├─ services/
├─ tasks/
├─ tools/
├─ utils/
└─ main.py
```

## Observações de limpeza

- Pastas de cache Python (`__pycache__`) são ignoradas via `.gitignore`. Elas podem ser removidas com segurança do disco.
- O diretório `outputs/` também está ignorado para evitar comitar relatórios locais.

## Ambiente

Coloque suas credenciais e configurações em `.env`. Um exemplo de variáveis necessárias está em `.env.example` (LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, etc.).

## Roadmap (curto prazo)

- agentes especializados por tipo de teste
- investigação mais profunda de contexto
- revisão mais específica por stack

## Status

Projeto em evolução — esta é uma base para automatizar análises de QA com agentes de IA.
