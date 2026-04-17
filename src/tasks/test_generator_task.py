from crewai import Task


class TestGeneratorTaskFactory:
    @staticmethod
    def create(
        agent,
        qa_report: str,
        file_path: str,
        code_content: str,
        repo_context: str,
    ) -> Task:
        description = f"""
Você deve gerar testes unitários baseados no relatório de QA abaixo.

Arquivo alvo: {file_path}

Relatório de QA:
[INICIO_RELATORIO]
{qa_report}
[FIM_RELATORIO]

Código-fonte atual do arquivo:
[INICIO_CODIGO]
{code_content}
[FIM_CODIGO]

Contexto adicional do repositório:
[INICIO_CONTEXTO]
{repo_context}
[FIM_CONTEXTO]

Instruções:
1. Leia atentamente a seção "Sugestões de testes unitários" do relatório de QA.
2. Analise o código-fonte para entender a implementação real.
3. Identifique o framework de testes usado no projeto (pytest, unittest, jest, mocha, etc.).
4. Gere testes unitários concretos para CADA sugestão do relatório.
5. Siga a estrutura de pastas e convenções do projeto.

Sua resposta deve ser APENAS no formato abaixo, um bloco para cada arquivo de teste:

### FILE: <caminho_relativo_do_arquivo_de_teste>
```
<código completo do arquivo de teste>
```

Regras:
- gere código completo e executável
- inclua todos os imports necessários
- use nomes descritivos para os testes
- cubra cenários positivos e negativos
- use mocks quando necessário para isolar dependências externas
- NÃO inclua explicações fora dos blocos de código
"""

        expected_output = """
Arquivos de teste completos em formato Markdown com blocos de código, prontos para serem salvos e executados.
"""

        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
        )
