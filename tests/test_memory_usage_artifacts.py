import unittest

from src.crew.test_generator_crew import _parse_memory_result


class MemoryUsageArtifactTests(unittest.TestCase):
    def test_parse_memory_result_extracts_structured_lessons(self):
        raw = (
            "[distance=0.421] (PR #63 em jrcosta/repo_alvo_api_simples, por qagent[bot])\n"
            "  Lição: Validar campos novos no contrato JSON.\n\n"
            "[distance=0.812] (PR #61 em jrcosta/repo_alvo_api_simples, por reviewer)\n"
            "  Lição: Cobrir compatibilidade de clientes antigos."
        )

        memories = _parse_memory_result(raw)

        self.assertEqual(2, len(memories))
        self.assertEqual(63, memories[0]["pr_number"])
        self.assertEqual("jrcosta/repo_alvo_api_simples", memories[0]["repo"])
        self.assertEqual("qagent[bot]", memories[0]["author"])
        self.assertEqual(0.421, memories[0]["distance"])
        self.assertEqual("Validar campos novos no contrato JSON.", memories[0]["lesson"])

    def test_parse_memory_result_ignores_empty_or_missing_memory_messages(self):
        self.assertEqual([], _parse_memory_result(""))
        self.assertEqual([], _parse_memory_result("Nenhuma memória relevante encontrada para esta consulta."))


if __name__ == "__main__":
    unittest.main()
