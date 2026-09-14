"""Datos artificiales para comprobar el flujo; no representan mediciones de campo."""
from pathlib import Path
import numpy as np
import pandas as pd


def main():
    rng = np.random.default_rng(42)
    fechas = pd.date_range('2026-03-01', periods=21 * 48, freq='30min')
    horas = fechas.hour + fechas.minute / 60
    temperatura = 20 + 5 * np.sin(2 * np.pi * (horas - 7) / 24)
    temperatura += rng.normal(0, 0.35, len(fechas))
    output = Path(__file__).resolve().parent / 'datos/temperatura_sintetica.csv'
    output.parent.mkdir(exist_ok=True)
    pd.DataFrame({'DateTime': fechas, 'Temperatura': temperatura}).to_csv(
        output, index=False, sep=';', decimal=',', float_format='%.3f'
    )
    print(f'Datos sintéticos: {len(fechas)} registros -> {output.name}')


if __name__ == '__main__':
    main()
