"""Task definition for the memory summariser agent."""

from crewai import Task


class MemoryTaskFactory:
    @staticmethod
    def create(agent, comment_body: str, repo: str, pr_number: int) -> Task:
        description = f"""
Você recebeu o seguinte comentário de revisão feito em um PR de testes unitários gerados automaticamente:

Repositório: {repo}
PR: #{pr_number}

Comentário:
[INICIO_COMENTARIO]
{comment_body}
[FIM_COMENTARIO]

Sua tarefa:
1. Leia o comentário com atenção.
2. Identifique todos os pontos onde o gerador de testes errou ou poderia melhorar.
3. Para cada ponto, escreva UMA lição curta e acionável (máximo 2 frases).
4. Ignore elogios, agradecimentos ou partes irrelevantes.
5. Se o comentário não contiver críticas ou sugestões de melhoria, responda "Nenhuma lição extraída."

Formato de resposta (uma lição por linha, prefixada por "- "):
- Não usar nomes genéricos como 'test1', 'test2'; usar nomes descritivos do cenário.
- Sempre mockar dependências externas em vez de fazer chamadas reais.
- ...
"""
        return Task(
            description=description,
            expected_output="Lista de lições aprendidas, uma por linha, prefixadas por '- '.",
            agent=agent,
        )
