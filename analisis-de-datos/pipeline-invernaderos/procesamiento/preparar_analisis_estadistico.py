from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
ANALYTIC_DIR = BASE_DIR / "Datos" / "Analiticos"
REPORT_DIR = BASE_DIR / "Datos" / "Reportes"


DATASETS = {
    "wigga": {
        "path": ANALYTIC_DIR / "wigga_variables.csv",
        "time_col": "fecha_hora",
        "key_cols": ["fecha_hora", "bloque"],
    },
    "cortinas": {
        "path": ANALYTIC_DIR / "cortinas_variables.csv",
        "time_col": "fecha",
        "key_cols": ["fecha", "bloque", "lado", "elemento"],
    },
    "ecowitt": {
        "path": ANALYTIC_DIR / "ecowitt_variables.csv",
        "time_col": "timestamp_recepcion",
        "key_cols": ["timestamp_recepcion"],
    },
    "apogee": {
        "path": ANALYTIC_DIR / "apogee_variables.csv",
        "time_col": "timestamp_recepcion",
        "key_cols": ["timestamp_recepcion"],
    },
    "analisis_apertura": {
        "path": ANALYTIC_DIR / "analisis_apertura_variables.csv",
        "time_col": None,
        "key_cols": ["bloque"],
    },
    "analisis_apertura_areas": {
        "path": ANALYTIC_DIR / "analisis_apertura_areas_variables.csv",
        "time_col": None,
        "key_cols": ["bloque"],
    },
}


def cargar_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo analitico: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def clasificar_columnas(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numericas = list(df.select_dtypes(include="number").columns)
    categoricas = [col for col in df.columns if col not in numericas]
    return numericas, categoricas


def calcular_outliers_iqr(df: pd.DataFrame, dataset: str, numericas: list[str]) -> list[dict[str, object]]:
    registros = []
    for columna in numericas:
        serie = pd.to_numeric(df[columna], errors="coerce").dropna()
        if serie.empty or len(serie) < 20 or serie.nunique(dropna=True) <= 5:
            continue
        q1 = serie.quantile(0.25)
        q3 = serie.quantile(0.75)
        iqr = q3 - q1
        if iqr <= 0:
            continue
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr
        outliers = serie[(serie < limite_inferior) | (serie > limite_superior)]
        registros.append(
            {
                "dataset": dataset,
                "columna": columna,
                "q1": round(float(q1), 6),
                "q3": round(float(q3), 6),
                "iqr": round(float(iqr), 6),
                "limite_inferior": round(float(limite_inferior), 6),
                "limite_superior": round(float(limite_superior), 6),
                "posibles_outliers": int(len(outliers)),
                "porcentaje_outliers": round(float(len(outliers) / len(serie) * 100), 4),
                "nota": "Revisar visualmente antes de eliminar.",
            }
        )
    return registros


def describir_numericas(df: pd.DataFrame, dataset: str, numericas: list[str]) -> list[dict[str, object]]:
    registros = []
    for columna in numericas:
        serie = pd.to_numeric(df[columna], errors="coerce")
        validos = serie.dropna()
        if validos.empty:
            continue
        registros.append(
            {
                "dataset": dataset,
                "columna": columna,
                "registros_validos": int(validos.count()),
                "nulos": int(serie.isna().sum()),
                "media": round(float(validos.mean()), 6),
                "mediana": round(float(validos.median()), 6),
                "desviacion_estandar": round(float(validos.std()), 6) if len(validos) > 1 else 0,
                "minimo": round(float(validos.min()), 6),
                "q1": round(float(validos.quantile(0.25)), 6),
                "q3": round(float(validos.quantile(0.75)), 6),
                "maximo": round(float(validos.max()), 6),
            }
        )
    return registros


def describir_categoricas(df: pd.DataFrame, dataset: str, categoricas: list[str]) -> list[dict[str, object]]:
    registros = []
    for columna in categoricas:
        serie = df[columna]
        moda = serie.mode(dropna=True)
        registros.append(
            {
                "dataset": dataset,
                "columna": columna,
                "registros_validos": int(serie.notna().sum()),
                "nulos": int(serie.isna().sum()),
                "valores_unicos": int(serie.nunique(dropna=True)),
                "valor_mas_frecuente": moda.iloc[0] if not moda.empty else None,
            }
        )
    return registros


def resumen_dataset(nombre: str, df: pd.DataFrame, config: dict[str, object]) -> dict[str, object]:
    time_col = config.get("time_col")
    key_cols = list(config.get("key_cols", []))
    numericas, categoricas = clasificar_columnas(df)

    inicio = None
    fin = None
    fechas_invalidas = None
    if time_col and time_col in df.columns:
        fechas = pd.to_datetime(df[time_col], errors="coerce")
        inicio = fechas.min()
        fin = fechas.max()
        fechas_invalidas = int(fechas.isna().sum())

    duplicados_llave = None
    if set(key_cols).issubset(df.columns):
        duplicados_llave = int(df.duplicated(key_cols).sum())

    return {
        "dataset": nombre,
        "filas": len(df),
        "columnas": len(df.columns),
        "columnas_numericas": len(numericas),
        "columnas_categoricas": len(categoricas),
        "nulos_totales": int(df.isna().sum().sum()),
        "duplicados_exactos": int(df.duplicated().sum()),
        "duplicados_llave": duplicados_llave,
        "columna_tiempo": time_col,
        "fechas_invalidas": fechas_invalidas,
        "fecha_inicio": inicio,
        "fecha_fin": fin,
        "estado": "listo_para_estadistica",
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    resumen = []
    estadistica_numerica = []
    estadistica_categorica = []
    outliers = []

    for nombre, config in DATASETS.items():
        df = cargar_dataset(config["path"])
        numericas, categoricas = clasificar_columnas(df)

        resumen.append(resumen_dataset(nombre, df, config))
        estadistica_numerica.extend(describir_numericas(df, nombre, numericas))
        estadistica_categorica.extend(describir_categoricas(df, nombre, categoricas))
        outliers.extend(calcular_outliers_iqr(df, nombre, numericas))

    pd.DataFrame(resumen).to_csv(
        REPORT_DIR / "preparacion_analisis_estadistico.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(estadistica_numerica).to_csv(
        REPORT_DIR / "estadistica_descriptiva_numerica.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(estadistica_categorica).to_csv(
        REPORT_DIR / "estadistica_descriptiva_categorica.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(outliers).to_csv(
        REPORT_DIR / "posibles_outliers_iqr.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("preparacion_analisis_estadistico.csv generado")
    print("estadistica_descriptiva_numerica.csv generado")
    print("estadistica_descriptiva_categorica.csv generado")
    print("posibles_outliers_iqr.csv generado")


if __name__ == "__main__":
    main()
