"""Verificaciones funcionales con datos artificiales. No entrena Deep Learning."""
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PortfolioTests(unittest.TestCase):
    def test_syntax_and_notebook_schema(self):
        import nbformat
        for path in ROOT.rglob('*.py'):
            with self.subTest(file=path.relative_to(ROOT)):
                ast.parse(path.read_text())
        for path in ROOT.rglob('*.ipynb'):
            with self.subTest(file=path.relative_to(ROOT)):
                notebook = nbformat.read(path, as_version=4)
                nbformat.validate(notebook)
                for cell in notebook.cells:
                    if cell.cell_type == 'code':
                        ast.parse(cell.source)

    def test_markdown_links(self):
        for path in ROOT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith(('mailto:', '#')):
                    continue
                with self.subTest(file=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / target.split('#')[0]).exists())

    def test_temperature_demo_and_missing_lag(self):
        import numpy as np
        import pandas as pd
        folder = ROOT / 'machine-learning/prediccion-temperatura'
        notebook = json.loads((folder / 'notebook.ipynb').read_text())
        namespace = {'display': lambda *_: None}
        previous = Path.cwd()
        try:
            os.chdir(folder)
            with contextlib.redirect_stdout(io.StringIO()):
                for cell in notebook['cells']:
                    if cell['cell_type'] == 'code':
                        exec(''.join(cell['source']), namespace)
                result = namespace['resultado_prediccion']
                self.assertEqual(result['fecha_futura'] - result['fecha_actual'], pd.Timedelta(hours=1))
                self.assertTrue(np.isfinite(result['temperatura_predicha']))
                history = namespace['df_modelo'].copy()
                history.loc[history.index.max() - pd.Timedelta(minutes=30), 'Temperatura'] = np.nan
                missing = namespace['predecir_ultima_hora'](history, namespace['modelo_final'], namespace['variables'])
                self.assertIsNone(missing)
        finally:
            os.chdir(previous)
        import matplotlib.pyplot as plt
        plt.close('all')

    def test_flask_form(self):
        folder = ROOT / 'desarrollo-web/flask-kmeans'
        runpy.run_path(str(folder / 'modelo.py'))
        app = load_module('portfolio_flask', folder / 'app.py').app
        with app.test_client() as client:
            self.assertEqual(client.get('/').status_code, 200)
            response = client.post('/predict', data={'ingresos': '4,5', 'gastos': '3'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('Grupo', response.get_data(as_text=True))
            for value in ['texto', 'nan', 'inf', '-1']:
                response = client.post('/predict', data={'ingresos': value, 'gastos': '3'})
                self.assertEqual(response.status_code, 200)
                self.assertRegex(response.get_data(as_text=True), 'Valores inválidos|valores finitos')

    def test_codecs(self):
        subprocess.run(['node', str(ROOT / 'sensores-iot/pruebas-codecs.cjs')], check=True)

    def test_dashboard_initial_views(self):
        from streamlit.testing.v1 import AppTest
        folder = ROOT / 'analisis-de-datos/dashboard-invernaderos'
        runpy.run_path(str(folder / 'generar_datos_demo.py'), run_name='__main__')
        for filename in ['dashboard.py', 'dashboard_cortinas.py']:
            with self.subTest(app=filename):
                at = AppTest.from_file(str(folder / filename)).run(timeout=45)
                self.assertEqual(len(at.exception), 0, str(at.exception))
                self.assertEqual(len(at.error), 0, str(at.error))
                self.assertGreater(len(at.selectbox), 0)
                if filename == 'dashboard.py':
                    for view in ['WIGA', 'Cortinas', 'Promedio', 'Varianza']:
                        at.radio(key='modo_dashboard').set_value(view).run(timeout=45)
                        self.assertEqual(len(at.exception), 0, f'{view}: {at.exception}')
                        self.assertEqual(len(at.error), 0, f'{view}: {at.error}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
