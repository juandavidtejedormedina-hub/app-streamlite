from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "Datos" / "Raw" / "Datos Excel.xlsx"
OUTPUT_DIR = BASE_DIR / "Datos" / "Procesados"
REPORT_DIR = BASE_DIR / "Datos" / "Reportes"


WIGGA_SHEETS = {
    "WIGGA bloque 38": "B38",
    "WIGGA bloque 27": "B27",
    "WIGGA bloque 35": "B35",
    "WIGGA bloque 34": "B34",
}

CORTINAS_SHEETS = {
    "Cortinas BLOQUE 38": "B38",
    "Cortinas BLOQUE 27": "B27",
    "Cortinas BLOQUE 35": "B35",
    "Cortinas BLOQUE 34": "B34",
}


reporte_limpieza: list[dict[str, object]] = []


def normalizar_columna(nombre: object) -> str:
    texto = str(nombre).strip().lower()
    texto = texto.replace("µ", "u")
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    texto = texto.replace("°", "")
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = re.sub(r"_+", "_", texto).strip("_")
    return texto


def limpiar_textos(df: pd.DataFrame) -> pd.DataFrame:
    columnas_texto = [
        col
        for col in df.columns
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])
    ]
    for col in columnas_texto:
        df[col] = df[col].map(lambda valor: valor.strip() if isinstance(valor, str) else valor)
        df[col] = df[col].replace("", pd.NA)
    return df


def quitar_duplicados_exactos(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    filas_antes = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    reporte_limpieza.append(
        {
            "dataset": dataset,
            "regla": "duplicados_exactos",
            "filas_antes": filas_antes,
            "filas_despues": len(df),
            "filas_removidas": filas_antes - len(df),
        }
    )
    return df


def registrar_remocion(dataset: str, regla: str, filas_antes: int, filas_despues: int) -> None:
    reporte_limpieza.append(
        {
            "dataset": dataset,
            "regla": regla,
            "filas_antes": filas_antes,
            "filas_despues": filas_despues,
            "filas_removidas": filas_antes - filas_despues,
        }
    )


def extraer_numero_bloque(codigo_bloque: str) -> str:
    return codigo_bloque.replace("B", "")


def limpiar_wigga() -> pd.DataFrame:
    tablas = []

    for hoja, bloque in WIGGA_SHEETS.items():
        df = pd.read_excel(RAW_FILE, sheet_name=hoja)
        df.columns = [normalizar_columna(col) for col in df.columns]

        bloque_numero = extraer_numero_bloque(bloque)
        rename_map = {}
        for col in df.columns:
            limpio = col.replace(f"_{bloque.lower()}_", "_")
            limpio = limpio.removesuffix(f"_{bloque.lower()}")
            limpio = limpio.replace(f"b{bloque_numero}", "")
            limpio = re.sub(r"_+", "_", limpio).strip("_")
            rename_map[col] = limpio

        df = df.rename(columns=rename_map)
        df = limpiar_textos(df)
        df["bloque"] = bloque
        df["hoja_origen"] = hoja
        df["fecha_hora"] = pd.to_datetime(
            df["fecha"].astype(str) + " " + df["hora"].astype(str),
            errors="coerce",
        )

        filas_antes = len(df)
        df = df.dropna(subset=["fecha_hora"])
        registrar_remocion(f"wigga_{bloque}", "fecha_hora_vacia_o_invalida", filas_antes, len(df))

        columnas_ordenadas = ["fecha_hora", "fecha", "hora", "bloque", "hoja_origen"]
        columnas_ordenadas += [col for col in df.columns if col not in columnas_ordenadas]
        df = df[columnas_ordenadas]
        tablas.append(df)

    wigga = pd.concat(tablas, ignore_index=True)
    wigga = quitar_duplicados_exactos(wigga, "wigga")
    wigga = wigga.sort_values(["bloque", "fecha_hora"]).reset_index(drop=True)
    return wigga


def _limpiar_hora(valor: object) -> str | None:
    if pd.isna(valor):
        return None
    if hasattr(valor, "strftime"):
        return valor.strftime("%H:%M")
    texto = str(valor).strip()
    if not texto:
        return None
    return texto[:5]


def limpiar_cortinas() -> pd.DataFrame:
    registros = []

    for hoja, bloque in CORTINAS_SHEETS.items():
        raw = pd.read_excel(RAW_FILE, sheet_name=hoja, header=None)
        datos = raw.iloc[3:].copy()

        for _, row in datos.iterrows():
            fecha = pd.to_datetime(row.iloc[0], errors="coerce")
            if pd.isna(fecha):
                continue

            registros.append(
                {
                    "fecha": fecha.date().isoformat(),
                    "bloque": bloque,
                    "hoja_origen": hoja,
                    "lado": "A",
                    "elemento": row.iloc[7],
                    "hora_apertura": _limpiar_hora(row.iloc[1]),
                    "porcentaje_apertura": pd.to_numeric(row.iloc[2], errors="coerce"),
                    "duracion_apertura_min": pd.to_numeric(row.iloc[3], errors="coerce"),
                    "hora_cierre": _limpiar_hora(row.iloc[4]),
                    "porcentaje_cierre": pd.to_numeric(row.iloc[5], errors="coerce"),
                    "duracion_cierre_min": pd.to_numeric(row.iloc[6], errors="coerce"),
                    "anotacion": row.iloc[8] if not pd.isna(row.iloc[8]) else None,
                    "culatas_pct": pd.to_numeric(row.iloc[17], errors="coerce"),
                }
            )

            registros.append(
                {
                    "fecha": fecha.date().isoformat(),
                    "bloque": bloque,
                    "hoja_origen": hoja,
                    "lado": "B",
                    "elemento": row.iloc[15],
                    "hora_apertura": _limpiar_hora(row.iloc[9]),
                    "porcentaje_apertura": pd.to_numeric(row.iloc[10], errors="coerce"),
                    "duracion_apertura_min": pd.to_numeric(row.iloc[11], errors="coerce"),
                    "hora_cierre": _limpiar_hora(row.iloc[12]),
                    "porcentaje_cierre": pd.to_numeric(row.iloc[13], errors="coerce"),
                    "duracion_cierre_min": pd.to_numeric(row.iloc[14], errors="coerce"),
                    "anotacion": row.iloc[16] if not pd.isna(row.iloc[16]) else None,
                    "culatas_pct": pd.to_numeric(row.iloc[17], errors="coerce"),
                }
            )

    cortinas = pd.DataFrame(registros)
    cortinas = limpiar_textos(cortinas)
    filas_antes = len(cortinas)
    cortinas = cortinas.dropna(subset=["elemento"], how="all")
    registrar_remocion("cortinas", "elemento_vacio", filas_antes, len(cortinas))
    cortinas = quitar_duplicados_exactos(cortinas, "cortinas")
    cortinas = cortinas.sort_values(["bloque", "fecha", "lado", "elemento"]).reset_index(drop=True)
    return cortinas


def limpiar_tabla_simple(hoja: str, dataset: str) -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, sheet_name=hoja)
    df.columns = [normalizar_columna(col) for col in df.columns]
    df = limpiar_textos(df)
    return quitar_duplicados_exactos(df, dataset)


def _leer_tabla_analisis_apertura(header_row: int, first_data_row: int, last_data_row: int) -> pd.DataFrame:
    raw = pd.read_excel(RAW_FILE, sheet_name="Analisis Apertura", header=None)
    df = raw.iloc[first_data_row:last_data_row].copy()
    df.columns = [normalizar_columna(col) for col in raw.iloc[header_row]]
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    df = df[[col for col in df.columns if col and not col.startswith("unnamed")]]
    df = limpiar_textos(df)

    if "bloque" in df.columns:
        filas_antes = len(df)
        df = df[df["bloque"].astype(str).str.match(r"Bloque\s+\d+", na=False)]
        registrar_remocion("analisis_apertura", "filas_sin_bloque", filas_antes, len(df))

    for col in df.columns:
        if col != "bloque":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)


def limpiar_analisis_apertura() -> pd.DataFrame:
    df = _leer_tabla_analisis_apertura(header_row=3, first_data_row=4, last_data_row=8)
    return quitar_duplicados_exactos(df, "analisis_apertura")


def limpiar_analisis_apertura_areas() -> pd.DataFrame:
    df = _leer_tabla_analisis_apertura(header_row=10, first_data_row=11, last_data_row=15)
    return quitar_duplicados_exactos(df, "analisis_apertura_areas")


def exportar_csv(nombre: str, df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUT_DIR / nombre
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"{nombre}: {len(df):,} filas x {len(df.columns):,} columnas")


def exportar_reportes(datasets: dict[str, pd.DataFrame]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    resumen = []
    nulos = []
    duplicados_llave = []

    llaves = {
        "wigga": ["fecha_hora", "bloque"],
        "cortinas": ["fecha", "bloque", "lado", "elemento"],
        "ecowitt": ["timestamp_recepcion"],
        "apogee": ["timestamp_recepcion"],
        "analisis_apertura": ["bloque"],
        "analisis_apertura_areas": ["bloque"],
    }

    for nombre, df in datasets.items():
        resumen.append(
            {
                "dataset": nombre,
                "filas": len(df),
                "columnas": len(df.columns),
                "duplicados_exactos": int(df.duplicated().sum()),
            }
        )

        for columna, cantidad in df.isna().sum().items():
            nulos.append(
                {
                    "dataset": nombre,
                    "columna": columna,
                    "nulos": int(cantidad),
                    "porcentaje_nulos": round(float(cantidad / len(df) * 100), 2) if len(df) else 0,
                }
            )

        llave = llaves.get(nombre, [])
        if set(llave).issubset(df.columns):
            duplicados_llave.append(
                {
                    "dataset": nombre,
                    "llave": ", ".join(llave),
                    "duplicados_por_llave": int(df.duplicated(llave).sum()),
                    "nota": "Revisar antes de eliminar; pueden ser eventos validos.",
                }
            )

    pd.DataFrame(resumen).to_csv(REPORT_DIR / "resumen_limpieza.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(nulos).to_csv(REPORT_DIR / "nulos_por_columna.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(duplicados_llave).to_csv(
        REPORT_DIR / "duplicados_por_llave.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(reporte_limpieza).to_csv(
        REPORT_DIR / "reglas_aplicadas.csv",
        index=False,
        encoding="utf-8-sig",
    )


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"No se encontro el archivo fuente: {RAW_FILE}")

    datasets = {
        "wigga": limpiar_wigga(),
        "cortinas": limpiar_cortinas(),
        "ecowitt": limpiar_tabla_simple("EcoWitt", "ecowitt"),
        "apogee": limpiar_tabla_simple("Apogge", "apogee"),
        "analisis_apertura": limpiar_analisis_apertura(),
        "analisis_apertura_areas": limpiar_analisis_apertura_areas(),
    }

    exportar_csv("wigga_limpio.csv", datasets["wigga"])
    exportar_csv("cortinas_limpio.csv", datasets["cortinas"])
    exportar_csv("ecowitt_limpio.csv", datasets["ecowitt"])
    exportar_csv("apogee_limpio.csv", datasets["apogee"])
    exportar_csv("analisis_apertura_limpio.csv", datasets["analisis_apertura"])
    exportar_csv("analisis_apertura_areas_limpio.csv", datasets["analisis_apertura_areas"])
    exportar_reportes(datasets)
    print(f"reportes: {REPORT_DIR}")


if __name__ == "__main__":
    main()
