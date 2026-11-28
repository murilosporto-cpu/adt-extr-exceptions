#!/usr/bin/env python3
"""
Test Runner do Projeto Dominos Pizza (Cafe com PWR)
Executa a suite de testes em tests/ com unittest.
Compativel com 'python run_tests.py', 'python -m unittest' e 'pytest'.
"""
import os
import sys
import unittest

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(base_dir, 'tests')
    
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
        
    print('===========================================================')
    print('   EXECUTANDO SUITE DE TESTES AUTOMATIZADOS (PWR DOMINOS)  ')
    print('===========================================================')
    
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=tests_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print('===========================================================')
    if result.wasSuccessful():
        print(f'   [SUCESSO] Todos os {result.testsRun} testes passaram!')
        print('===========================================================')
        sys.exit(0)
    else:
        print(f'   [FALHA] Falhas: {len(result.failures)} | Erros: {len(result.errors)}')
        print('===========================================================')
        sys.exit(1)

if __name__ == '__main__':
    main()