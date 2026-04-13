from crewai import Task


class QATaskFactory:
    @staticmethod
    def create(agent, file_path: str, file_diff: str, code_content: str) -> Task:
        description = f"""
Você é um QA Sênior e deve produzir um relatório técnico completo sobre a mudança abaixo.

Arquivo: {file_path}

Diff da mudança:
[INICIO_DIFF]
{file_diff}
[FIM_DIFF]

Conteúdo atual do arquivo para contexto:
[INICIO_CODIGO]
{code_content}
[FIM_CODIGO]

Analise com foco em:
- riscos funcionais da mudança
- regressão
- comportamento inválido
- casos de borda
- integração
- observabilidade
- impacto em performance, quando aplicável

Preencha obrigatoriamente estas seções:
# Resumo da mudança
# Riscos identificados
# Cenários de testes manuais
# Sugestões de testes unitários
# Sugestões de testes de integração
# Sugestões de testes de carga ou desempenho
# Pontos que precisam de esclarecimento

Regras obrigatórias:
- foque principalmente no diff
- use o conteúdo completo apenas como contexto
- não inclua "Thought:"
- não inclua raciocínio interno
- não faça conclusão final
- não diga "o relatório acima"
- entregue apenas o relatório final em markdown
"""

        expected_output = """
Relatório completo em Markdown, com todas as seções solicitadas preenchidas.
"""

        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            markdown=True,
            output_file="outputs/analysis.md",
        )