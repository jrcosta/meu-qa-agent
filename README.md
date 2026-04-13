# Meu QA Sênior - Inteligência Artificial 🕵️‍♂️✨

**Meu QA** é um agente autônomo de Inteligência Artificial construído sobre **CrewAI** e LLMs modernos, estruturado com uma postura, senso crítico e mentalidade de um Engenheiro de Qualidade (**QA Sênior**). 

Seu principal objetivo é atuar localmente (ou em esteiras) analisando **mudanças em código fonte** mapeadas pelo Git  e produzindo relatórios de altíssima qualidade focados em blindar o seu projeto e prever cenários de risco.

---

## 🎯 O que ele faz?

Através da análise automática dos diffs dos arquivos, o Agente de QA fornece relatórios técnicos ricos, englobando:

- **Riscos e falhas lógicas** introduzidos pelas alterações atuais.
- **Cenários pragmáticos de testes manuais**.
- Estratégias e recomendações diretas para **Testes Unitários e Integração**.
- Avaliação rigorosa de caso de borda (*Edge Cases*) e comportamentos inválidos.
- Impactos de observabilidade, métricas e performance / testes de carga (quando aplicáveis).

## 🚀 Funcionalidades

- **Integração Real com Git localmente:** Não é necessário copiar e colar código no chat. O script identifica de forma autônoma os arquivos em estado modificado no versionamento local ou recém "comitados", buscando *exatamente as linhas do diff*.
- **Agnóstico de Linguagem:** Pode analisar Python, Javascript/Typescript, Go, Kotlin, Java, e tudo que seu git reportar. A IA tem o conhecimento intrínseco destas linguagens.
- **CrewAI e Abstrações Modernas de LLMs:** A arquitetura do projeto separa dinamicamente a definição do Agente e da Tarefa. É inteiramente plugável com Groq (Llama), OpenAI (GPT-4), Anthropic, etc. através do LiteLLM.
- **Relatórios consolidados:** Output nativo renderizado em Markdown para facilitar a fácil leitura, salvos de forma padronizada em disco (`outputs/analysis.md`).
- **Escalável:** Projetado de maneira enxuta, podendo ser usado localmente no dia a dia como "par de revisão", mas preparado para escalar como submodule de CI/CD em rotinas de pull-request no GitHub ou GitLab.

---

## 🛠️ Pré-requisitos

Para rodar este projeto localmente, certifique-se de ter instalado:

- **Python 3.10+**
- **Git**

## 📦 Instalação

1. Clone este repositório:
```bash
git clone https://github.com/jrcosta/meu-qa-agent.git
cd meu-qa-agent
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv .venv
# No Windows
.venv\Scripts\activate
# No Linux/Mac
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

O agente QA é plenamente configurável por meio de variáveis de ambiente.
Na raiz do código-fonte, renomeie (ou copie) o arquivo `.env.exemple` para `.env` e ajuste suas configurações.

Exemplo pronto utilizando a [Groq](https://console.groq.com/):

```env
LLM_PROVIDER=groq
LLM_MODEL=groq/llama-3.3-70b-versatile
LLM_API_KEY=sua-api-key-aqui
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_TEMPERATURE=0.2
```

> **Dica:** Os provedores abertos (como Groq, Ollama) funcionam perfeitamente na CLI seguindo a notação de modelos da lib LiteLLM (ex: `groq/llama-3.3-70b-versatile`).

## 💻 Como rodar e analisar código

1. Faça suas modificações normais no software ou adicione arquivos nos seus projetos de teste.
2. Com o seu ambiente ativado, simplesmente dispare a ferramenta na linha de comando na pasta do repositório:

```bash
python -m src.main
```

3. O QA Agent iniciará o mapeamento, inspecionará o git diff das suas modificações, passará todo o contexto técnico para a camada do modelo, processará a tarefa e confirmará a escrita. 

**O relatório técnico completo ficará em:**
👉 `outputs/analysis.md`

---

## 🗂 Estrutura do Código

Para quem desejar contribuir ou expandir:

```text
meu-qa-agent/
├── src/
│   ├── agent/       # Definições, restrições e persona do QA Sênior
│   ├── config/      # Configurações de settings e Pydantic para environment
│   ├── crew/        # Runners de equipe coordenados via CrewAI
│   ├── prompts/     # Configuração nativa de system_prompts
│   ├── tasks/       # Representação e delegação das análises
│   ├── utils/       # Parsers de git e file mapping
│   └── main.py      # Ponto de inicialização do programa
├── examples/        # Stub e códigos exemplares com "falhas de implementação" 
├── outputs/         # Arquitetura autogerenciada que receberá os relatórios 
└── ...
```