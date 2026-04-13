# Meu QA

Agente de IA com postura de **QA Sênior** para analisar mudanças de código, identificar riscos e sugerir cenários de testes manuais, unitários, de integração e de carga.

O projeto foi construído com foco em evolução gradual, começando pela execução local e caminhando para integração com **GitHub Actions** e uso futuro como **submódulo Git** em outros repositórios.

---

## Objetivo

O `Meu QA` foi criado para atuar como um agente avaliador de mudanças de software com uma visão de qualidade, e não apenas como um revisor de estilo de código.

Ele analisa alterações com foco em:

- riscos funcionais
- regressão
- comportamento inválido
- casos de borda
- integração
- observabilidade
- impacto em performance
- lacunas de testes

A ideia é que ele possa ser executado automaticamente a cada nova mudança no repositório e gere um relatório útil para desenvolvimento e QA.

---

## Principais características

- Postura de **QA Sênior**
- Análise de **arquivos alterados via Git diff**
- Uso de **CrewAI** para orquestração
- Uso de **Groq** como provider de LLM
- Configuração por **variáveis de ambiente**
- Saída em **Markdown**
- Estrutura pensada para futura execução em **GitHub Actions**
- Preparado para futura adaptação como **submódulo Git**

---

## Tecnologias utilizadas

- Python
- CrewAI
- LiteLLM
- Groq
- python-dotenv
- Git

---

## Estrutura do projeto

```text
meu-qa/
├─ .github/
│  └─ workflows/
├─ examples/
│  └─ user_service.py
├─ outputs/
│  └─ analysis.md
├─ src/
│  ├─ agent/
│  │  └─ qa_agent.py
│  ├─ config/
│  │  └─ settings.py
│  ├─ crew/
│  │  └─ qa_crew.py
│  ├─ prompts/
│  │  └─ system_prompt.txt
│  ├─ tasks/
│  │  └─ qa_task.py
│  ├─ utils/
│  │  └─ git_utils.py
│  └─ main.py
├─ tests/
├─ .env.example
├─ .gitignore
├─ README.md
└─ requirements.txt
```

---

## Como funciona

O fluxo atual é:

1. o script identifica arquivos alterados com Git
2. filtra arquivos que fazem sentido para análise
3. obtém o **diff** da mudança
4. lê o conteúdo atual do arquivo como contexto
5. envia a análise para uma crew do CrewAI
6. o agente responde com um relatório em Markdown
7. o resultado é salvo em `outputs/analysis.md`

---

## Persona do agente

O agente foi configurado para agir como um **QA Sênior**, com foco em qualidade e risco.

Isso significa que ele prioriza:

- impacto funcional da mudança
- regressão potencial
- cenários negativos
- integração com outros componentes
- necessidades de testes
- pontos que precisam de esclarecimento

Ele **não atua apenas como code reviewer estético**.

---

## Requisitos

Antes de rodar o projeto, você precisa ter instalado:

- Python 3.11+
- Git
- acesso a uma chave de API da Groq

---

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd meu-qa
```

### 2. Crie e ative um ambiente virtual

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`.

### Exemplo de `.env`

```env
LLM_PROVIDER=groq
LLM_MODEL=groq/llama-3.3-70b-versatile
LLM_API_KEY=sua_chave_aqui
LLM_TEMPERATURE=0
```

### Variáveis suportadas

- `LLM_PROVIDER`: provider do modelo
- `LLM_MODEL`: nome do modelo
- `LLM_API_KEY`: chave da API
- `LLM_TEMPERATURE`: temperatura da geração

Observação: o projeto foi pensado para ser configurável por ambiente, facilitando futuras trocas de provider/modelo.

---

## Como executar localmente

Faça alguma alteração em um arquivo analisável do projeto e rode:

```bash
python -m src.main
```

Se houver mudanças relevantes no Git, o agente irá gerar um relatório em:

```text
outputs/analysis.md
```

---

## Exemplo de saída

O relatório gerado segue uma estrutura semelhante a esta:

```md
# Arquivo analisado: examples/user_service.py

# Resumo da mudança
...

# Riscos identificados
...

# Cenários de testes manuais
...

# Sugestões de testes unitários
...

# Sugestões de testes de integração
...

# Sugestões de testes de carga ou desempenho
...

# Pontos que precisam de esclarecimento
...
```

---

## Como o Git é usado

Atualmente o projeto utiliza Git para descobrir arquivos alterados e obter o diff das mudanças.

### Etapas principais

- identificar arquivos modificados
- ignorar arquivos não relevantes
- obter diff do arquivo
- enviar diff + contexto atual do arquivo para análise

### Arquivos ignorados

Exemplos de extensões e diretórios ignorados:

- `.md`
- `.txt`
- imagens
- arquivos de lock
- `.venv`
- `outputs`
- `__pycache__`

Isso ajuda a manter a análise focada em arquivos de código e configuração relevantes.

---

## GitHub Actions

O projeto foi estruturado para ser executado futuramente em **GitHub Actions**, com foco em análises automáticas a cada push.

A evolução esperada inclui:

- checkout do repositório
- instalação das dependências
- configuração do `.env` via secrets
- execução do agente
- publicação do relatório como artefato

---

## Uso futuro como submódulo

A arquitetura atual foi pensada para permitir, no futuro, que este projeto seja incorporado em outro repositório como **submódulo Git**.

Objetivo desse modo de uso:

- manter o agente versionado separadamente
- reaproveitar a mesma lógica em múltiplos projetos
- executar a análise dentro do repositório pai
- disparar a avaliação automaticamente em pipeline

---

## Limitações atuais

No estágio atual, o projeto ainda possui algumas limitações conhecidas:

- análise ainda baseada em execução local/manual
- saída livre em Markdown, ainda sem schema estruturado por Pydantic
- análise focada em arquivos alterados, mas sem comentário automático em PR
- ainda não empacotado como submódulo pronto para múltiplos repositórios

Essas limitações fazem parte da evolução planejada.

---

## Próximos passos planejados

- melhorar a robustez da saída
- adicionar formato estruturado além do Markdown
- integrar com GitHub Actions
- publicar relatório como artefato
- futuramente comentar em PR
- adaptar para uso como submódulo Git
- permitir execução no repositório pai de forma mais transparente

---

## Filosofia do projeto

O objetivo do `Meu QA` não é apenas “revisar código”, mas **ampliar a visão de qualidade sobre mudanças de software**.

A proposta é atuar como apoio para times de desenvolvimento e QA, ajudando a responder perguntas como:

- quais riscos essa mudança introduz?
- o que precisa ser testado manualmente?
- quais testes automatizados deveriam existir?
- há impacto em integração ou performance?
- existe algo que ainda não foi claramente definido pelo requisito?

---

## Boas práticas recomendadas para uso

- manter a temperatura em `0` para respostas mais estáveis
- analisar preferencialmente o **diff**, não o arquivo inteiro
- ignorar arquivos que não sejam úteis para avaliação técnica
- revisar o relatório antes de tomar decisões automáticas baseadas nele
- usar o agente como apoio técnico, não como substituto de validação humana

---

## Troubleshooting

### Nenhum arquivo alterado relevante encontrado

Verifique se:

- existe mudança local no Git
- o arquivo alterado não está na lista de ignorados
- o arquivo foi salvo antes da execução

### Erro com modelo ou chave de API

Verifique se:

- o `.env` foi criado corretamente
- `LLM_API_KEY` está preenchida
- `LLM_MODEL` está configurado com um modelo válido

### Problemas com LiteLLM / dependências

Se houver erros relacionados a dependências opcionais, revise o `requirements.txt` e reinstale:

```bash
pip install -r requirements.txt
```

---

## Exemplo de evolução do projeto

A construção foi feita em etapas pequenas, passando por:

- estrutura inicial de pastas
- configuração com `.env`
- cliente de LLM
- criação do agente
- adaptação para CrewAI
- leitura de arquivo real
- análise de arquivos alterados
- análise de diff

Essa abordagem facilita aprendizado, manutenção e evolução.

---

## Contribuição

Como o projeto está em evolução, contribuições futuras podem incluir:

- melhorias nos prompts
- melhor filtragem de arquivos
- schema estruturado para saída
- integração com pull requests
- suporte a múltiplos providers
- melhorias de observabilidade

---

## Licença

Defina aqui a licença que você pretende usar.

Exemplos:

- MIT
- Apache-2.0
- uso interno

---

## Autor

Projeto criado para estudo, evolução prática em IA aplicada à qualidade de software e futura automação de revisão técnica com foco em QA.