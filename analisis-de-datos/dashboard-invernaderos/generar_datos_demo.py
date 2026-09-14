"""Genera dos Excel artificiales, reproducibles y sin información empresarial."""
from pathlib import Path
import numpy as np
import pandas as pd


def main():
    out = Path(__file__).resolve().parent / 'datos'
    out.mkdir(exist_ok=True)
    rng = np.random.default_rng(42)
    fechas = pd.date_range('2026-03-01', periods=7 * 48, freq='30min')
    horas = fechas.hour + fechas.minute / 60
    columnas_cortinas = [
        'Fecha', 'Hora Apertura A', '% Apertura A', 'Duracion Apertura A',
        'Hora Cierre A', '% Cierre A', 'Duracion Cierre A', 'Frente A', 'Anotacion A',
        'Hora Apertura B', '% Apertura B', 'Duracion Apertura B', 'Hora Cierre B',
        '% Cierre B', 'Duracion Cierre B', 'Puerta B', 'Anotacion B', 'Culatas %'
    ]
    with pd.ExcelWriter(out / 'variables_sinteticas.xlsx', engine='openpyxl') as writer_v, \
         pd.ExcelWriter(out / 'cortinas_sinteticas.xlsx', engine='openpyxl') as writer_c:
        for i, bloque in enumerate(['27', '34', '35', '38']):
            ciclo = np.sin(2 * np.pi * (horas - 7) / 24)
            df = pd.DataFrame({
                'DateTime': fechas,
                'Temperatura': 20 + 4 * ciclo + i * .4 + rng.normal(0, .3, len(fechas)),
                'Humedad Relativa': 72 - 12 * ciclo + rng.normal(0, 1, len(fechas)),
                'Radiación PAR': np.maximum(0, 600 * ciclo),
                'Gramos de agua': 12 + ciclo + rng.normal(0, .1, len(fechas)),
            })
            df.to_excel(writer_v, sheet_name=f'B{bloque}', index=False)
            rows = []
            for fecha in pd.date_range('2026-03-01', periods=7):
                rows.append([fecha, '08:00:00', 60, 5, '17:00:00', 0, 5,
                             'Frente A', 'Ejemplo sintético', '09:00:00', 50, 5,
                             '16:00:00', 0, 5, 'Puerta B', 'Ejemplo sintético', 20])
            pd.DataFrame(rows, columns=columnas_cortinas).to_excel(
                writer_c, sheet_name=f'B{bloque}', index=False
            )
    print('Excel de demostración generados: cuatro bloques, siete días, datos sintéticos.')


if __name__ == '__main__':
    main()
