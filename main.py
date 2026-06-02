"""
================================================================================
MAIN.py - ORQUESTADOR DE TUBERÍA COMPLETA MLOps
================================================================================

Ejecuta secuencialmente:
1. Data Profiling (diagnóstico de calidad)
2. ETL Pipeline (limpieza y validación)
3. ML Training (entrenamiento de modelos)
4. Dashboard (visualización de resultados)

Uso:
    python main.py

Autor: Proyecto Final - MLOps Pipeline
================================================================================
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar módulos
try:
    from sqlalchemy import create_engine
    import pandas as pd
    import sys
    from pathlib import Path
    
    # Agregar carpeta modulos/ al path
    sys.path.insert(0, str(Path(__file__).parent / 'modulos'))
    
    # Importar módulos locales
    from data_profiling import DataProfiler
    from etl_pipeline import ETLPipeline
    from ml_training import TuberiaImputacionML
    from dashboard import DashboardSaludDato
    
except ImportError as e:
    logger.error(f"Error de importación: {e}")
    logger.info("Asegúrate que los módulos están en la raíz del proyecto")
    sys.exit(1)


# ================================================================================
# CONFIGURACIÓN
# ================================================================================

DB_CONFIG = {
    'user': 'catastro_jmm9_user',
    'password': 'W4q6uMkHT6BTaRDUF58XYY7AV2CUatBW',
    'host': 'pg-d7t01mq8qa3s73f28r4g-a.oregon-postgres.render.com',
    'port': '5432',
    'database': 'catastro_jmm9'
}

QUERY_DATOS = """
SELECT 
    nm_mtcla_prdio AS id_predio,
    estrato_pre AS estrato,
    ds_barrio AS barrio_nombre,
    ava_total_ava AS avaluo_total,
    area_con AS area_construida,
    nm_ptje AS puntaje,
    ds_tipo_constru AS tipo_construccion
FROM catastro.insertar_predios_construccion
--LIMIT 100000
"""

CANTIDAD_REGISTROS = "FULL"


# ================================================================================
# FUNCIONES DE UTILIDAD
# ================================================================================

def conectar_postgresql():
    """Establece conexión a PostgreSQL."""
    try:
        url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
              f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(url)
        logger.info("✓ Conexión a PostgreSQL establecida")
        return engine
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        raise


def cargar_datos(engine, query):
    """Carga datos desde PostgreSQL."""
    try:
        logger.info(f"Cargando datos (LIMIT {CANTIDAD_REGISTROS})...")
        conn = engine.raw_connection()
        try:
            df = pd.read_sql_query(query, con=conn)
        finally:
            conn.close()
        logger.info(f"✓ {len(df):,} registros cargados\n")
        return df
    except Exception as e:
        logger.error(f"❌ Error cargando datos: {e}")
        raise


def crear_directorio_outputs():
    """Crea directorio de outputs con estructura clara."""
    base = Path(__file__).parent / 'outputs'
    
    base.mkdir(exist_ok=True)
    (base / 'datos').mkdir(exist_ok=True)
    (base / 'modelos').mkdir(exist_ok=True)
    (base / 'reportes').mkdir(exist_ok=True)
    (base / 'visualizaciones').mkdir(exist_ok=True)
    
    logger.info(f"✓ Estructura de directorios lista en: {base}\n")
    return base


# ================================================================================
# ETAPA 1: DATA PROFILING
# ================================================================================

def ejecutar_data_profiling(df):
    """
    Diagnóstico automatizado de datos.
    """
    logger.info("\n" + "="*80)
    logger.info("ETAPA 1: DATA PROFILING (DIAGNÓSTICO DE CALIDAD)")
    logger.info("="*80 + "\n")

    profiler = DataProfiler(df, nombre_dataset='EAGIC_Catastro')
    perfil = profiler.generar_perfil_completo()
    profiler.imprimir_resumen()

    # Guardar resultados
    timestamp = profiler.timestamp
    ruta_json = profiler.guardar_perfil_json(
        f'outputs/reportes/01_perfil_datos_{timestamp}.json'
    )
    ruta_txt = profiler.generar_reporte_texto(
        f'outputs/reportes/01_reporte_profiling_{timestamp}.txt'
    )

    return profiler, ruta_json, ruta_txt


# ================================================================================
# ETAPA 2: ETL PIPELINE
# ================================================================================

def ejecutar_etl_pipeline(df_original):
    """
    Limpieza, validación y estandarización de datos.
    """
    logger.info("\n" + "="*80)
    logger.info("ETAPA 2: ETL PIPELINE (FILTRO DE PUREZA)")
    logger.info("="*80 + "\n")

    pipeline = ETLPipeline(df_original, nombre='EAGIC_Catastro')
    df_limpio, reporte = pipeline.ejecutar_pipeline_completo(col_pk='id_predio')

    # Guardar resultados
    timestamp = pipeline.timestamp
    ruta_csv = pipeline.guardar_datos_limpios(
        f'outputs/datos/02_datos_limpios_{timestamp}.csv'
    )
    ruta_json = pipeline.guardar_reporte_json(
        f'outputs/reportes/02_reporte_etl_{timestamp}.json'
    )

    return df_limpio, pipeline, ruta_csv, ruta_json


# ================================================================================
# ETAPA 3: ML TRAINING
# ================================================================================

def ejecutar_ml_training(df_limpio):
    """
    Entrenamiento de modelos para imputación inteligente.
    """
    logger.info("\n" + "="*80)
    logger.info("ETAPA 3: ML TRAINING (IMPUTACIÓN INTELIGENTE)")
    logger.info("="*80 + "\n")

    tuberia = TuberiaImputacionML(df_limpio, nombre_dataset='EAGIC_Catastro')
    df_imputado = tuberia.ejecutar_tuberia_completa()

    # Guardar modelos
    tuberia.guardar_modelos(prefijo='outputs/modelos/modelo_catastro')
    timestamp = tuberia.timestamp
    ruta_json = tuberia.guardar_reporte(
        f'outputs/reportes/03_reporte_ml_{timestamp}.json'
    )

    # Guardar datos imputados
    ruta_csv = f'outputs/datos/03_datos_imputados_{timestamp}.csv'
    df_imputado.to_csv(ruta_csv, index=False)
    logger.info(f"✓ Datos imputados guardados: {ruta_csv}")

    return df_imputado, tuberia, ruta_csv, ruta_json


# ================================================================================
# ETAPA 4: DASHBOARD
# ================================================================================

def ejecutar_dashboard(df_original, df_limpio, df_imputado):
    """
    Generación de tablero visual de calidad de datos.
    """
    logger.info("\n" + "="*80)
    logger.info("ETAPA 4: DASHBOARD (TABLERO DE SALUD DEL DATO)")
    logger.info("="*80 + "\n")

    dashboard = DashboardSaludDato(
        df_original=df_original,
        df_limpio=df_limpio,
        df_imputado=df_imputado,
        nombre='EAGIC_Catastro'
    )

    timestamp = dashboard.timestamp
    ruta_html = dashboard.crear_dashboard_html(
        f'outputs/visualizaciones/dashboard_salud_dato_{timestamp}.html'
    )
    ruta_json = dashboard.generar_reporte_json(
        f'outputs/reportes/04_reporte_dashboard_{timestamp}.json'
    )

    return dashboard, ruta_html, ruta_json


# ================================================================================
# REPORTE FINAL
# ================================================================================

def generar_reporte_final(profiler, pipeline, tuberia, dashboard, archivos):
    """
    Genera resumen final del proyecto.
    """
    logger.info("\n" + "#"*80)
    logger.info("# REPORTE FINAL - EJECUCIÓN COMPLETA")
    logger.info("#"*80 + "\n")

    resumen = {
        'timestamp_ejecución': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'dataset': 'EAGIC_Catastro',
        'etapas': {
            'data_profiling': {
                'score_calidad': float(profiler.perfil['calidad']['score_global']),
                'completitud': float(profiler.perfil['calidad']['completitud']),
                'estado': profiler.perfil['calidad']['estado']
            },
            'etl_pipeline': {
                'registros_inicial': pipeline.reporte['etapas']['resumen']['registros_inicial'],
                'registros_final': pipeline.reporte['etapas']['resumen']['registros_final'],
                'porcentaje_retencion': pipeline.reporte['etapas']['resumen']['porcentaje_retencion'],
                'duplicados_eliminados': pipeline.reporte['etapas']['duplicados']['registros_eliminados']
            },
            'ml_training': {
                'modelo_area': tuberia.reporte['area_construida']['modelo_seleccionado'],
                'r2_area': tuberia.reporte['area_construida']['metricas_mejor']['r2'],
                'mae_area': tuberia.reporte['area_construida']['metricas_mejor']['mae'],
                'registros_imputados': {
                    'area_construida': int(archivos['imputados_area']),
                    'puntaje': int(archivos['imputados_puntaje']),
                    'tipo_construccion': int(archivos['imputados_tipo'])
                }
            }
        },
        'archivos_generados': archivos
    }

    # Mostrar resumen en consola
    logger.info("📊 ESTADÍSTICAS GENERALES")
    logger.info(f"  Registros inicial: {resumen['etapas']['etl_pipeline']['registros_inicial']:,}")
    logger.info(f"  Registros final: {resumen['etapas']['etl_pipeline']['registros_final']:,}")
    logger.info(f"  Retencion: {resumen['etapas']['etl_pipeline']['porcentaje_retencion']}%")
    
    logger.info(f"\n🎯 SCORE DE CALIDAD")
    logger.info(f"  Score global: {resumen['etapas']['data_profiling']['score_calidad']}/100")
    logger.info(f"  Estado: {resumen['etapas']['data_profiling']['estado']}")
    
    logger.info(f"\n🤖 MODELOS ENTRENADOS")
    logger.info(f"  area_construida: {resumen['etapas']['ml_training']['modelo_area']} (R² = {resumen['etapas']['ml_training']['r2_area']:.4f})")
    
    logger.info(f"\n📁 ARCHIVOS GENERADOS")
    for categoria, archivos_cat in resumen['archivos_generados'].items():
        if isinstance(archivos_cat, dict):
            logger.info(f"  {categoria}:")
            for arch_nombre, arch_ruta in archivos_cat.items():
                if not isinstance(arch_ruta, (int, float)):
                    logger.info(f"    - {arch_nombre}: {arch_ruta}")
        elif isinstance(archivos_cat, int):
            continue
        else:
            logger.info(f"  {categoria}: {archivos_cat}")

    logger.info("\n" + "#"*80)
    logger.info("# ✅ TUBERÍA COMPLETADA EXITOSAMENTE")
    logger.info("#"*80 + "\n")

    return resumen


# ================================================================================
# MAIN
# ================================================================================

def main():
    """Ejecuta la tubería completa."""
    
    try:
        logger.info("\n" + "="*80)
        logger.info("PROYECTO FINAL: IMPUTACIÓN INTELIGENTE CON MACHINE LEARNING")
        logger.info("="*80 + "\n")

        # Setup
        crear_directorio_outputs()

        # Conexión y carga de datos
        logger.info("PREPARACIÓN DE DATOS\n" + "-"*80 + "\n")
        engine = conectar_postgresql()
        df_original = cargar_datos(engine, QUERY_DATOS)

        # Etapa 1: Data Profiling
        profiler, _, _ = ejecutar_data_profiling(df_original)

        # Etapa 2: ETL Pipeline
        df_limpio, pipeline, _, _ = ejecutar_etl_pipeline(df_original)

        # Etapa 3: ML Training
        df_imputado, tuberia, _, _ = ejecutar_ml_training(df_limpio)

        # Etapa 4: Dashboard
        dashboard, ruta_dashboard, _ = ejecutar_dashboard(df_original, df_limpio, df_imputado)

        # Archivos generados
        archivos_generados = {
            'datos': {
                'original': 'Cargado desde PostgreSQL',
                'limpio': f'outputs/datos/02_datos_limpios_*.csv',
                'imputado': f'outputs/datos/03_datos_imputados_*.csv'
            },
            'modelos': 'outputs/modelos/modelo_catastro_*.pkl (3 modelos)',
            'reportes': 'outputs/reportes/*.json (4 reportes)',
            'visualizaciones': ruta_dashboard,
            'imputados_area': int(df_imputado['area_construida_imputada'].sum()),
            'imputados_puntaje': int(df_imputado['puntaje_imputado'].sum()),
            'imputados_tipo': int(df_imputado['tipo_construccion_imputado'].sum())
        }

        # Reporte final
        generar_reporte_final(profiler, pipeline, tuberia, dashboard, archivos_generados)

        logger.info("Para ver el dashboard, abre en navegador:")
        logger.info(f"  {Path(ruta_dashboard).resolve()}\n")

    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
