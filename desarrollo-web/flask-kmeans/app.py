from pathlib import Path

import numpy as np
from flask import Flask, render_template, request
from joblib import load

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
kmeans = load(BASE_DIR / 'modelo_kmeans.pkl')


def get_group_label(label):
    mapping = {0: 'Grupo 1', 1: 'Grupo 2'}
    return mapping.get(int(label), 'Desconocido')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        ingresos = float(request.form.get('ingresos', '0').replace(',', '.'))
        gastos = float(request.form.get('gastos', '0').replace(',', '.'))
    except ValueError:
        return render_template('index.html', error='Valores inválidos')

    if not np.isfinite([ingresos, gastos]).all() or ingresos < 0 or gastos < 0:
        return render_template('index.html', error='Usa valores finitos mayores o iguales a cero')

    X_new = np.array([[ingresos, gastos]])
    label = kmeans.predict(X_new)[0]
    group = get_group_label(label)
    return render_template('index.html', ingresos=ingresos, gastos=gastos, group=group)


if __name__ == '__main__':
    app.run()
