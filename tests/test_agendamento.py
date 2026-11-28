import unittest
import os
import sys
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from executar_agendamento_diario import obter_datas_alvo

class TestAgendamentoDiario(unittest.TestCase):
    def test_obter_datas_alvo(self):
        target_dates, yesterday_str = obter_datas_alvo()
        self.assertIsInstance(target_dates, list)
        self.assertGreaterEqual(len(target_dates), 10, "Janela de seguranca deve conter no minimo 10 datas")
        self.assertEqual(len(yesterday_str), 10, "Ontem deve ter formato YYYY-MM-DD")
        self.assertIn(yesterday_str, target_dates, "Dia de ontem deve estar entre as datas alvo")
        for dt in target_dates:
            # Validar formato de data
            datetime.strptime(dt, '%Y-%m-%d')

    def test_arquivos_agendamento_existem(self):
        py_script = os.path.join(BASE_DIR, 'executar_agendamento_diario.py')
        bat_script = os.path.join(BASE_DIR, 'EXECUTAR_AGENDAMENTO_DIARIO.bat')
        self.assertTrue(os.path.exists(py_script), "executar_agendamento_diario.py deve existir")
        self.assertTrue(os.path.exists(bat_script), "EXECUTAR_AGENDAMENTO_DIARIO.bat deve existir")
        
        # Validar conteudo basico do bat
        with open(bat_script, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        self.assertIn('executar_agendamento_diario.py', content)
        self.assertNotIn('pause', content.lower(), "Nao deve conter comandos interativos como pause no bat de agendamento")

    def test_tarefa_agendador_windows(self):
        # Valida que a tarefa esta registrada no Task Scheduler
        res = subprocess.run(
            ['schtasks', '/query', '/tn', 'Dominos_PWR_Varredura_Diaria'],
            capture_output=True,
            text=True,
            errors='ignore'
        )
        self.assertEqual(res.returncode, 0, "A tarefa Dominos_PWR_Varredura_Diaria deve estar registrada no Task Scheduler")
        self.assertIn('Dominos_PWR_Varredura_Diaria', res.stdout)

if __name__ == '__main__':
    unittest.main()