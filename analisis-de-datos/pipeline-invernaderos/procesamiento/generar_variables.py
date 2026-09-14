from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "Datos" / "Procesados"
ANALYTIC_DIR = BASE_DIR / "Datos" / "Analiticos"
REPORT_DIR = BASE_DIR / "Datos" / "Reportes"


WIGGA_FILE = PROCESSED_DIR / "wigga_limpio.csv"
CORTINAS_FILE = PROCESSED_DIR / "cortinas_limpio.csv"
ECOWITT_FILE = PROCESSED_DIR / "ecowitt_limpio.csv"
APOGEE_FILE = PROCESSED_DIR / "apogee_limpio.csv"
ANALISIS_APERTURA_FILE = PROCESSED_DIR / "analisis_apertura_limpio.csv"
ANALISIS_APERTURA_AREAS_FILE = PROCESSED_DIR / "analisis_apertura_areas_limpio.csv"


VARIABLES_GENERADAS: list[dict[str, str]] = []


def registrar_variable(dataset: str, variable: str, descripcion: str, razon: str, unidad: str = "") -> None:
    VARIABLES_GENERADAS.append(
        {
            "dataset": dataset,
            "variable": variable,
            "descripcion": descripcion,
            "razon_analitica": razon,
            "unidad": unidad,
        }
    )


def clasificar_periodo_dia(hora: float) -> str | None:
    if pd.isna(hora):
        return None
    hora_entera = int(hora)
    if 0 <= hora_entera <= 5:
        return "madrugada"
    if 6 <= hora_entera <= 11:
        return "manana"
    if 12 <= hora_entera <= 17:
        return "tarde"
    return "noche"


def agregar_variables_temporales(
    df: pd.DataFrame,
    columna_fecha: str,
    dataset: str,
    incluir_ciclos: bool = True,
    incluir_hora: bool = True,
) -> pd.DataFrame:
    df = df.copy()
    fecha = pd.to_datetime(df[columna_fecha], errors="coerce")

    df["anio"] = fecha.dt.year
    df["mes"] = fecha.dt.month
    df["dia_mes"] = fecha.dt.day
    df["dia_semana"] = fecha.dt.dayofweek
    df["dia_anio"] = fecha.dt.dayofyear
    df["semana_anio"] = fecha.dt.isocalendar().week.astype("Int64")
    for variable, descripcion in [
        ("anio", "Anio de la medicion o evento."),
        ("mes", "Mes de la medicion o evento."),
        ("dia_mes", "Dia del mes."),
        ("dia_semana", "Dia de la semana: 0 lunes, 6 domingo."),
        ("dia_anio", "Dia del anio."),
        ("semana_anio", "Semana ISO del anio."),
    ]:
        registrar_variable(
            dataset,
            variable,
            descripcion,
            "Facilita filtros, agrupaciones temporales y comparacion de ciclos diarios.",
        )

    if incluir_hora:
        df["hora_num"] = fecha.dt.hour
        df["minuto_num"] = fecha.dt.minute
        df["hora_decimal"] = df["hora_num"] + (df["minuto_num"] / 60)
        df["periodo_dia"] = df["hora_num"].apply(clasificar_periodo_dia)

        for variable, descripcion in [
            ("hora_num", "Hora entera del dia."),
            ("minuto_num", "Minuto de la hora."),
            ("hora_decimal", "Hora expresada como numero decimal."),
            ("periodo_dia", "Clasificacion simple del momento del dia."),
        ]:
            registrar_variable(
                dataset,
                variable,
                descripcion,
                "Facilita filtros, agrupaciones temporales y comparacion de ciclos diarios.",
            )

    if incluir_ciclos and incluir_hora:
        minutos_dia = df["hora_num"] * 60 + df["minuto_num"]
        df["hora_seno"] = np.sin(2 * np.pi * minutos_dia / 1440)
        df["hora_coseno"] = np.cos(2 * np.pi * minutos_dia / 1440)
        df["dia_anio_seno"] = np.sin(2 * np.pi * df["dia_anio"] / 365)
        df["dia_anio_coseno"] = np.cos(2 * np.pi * df["dia_anio"] / 365)

        for variable, descripcion in [
            ("hora_seno", "Componente ciclico seno de la hora del dia."),
            ("hora_coseno", "Componente ciclico coseno de la hora del dia."),
            ("dia_anio_seno", "Componente ciclico seno del dia del anio."),
            ("dia_anio_coseno", "Componente ciclico coseno del dia del anio."),
        ]:
            registrar_variable(
                dataset,
                variable,
                descripcion,
                "Permite analisis estadistico respetando que el tiempo es circular.",
            )

    return df


def rezago_exacto_por_tiempo(
    df: pd.DataFrame,
    grupo: str,
    fecha: str,
    columna: str,
    delta: pd.Timedelta,
) -> pd.Series:
    resultado = pd.Series(index=df.index, dtype="float64")
    for _, grupo_df in df.groupby(grupo, sort=False):
        grupo_df = grupo_df.sort_values(fecha)
        serie = grupo_df.set_index(fecha)[columna]
        fechas_rezago = grupo_df[fecha] - delta
        resultado.loc[grupo_df.index] = serie.reindex(fechas_rezago).to_numpy()
    return resultado


def rolling_por_tiempo(
    df: pd.DataFrame,
    grupo: str,
    fecha: str,
    columna: str,
    ventana: str,
    funcion: str,
    min_periods: int = 1,
) -> pd.Series:
    resultado = pd.Series(index=df.index, dtype="float64")
    for _, grupo_df in df.groupby(grupo, sort=False):
        grupo_df = grupo_df.sort_values(fecha)
        serie = grupo_df.set_index(fecha)[columna]
        rolling = serie.rolling(ventana, min_periods=min_periods)
        resultado.loc[grupo_df.index] = getattr(rolling, funcion)().to_numpy()
    return resultado


def agregar_variables_wigga() -> pd.DataFrame:
    df = pd.read_csv(WIGGA_FILE, encoding="utf-8-sig")
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    df = df.sort_values(["bloque", "fecha_hora"]).reset_index(drop=True)
    df = agregar_variables_temporales(df, "fecha_hora", "wigga")

    radiacion = df["radiacion_par_umol_m_2_s_1"]
    df["es_dia"] = np.where(radiacion.notna(), np.where(radiacion > 0, 1, 0), np.nan)
    registrar_variable(
        "wigga",
        "es_dia",
        "Indicador 1/0 de presencia de radiacion PAR.",
        "Separa mediciones con luz y sin luz sin borrar los valores cero de radiacion.",
        "0/1",
    )

    df["intervalo_minutos"] = df.groupby("bloque")["fecha_hora"].diff().dt.total_seconds() / 60
    registrar_variable(
        "wigga",
        "intervalo_minutos",
        "Minutos transcurridos desde la medicion anterior del mismo bloque.",
        "Ayuda a detectar saltos, huecos o cambios en frecuencia de medicion.",
        "min",
    )

    df["diferencia_temp_punto_rocio_c"] = df["temperatura_c"] - df["punto_rocio_c"]
    df["riesgo_condensacion"] = np.where(df["diferencia_temp_punto_rocio_c"] <= 2, 1, 0)
    df.loc[df["diferencia_temp_punto_rocio_c"].isna(), "riesgo_condensacion"] = np.nan
    df["amplitud_temperatura_c"] = df["temperatura_max_c"] - df["temperatura_min_c"]
    df["amplitud_humedad_pct"] = df["humedad_max"] - df["humedad_min"]

    for variable, descripcion, unidad, razon in [
        (
            "diferencia_temp_punto_rocio_c",
            "Temperatura menos punto de rocio.",
            "C",
            "Mide cercania a condensacion usando variables medidas por WIGGA.",
        ),
        (
            "riesgo_condensacion",
            "1 si la temperatura esta a 2 C o menos del punto de rocio.",
            "0/1",
            "Permite filtrar momentos de posible condensacion para analisis agronomico.",
        ),
        (
            "amplitud_temperatura_c",
            "Temperatura maxima menos temperatura minima del registro.",
            "C",
            "Resume variabilidad termica del intervalo.",
        ),
        (
            "amplitud_humedad_pct",
            "Humedad maxima menos humedad minima del registro.",
            "%",
            "Resume variabilidad de humedad del intervalo.",
        ),
    ]:
        registrar_variable("wigga", variable, descripcion, razon, unidad)

    cambios = {
        "temperatura_c": "cambio_temperatura_c",
        "humedad_relativa": "cambio_humedad_relativa",
        "dpv_kpa": "cambio_dpv_kpa",
        "radiacion_par_umol_m_2_s_1": "cambio_radiacion_par",
        "gramos_de_agua_g": "cambio_gramos_de_agua_g",
    }
    for origen, destino in cambios.items():
        df[destino] = df.groupby("bloque")[origen].diff()
        registrar_variable(
            "wigga",
            destino,
            f"Cambio frente a la medicion anterior de {origen}.",
            "Describe dinamica inmediata por bloque sin mezclar sensores.",
        )

    rezagos = {
        "1h": pd.Timedelta(hours=1),
        "6h": pd.Timedelta(hours=6),
        "24h": pd.Timedelta(hours=24),
    }
    columnas_rezago = {
        "temperatura_c": "temperatura",
        "humedad_relativa": "humedad",
        "dpv_kpa": "dpv",
        "radiacion_par_umol_m_2_s_1": "radiacion",
    }
    for nombre_rezago, delta in rezagos.items():
        for origen, prefijo in columnas_rezago.items():
            destino = f"{prefijo}_rezago_{nombre_rezago}"
            df[destino] = rezago_exacto_por_tiempo(df, "bloque", "fecha_hora", origen, delta)
            registrar_variable(
                "wigga",
                destino,
                f"Valor exacto de {origen} hace {nombre_rezago}.",
                "Permite comparar el estado actual contra memoria corta y contra el mismo horario previo.",
            )

    df["temperatura_vs_1h"] = df["temperatura_c"] - df["temperatura_rezago_1h"]
    df["temperatura_vs_24h"] = df["temperatura_c"] - df["temperatura_rezago_24h"]
    df["humedad_vs_1h"] = df["humedad_relativa"] - df["humedad_rezago_1h"]
    df["dpv_vs_1h"] = df["dpv_kpa"] - df["dpv_rezago_1h"]
    df["radiacion_vs_1h"] = df["radiacion_par_umol_m_2_s_1"] - df["radiacion_rezago_1h"]

    for variable, descripcion in [
        ("temperatura_vs_1h", "Diferencia de temperatura frente a 1 hora antes."),
        ("temperatura_vs_24h", "Diferencia de temperatura frente al mismo horario del dia anterior."),
        ("humedad_vs_1h", "Diferencia de humedad relativa frente a 1 hora antes."),
        ("dpv_vs_1h", "Diferencia de DPV frente a 1 hora antes."),
        ("radiacion_vs_1h", "Diferencia de radiacion PAR frente a 1 hora antes."),
    ]:
        registrar_variable(
            "wigga",
            variable,
            descripcion,
            "Ayuda a medir tendencia reciente y variacion temporal.",
        )

    ventanas = ["3h", "6h", "24h"]
    columnas_rolling = {
        "temperatura_c": "temperatura",
        "humedad_relativa": "humedad",
        "dpv_kpa": "dpv",
        "radiacion_par_umol_m_2_s_1": "radiacion",
    }
    for ventana in ventanas:
        for origen, prefijo in columnas_rolling.items():
            destino = f"{prefijo}_promedio_{ventana}"
            df[destino] = rolling_por_tiempo(df, "bloque", "fecha_hora", origen, ventana, "mean")
            registrar_variable(
                "wigga",
                destino,
                f"Promedio movil de {origen} en ventana de {ventana}.",
                "Suaviza ruido y resume condiciones recientes por bloque.",
            )

    for ventana in ["3h", "24h"]:
        destino = f"radiacion_acumulada_{ventana}"
        df[destino] = rolling_por_tiempo(
            df,
            "bloque",
            "fecha_hora",
            "radiacion_par_umol_m_2_s_1",
            ventana,
            "sum",
        )
        registrar_variable(
            "wigga",
            destino,
            f"Suma movil de radiacion PAR en ventana de {ventana}.",
            "Resume exposicion reciente a radiacion; los ceros validos se conservan.",
        )

    df["fecha_dia"] = df["fecha_hora"].dt.date
    grupo_dia = df.groupby(["bloque", "fecha_dia"], sort=False)
    df["radiacion_acumulada_dia"] = grupo_dia["radiacion_par_umol_m_2_s_1"].cumsum()
    df["temperatura_max_dia_hasta_ahora"] = grupo_dia["temperatura_c"].cummax()
    df["temperatura_min_dia_hasta_ahora"] = grupo_dia["temperatura_c"].cummin()
    df["humedad_max_dia_hasta_ahora"] = grupo_dia["humedad_relativa"].cummax()
    df["humedad_min_dia_hasta_ahora"] = grupo_dia["humedad_relativa"].cummin()
    df["amplitud_temperatura_dia_hasta_ahora"] = (
        df["temperatura_max_dia_hasta_ahora"] - df["temperatura_min_dia_hasta_ahora"]
    )
    df["amplitud_humedad_dia_hasta_ahora"] = (
        df["humedad_max_dia_hasta_ahora"] - df["humedad_min_dia_hasta_ahora"]
    )
    df = df.drop(columns=["fecha_dia"])

    for variable, descripcion in [
        ("radiacion_acumulada_dia", "Radiacion PAR acumulada dentro del dia por bloque."),
        ("temperatura_max_dia_hasta_ahora", "Temperatura maxima acumulada del dia hasta el registro."),
        ("temperatura_min_dia_hasta_ahora", "Temperatura minima acumulada del dia hasta el registro."),
        ("humedad_max_dia_hasta_ahora", "Humedad maxima acumulada del dia hasta el registro."),
        ("humedad_min_dia_hasta_ahora", "Humedad minima acumulada del dia hasta el registro."),
        ("amplitud_temperatura_dia_hasta_ahora", "Rango termico acumulado del dia hasta el registro."),
        ("amplitud_humedad_dia_hasta_ahora", "Rango de humedad acumulado del dia hasta el registro."),
    ]:
        registrar_variable(
            "wigga",
            variable,
            descripcion,
            "Resume el comportamiento diario progresivo por bloque.",
        )

    return df


def _hora_a_minutos(fecha: pd.Series, hora: pd.Series) -> pd.Series:
    fecha_str = fecha.astype(str)
    hora_str = hora.astype(str)
    dt = pd.to_datetime(fecha_str + " " + hora_str, errors="coerce")
    return dt.dt.hour * 60 + dt.dt.minute


def agregar_variables_cortinas() -> pd.DataFrame:
    df = pd.read_csv(CORTINAS_FILE, encoding="utf-8-sig")
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = agregar_variables_temporales(
        df,
        "fecha",
        "cortinas",
        incluir_ciclos=False,
        incluir_hora=False,
    )

    df["hora_apertura_minuto_dia"] = _hora_a_minutos(df["fecha"], df["hora_apertura"])
    df["hora_cierre_minuto_dia"] = _hora_a_minutos(df["fecha"], df["hora_cierre"])
    df["hora_apertura_decimal"] = df["hora_apertura_minuto_dia"] / 60
    df["hora_cierre_decimal"] = df["hora_cierre_minuto_dia"] / 60
    df["duracion_abierta_min"] = df["hora_cierre_minuto_dia"] - df["hora_apertura_minuto_dia"]
    df.loc[df["duracion_abierta_min"] < 0, "duracion_abierta_min"] = np.nan
    df["tiene_anotacion"] = np.where(df["anotacion"].notna(), 1, 0)
    df["tipo_elemento"] = np.where(
        df["elemento"].astype(str).str.contains("FRENTE", case=False, na=False),
        "frente",
        np.where(df["elemento"].astype(str).str.contains("PUERTA", case=False, na=False), "puerta", "otro"),
    )

    for variable, descripcion, unidad, razon in [
        (
            "hora_apertura_minuto_dia",
            "Hora de apertura convertida a minuto del dia.",
            "min",
            "Permite comparar horarios y graficar distribuciones.",
        ),
        (
            "hora_cierre_minuto_dia",
            "Hora de cierre convertida a minuto del dia.",
            "min",
            "Permite comparar horarios y graficar distribuciones.",
        ),
        (
            "hora_apertura_decimal",
            "Hora de apertura en formato decimal.",
            "hora",
            "Facilita promedios y visualizaciones temporales.",
        ),
        (
            "hora_cierre_decimal",
            "Hora de cierre en formato decimal.",
            "hora",
            "Facilita promedios y visualizaciones temporales.",
        ),
        (
            "duracion_abierta_min",
            "Minutos entre apertura y cierre registrados.",
            "min",
            "Resume cuanto tiempo permanecio abierto el elemento.",
        ),
        (
            "tiene_anotacion",
            "Indicador 1/0 de existencia de observacion.",
            "0/1",
            "Permite separar eventos normales de eventos con novedad.",
        ),
        (
            "tipo_elemento",
            "Clasificacion del elemento como frente, puerta u otro.",
            "categoria",
            "Facilita comparaciones entre frentes y puertas.",
        ),
    ]:
        registrar_variable("cortinas", variable, descripcion, razon, unidad)

    return df


def sector_viento(grados: object) -> str | None:
    if pd.isna(grados):
        return None
    sectores = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    indice = int(((float(grados) + 22.5) % 360) // 45)
    return sectores[indice]


def agregar_variables_ecowitt() -> pd.DataFrame:
    df = pd.read_csv(ECOWITT_FILE, encoding="utf-8-sig")
    df["timestamp_recepcion"] = pd.to_datetime(df["timestamp_recepcion"], errors="coerce")
    df = df.sort_values("timestamp_recepcion").reset_index(drop=True)
    df = agregar_variables_temporales(df, "timestamp_recepcion", "ecowitt")

    df["intervalo_minutos"] = df["timestamp_recepcion"].diff().dt.total_seconds() / 60
    radianes = np.deg2rad(df["direccion_viento_grados"])
    df["viento_u_mps"] = df["velocidad_viento_mps"] * np.sin(radianes)
    df["viento_v_mps"] = df["velocidad_viento_mps"] * np.cos(radianes)
    df["sector_viento"] = df["direccion_viento_grados"].apply(sector_viento)
    df["cambio_temperatura_c"] = df["temperatura_c"].diff()
    df["temperatura_promedio_1h"] = (
        df.set_index("timestamp_recepcion")["temperatura_c"].rolling("1h", min_periods=1).mean().to_numpy()
    )
    df["humedad_promedio_1h"] = (
        df.set_index("timestamp_recepcion")["humedad_pct"].rolling("1h", min_periods=1).mean().to_numpy()
    )

    for variable, descripcion, unidad, razon in [
        ("intervalo_minutos", "Minutos desde la medicion anterior.", "min", "Detecta huecos de medicion."),
        ("viento_u_mps", "Componente este-oeste del viento.", "m/s", "Permite analizar direccion como variable numerica."),
        ("viento_v_mps", "Componente norte-sur del viento.", "m/s", "Permite analizar direccion como variable numerica."),
        ("sector_viento", "Direccion del viento agrupada en 8 sectores.", "categoria", "Facilita filtros y conteos."),
        ("cambio_temperatura_c", "Cambio de temperatura frente a medicion anterior.", "C", "Mide dinamica inmediata."),
        ("temperatura_promedio_1h", "Promedio movil de temperatura en 1 hora.", "C", "Suaviza ruido reciente."),
        ("humedad_promedio_1h", "Promedio movil de humedad en 1 hora.", "%", "Suaviza ruido reciente."),
    ]:
        registrar_variable("ecowitt", variable, descripcion, razon, unidad)

    return df


def agregar_variables_apogee() -> pd.DataFrame:
    df = pd.read_csv(APOGEE_FILE, encoding="utf-8-sig")
    df["timestamp_recepcion"] = pd.to_datetime(df["timestamp_recepcion"], errors="coerce")
    df = df.sort_values("timestamp_recepcion").reset_index(drop=True)
    df = agregar_variables_temporales(df, "timestamp_recepcion", "apogee")

    df["intervalo_minutos"] = df["timestamp_recepcion"].diff().dt.total_seconds() / 60
    df["hay_luz"] = np.where((df["ppfd_apogee_umol_m2s"] > 0) | (df["luz_lux"] > 0), 1, 0)
    df["ppfd_promedio_1h"] = (
        df.set_index("timestamp_recepcion")["ppfd_apogee_umol_m2s"]
        .rolling("1h", min_periods=1)
        .mean()
        .to_numpy()
    )
    df["lux_promedio_1h"] = df.set_index("timestamp_recepcion")["luz_lux"].rolling("1h", min_periods=1).mean().to_numpy()

    for variable, descripcion, unidad, razon in [
        ("intervalo_minutos", "Minutos desde la medicion anterior.", "min", "Detecta huecos de medicion."),
        ("hay_luz", "Indicador 1/0 de presencia de luz medida.", "0/1", "Separa periodos con luz y sin luz."),
        ("ppfd_promedio_1h", "Promedio movil de PPFD en 1 hora.", "umol/m2/s", "Suaviza variabilidad reciente."),
        ("lux_promedio_1h", "Promedio movil de lux en 1 hora.", "lux", "Suaviza variabilidad reciente."),
    ]:
        registrar_variable("apogee", variable, descripcion, razon, unidad)

    return df


def _division_segura(numerador: pd.Series, denominador: pd.Series) -> pd.Series:
    resultado = numerador / denominador
    resultado = resultado.replace([np.inf, -np.inf], np.nan)
    return resultado


def agregar_variables_analisis_apertura() -> pd.DataFrame:
    df = pd.read_csv(ANALISIS_APERTURA_FILE, encoding="utf-8-sig")
    df["bloque_codigo"] = df["bloque"].astype(str).str.extract(r"(\d+)")[0].map(lambda x: f"B{x}" if pd.notna(x) else np.nan)
    registrar_variable(
        "analisis_apertura",
        "bloque_codigo",
        "Codigo de bloque en formato B27, B34, B35 o B38.",
        "Permite unir esta tabla con WIGGA y Cortinas.",
    )

    grupos_apertura = ["lateral", "frontal", "culatas"]
    for grupo in grupos_apertura:
        real = f"apertura_{grupo}_real_m"
        maxima = f"apertura_{grupo}_maxima_permitida_m"
        teorica = f"apertura_{grupo}_teorica_m"
        if {real, maxima, teorica}.issubset(df.columns):
            df[real] = pd.to_numeric(df[real], errors="coerce")
            df[maxima] = pd.to_numeric(df[maxima], errors="coerce")
            df[teorica] = pd.to_numeric(df[teorica], errors="coerce")
            df[f"brecha_apertura_{grupo}_m"] = df[maxima] - df[real]
            df[f"uso_apertura_{grupo}_pct"] = _division_segura(df[real], df[maxima]) * 100
            df[f"apertura_{grupo}_real_vs_teorica_pct"] = _division_segura(df[real], df[teorica]) * 100

            for variable, descripcion in [
                (f"brecha_apertura_{grupo}_m", f"Diferencia entre apertura maxima permitida y real para {grupo}."),
                (f"uso_apertura_{grupo}_pct", f"Porcentaje de uso de apertura maxima permitida para {grupo}."),
                (
                    f"apertura_{grupo}_real_vs_teorica_pct",
                    f"Porcentaje de apertura real frente a apertura teorica para {grupo}.",
                ),
            ]:
                registrar_variable(
                    "analisis_apertura",
                    variable,
                    descripcion,
                    "Ayuda a comparar capacidad teorica, permitida y real por bloque.",
                )

    return df


def agregar_variables_analisis_apertura_areas() -> pd.DataFrame:
    df = pd.read_csv(ANALISIS_APERTURA_AREAS_FILE, encoding="utf-8-sig")
    df["bloque_codigo"] = df["bloque"].astype(str).str.extract(r"(\d+)")[0].map(lambda x: f"B{x}" if pd.notna(x) else np.nan)
    registrar_variable(
        "analisis_apertura_areas",
        "bloque_codigo",
        "Codigo de bloque en formato B27, B34, B35 o B38.",
        "Permite unir esta tabla con WIGGA y Cortinas.",
    )

    columnas_numericas = [col for col in df.columns if col not in {"bloque", "bloque_codigo"}]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if {"total_area_real_m2", "total_area_maxima_permitida_m2"}.issubset(df.columns):
        df["uso_area_maxima_pct"] = _division_segura(
            df["total_area_real_m2"],
            df["total_area_maxima_permitida_m2"],
        ) * 100
        df["brecha_ventilacion_pct_maxima"] = _division_segura(
            df["brecha_de_ventilacion_max_permitida_real_m2"],
            df["total_area_maxima_permitida_m2"],
        ) * 100
        registrar_variable(
            "analisis_apertura_areas",
            "uso_area_maxima_pct",
            "Porcentaje de area real frente al area maxima permitida.",
            "Resume aprovechamiento operativo de ventilacion instalada.",
            "%",
        )
        registrar_variable(
            "analisis_apertura_areas",
            "brecha_ventilacion_pct_maxima",
            "Brecha de ventilacion como porcentaje del area maxima permitida.",
            "Permite comparar perdidas entre bloques de distinto tamano.",
            "%",
        )

    if {"total_area_real_m2", "total_area_teorica_m2"}.issubset(df.columns):
        df["uso_area_teorica_pct"] = _division_segura(df["total_area_real_m2"], df["total_area_teorica_m2"]) * 100
        registrar_variable(
            "analisis_apertura_areas",
            "uso_area_teorica_pct",
            "Porcentaje de area real frente al area teorica.",
            "Mide desempeno real frente al diseno ideal.",
            "%",
        )

    if "perdida_operativa" in df.columns:
        df["perdida_operativa_pct"] = df["perdida_operativa"] * 100
        registrar_variable(
            "analisis_apertura_areas",
            "perdida_operativa_pct",
            "Perdida operativa expresada como porcentaje.",
            "Hace legible el indicador calculado en el Excel original.",
            "%",
        )

    return df


def exportar_csv(nombre: str, df: pd.DataFrame) -> None:
    ANALYTIC_DIR.mkdir(parents=True, exist_ok=True)
    ruta = ANALYTIC_DIR / nombre
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"{nombre}: {len(df):,} filas x {len(df.columns):,} columnas")


def exportar_reportes(datasets: dict[str, pd.DataFrame]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(VARIABLES_GENERADAS).drop_duplicates().to_csv(
        REPORT_DIR / "variables_generadas.csv",
        index=False,
        encoding="utf-8-sig",
    )

    nulos = []
    for nombre, df in datasets.items():
        for columna, cantidad in df.isna().sum().items():
            nulos.append(
                {
                    "dataset": nombre,
                    "columna": columna,
                    "nulos": int(cantidad),
                    "porcentaje_nulos": round(float(cantidad / len(df) * 100), 2) if len(df) else 0,
                }
            )
    pd.DataFrame(nulos).to_csv(REPORT_DIR / "nulos_variables.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    datasets = {
        "wigga": agregar_variables_wigga(),
        "cortinas": agregar_variables_cortinas(),
        "ecowitt": agregar_variables_ecowitt(),
        "apogee": agregar_variables_apogee(),
        "analisis_apertura": agregar_variables_analisis_apertura(),
        "analisis_apertura_areas": agregar_variables_analisis_apertura_areas(),
    }

    exportar_csv("wigga_variables.csv", datasets["wigga"])
    exportar_csv("cortinas_variables.csv", datasets["cortinas"])
    exportar_csv("ecowitt_variables.csv", datasets["ecowitt"])
    exportar_csv("apogee_variables.csv", datasets["apogee"])
    exportar_csv("analisis_apertura_variables.csv", datasets["analisis_apertura"])
    exportar_csv("analisis_apertura_areas_variables.csv", datasets["analisis_apertura_areas"])
    exportar_reportes(datasets)
    print(f"reportes: {REPORT_DIR}")


if __name__ == "__main__":
    main()
