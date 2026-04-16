from crewai import Task


class QATaskFactory:
    @staticmethod
    def create(
        agent,
        file_path: str,
        file_diff: str,
        code_content: str,
        repo_context: str,
    ) -> Task:
        description = f"""
Você deve revisar a mudança abaixo com postura de QA Sênior Investigador.

Arquivo alterado: {file_path}

Diff da mudança:
[INICIO_DIFF]
{file_diff}
[FIM_DIFF]

Conteúdo atual do arquivo:
[INICIO_CODIGO]
{code_content}
[FIM_CODIGO]

Contexto inicial do repositório:
[INICIO_CONTEXTO]
{repo_context}
[FIM_CONTEXTO]

Instruções de investigação:
1. Entenda exatamente o que mudou no diff.
2. Use o conteúdo atual do arquivo como fonte principal.
3. Quando o diff e o arquivo não forem suficientes, use as tools disponíveis para buscar evidência adicional.
4. Priorize abrir arquivos diretamente relacionados, localizar testes existentes e buscar símbolos do diff no repositório.
5. Não use tools sem objetivo claro e não repita buscas inúteis.
6. Após usar uma tool, incorpore explicitamente o que foi encontrado à análise.
7. Se uma tool falhar, registre a limitação e siga com a melhor análise possível.
8. Não invente regra de negócio sem evidência observável.

Sua resposta deve conter:

# Tipo da mudança
Classifique a mudança.

# Evidências observadas
Aponte os trechos ou comportamentos do diff, do arquivo e das tools que sustentam sua análise.
Sempre cite a origem da evidência.

# Impacto provável
Explique o que provavelmente foi afetado.

# Riscos identificados
Liste riscos reais e contextualizados.
Para cada risco, inclua:
- descrição
- evidência
- impacto provável

# Cenários de testes manuais
Sugira cenários específicos para a mudança.
Para cada cenário, inclua objetivo e evidência.

# Sugestões de testes unitários
Sugira testes unitários específicos.
Para cada sugestão, inclua alvo do teste e evidência.

# Sugestões de testes de integração
Sugira testes de integração específicos.
Para cada sugestão, inclua fluxo coberto e evidência.

# Sugestões de testes de carga ou desempenho
Inclua apenas se a mudança justificar claramente.
Se não houver evidência, diga explicitamente que não há indício suficiente.

# Pontos que precisam de esclarecimento
Liste dúvidas relevantes de negócio ou implementação.

Regras:
- não escreva resposta genérica
- não faça checklist superficial
- não diga apenas "testar funcionalidade"
- não invente contexto que não esteja no diff, no arquivo, no contexto inicial ou no resultado das tools
- não sugira performance/carga sem indício real
- prefira dizer "não há evidência suficiente" em vez de supor
"""

        expected_output = """
Relatório completo em Markdown, técnico, contextualizado, investigativo e baseado no diff, no conteúdo atual do arquivo, no contexto inicial e nas evidências obtidas com tools.
"""

        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            markdown=True,
        )
