import unittest
import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from atualizar_painel import (
    carregar_mapeamentos,
    obter_todos_os_dias,
    calcular_periodos_e_semanas
)

class TestAtualizarPainel(unittest.TestCase):
    def test_carregar_mapeamentos(self):
        fran_map, corp_map = carregar_mapeamentos()
        self.assertIsInstance(fran_map, dict)
        self.assertIsInstance(corp_map, dict)
        self.assertGreater(len(fran_map), 50, "Deve haver dezenas de lojas de franquias mapeadas")
        self.assertGreater(len(corp_map), 10, "Deve haver lojas corporativas mapeadas")
        self.assertIn("19602", fran_map, "Loja 19602 deve estar no mapa de franquias")

    def test_obter_todos_os_dias(self):
        dias = obter_todos_os_dias()
        self.assertIsInstance(dias, list)
        self.assertGreater(len(dias), 90, "Base historica deve possuir mais de 90 dias")
        for d in dias:
            self.assertEqual(len(d), 10, f"Data {d} deve ter formato YYYY-MM-DD")
            self.assertEqual(d[4], '-')
            self.assertEqual(d[7], '-')

    def test_calcular_periodos_e_semanas(self):
        dias = obter_todos_os_dias()
        periods, weeks = calcular_periodos_e_semanas(dias)
        self.assertIsInstance(periods, dict)
        self.assertIsInstance(weeks, list)
        self.assertEqual(len(weeks), 4, "Devem ser exatamente 4 semanas na janela movel")
        self.assertIn('acumulado', periods, "Periods deve conter acumulado")
        for w in weeks:
            self.assertIn(w, periods, f"Semana {w} deve estar presente em periods")

    def test_integridade_data_json(self):
        expected_keys = ['stores', 'weeks', 'adt', 'exceptions', 'monthly', 'updatedAt', 'backfill']
        for subpath in ['franquias/data.json', 'lojas-proprias/data.json']:
            full_path = os.path.join(BASE_DIR, subpath)
            self.assertTrue(os.path.exists(full_path), f"Arquivo {subpath} deve existir")
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for k in expected_keys:
                self.assertIn(k, data, f"Chave {k} deve estar em {subpath}")
            self.assertGreater(len(data['stores']), 0)

if __name__ == '__main__':
    unittest.main()