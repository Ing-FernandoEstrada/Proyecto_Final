"""
================================================================================
01_DATA_PROFILING.py - DIAGNÓSTICO AUTOMATIZADO DE CALIDAD DE DATOS
================================================================================

Módulo de perfilado exhaustivo de datos:
- Detecta valores nulos, ceros erróneos, duplicados
- Analiza distribuciones, outliers, inconsistencias
- Genera reporte JSON para monitoreo continuo
- Cálculo de confiabilidad por columna

Salida: perfil_datos_TIMESTAMP.json + reporte_profiling.txt

Autor: Proyecto Final - MLOps Data Quality
================================================================================
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:,.2f}'.format)


class DataProfiler:
    """
    Perfilador automático de datasets.
    Genera diagnóstico exhaustivo de calidad de datos.
    """

    def __init__(self, df, nombre_dataset='dataset'):
        """
        Args:
            df: DataFrame a analizar
            nombre_dataset: Nombre del dataset (para logging)
        """
        self.df = df.copy()
        self.nombre_dataset = nombre_dataset
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.perfil = {}

    def perfil_basico(self):
        """Estadísticas básicas: tamaño, tipos, memoria."""
        self.perfil['meta'] = {
            'dataset': self.nombre_dataset,
            'timestamp': self.timestamp,
            'registros': int(len(self.df)),
            'columnas': int(len(self.df.columns)),
            'memoria_mb': float(self.df.memory_usage(deep=True).sum() / 1024**2),
            'duplicados_totales': int(self.df.duplicated().sum()),
            'duplicados_completos': int(self.df.duplicated(keep=False).sum())
        }
        return self.perfil['meta']

    def analisis_nulos(self):
        """Analiza valores nulos por columna."""
        self.perfil['nulos'] = {}
        
        for col in self.df.columns:
            nulos = self.df[col].isnull().sum()
            pct = (nulos / len(self.df)) * 100
            
            self.perfil['nulos'][col] = {
                'cantidad': int(nulos),
                'porcentaje': float(round(pct, 2)),
                'confiabilidad': float(round(100 - pct, 2))
            }
        
        return self.perfil['nulos']

    def analisis_numerico(self):
        """Análisis de columnas numéricas: distribución, outliers, ceros."""
        self.perfil['numerico'] = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            datos = self.df[col].dropna()
            
            if len(datos) == 0:
                continue
            
            # Ceros y valores <= 0
            n_ceros = (datos == 0).sum()
            n_negativos = (datos < 0).sum()
            
            # Outliers (IQR method)
            Q1, Q3 = datos.quantile([0.25, 0.75])
            IQR = Q3 - Q1
            limite_inf = Q1 - 1.5 * IQR
            limite_sup = Q3 + 1.5 * IQR
            outliers = ((datos < limite_inf) | (datos > limite_sup)).sum()
            
            self.perfil['numerico'][col] = {
                'tipo': 'numérico',
                'no_nulos': int(len(datos)),
                'media': float(datos.mean()),
                'mediana': float(datos.median()),
                'std': float(datos.std()),
                'min': float(datos.min()),
                'max': float(datos.max()),
                'q25': float(Q1),
                'q75': float(Q3),
                'ceros': int(n_ceros),
                'pct_ceros': float(round((n_ceros / len(datos)) * 100, 2)) if len(datos) > 0 else 0,
                'negativos': int(n_negativos),
                'pct_negativos': float(round((n_negativos / len(datos)) * 100, 2)) if len(datos) > 0 else 0,
                'outliers': int(outliers),
                'pct_outliers': float(round((outliers / len(datos)) * 100, 2)) if len(datos) > 0 else 0,
                'confiabilidad': float(round(100 - (n_ceros + n_negativos + outliers) / len(datos) * 100, 2))
            }
        
        return self.perfil['numerico']

    def analisis_categorico(self):
        """Análisis de columnas categóricas: cardinalidad, dominancia."""
        self.perfil['categorico'] = {}
        
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        for col in cat_cols:
            datos = self.df[col].dropna()
            
            if len(datos) == 0:
                continue
            
            unique = datos.nunique()
            valor_dominante = datos.value_counts().iloc[0] if len(datos) > 0 else 0
            pct_dominante = (valor_dominante / len(datos)) * 100 if len(datos) > 0 else 0
            
            self.perfil['categorico'][col] = {
                'tipo': 'categórico',
                'no_nulos': int(len(datos)),
                'valores_unicos': int(unique),
                'valor_dominante': str(datos.value_counts().index[0]) if len(datos) > 0 else None,
                'freq_dominante': int(valor_dominante),
                'pct_dominante': float(round(pct_dominante, 2)),
                'diversidad': float(round(100 * (1 - pct_dominante / 100), 2)),
                'top_5_valores': {
                    str(k): int(v) for k, v in datos.value_counts().head(5).items()
                },
                'confiabilidad': float(round(100 - (self.df[col].isnull().sum() / len(self.df)) * 100, 2))
            }
        
        return self.perfil['categorico']

    def patrones_nulos(self):
        """Detecta patrones en nulos (si están correlacionados)."""
        self.perfil['patrones_nulos'] = {}
        
        cols_con_nulos = self.df.columns[self.df.isnull().any()].tolist()
        
        if len(cols_con_nulos) < 2:
            return {}
        
        for i, col1 in enumerate(cols_con_nulos):
            for col2 in cols_con_nulos[i+1:]:
                ambos_nulos = (self.df[col1].isnull() & self.df[col2].isnull()).sum()
                if ambos_nulos > 0:
                    self.perfil['patrones_nulos'][f'{col1}_{col2}'] = {
                        'registros_ambos_nulos': int(ambos_nulos),
                        'porcentaje': float(round((ambos_nulos / len(self.df)) * 100, 2))
                    }
        
        return self.perfil['patrones_nulos']

    def matriz_correlacion(self):
        """Matriz de correlación entre numéricas (para dependencias)."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) > 1:
            corr = self.df[numeric_cols].corr()
            # Guardar correlaciones significativas (abs > 0.5)
            self.perfil['correlaciones_altas'] = {}
            
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    c = corr.loc[col1, col2]
                    if abs(c) > 0.5:
                        self.perfil['correlaciones_altas'][f'{col1}_{col2}'] = float(round(c, 3))
        
        return self.perfil.get('correlaciones_altas', {})

    def score_calidad(self):
        """
        Calcula score de calidad global (0-100).
        Basado en: completitud, consistencia, unicidad.
        """
        # Completitud: % de celdas sin nulos
        n_celdas = len(self.df) * len(self.df.columns)
        n_nulos = self.df.isnull().sum().sum()
        completitud = 100 * (1 - n_nulos / n_celdas)
        
        # Consistencia: % de registros sin duplicados completos
        n_duplicados = self.df.duplicated(keep=False).sum()
        consistencia = 100 * (1 - n_duplicados / len(self.df))
        
        # Score final: promedio ponderado
        score = (completitud * 0.6 + consistencia * 0.4)
        
        self.perfil['calidad'] = {
            'score_global': float(round(score, 2)),
            'completitud': float(round(completitud, 2)),
            'consistencia': float(round(consistencia, 2)),
            'estado': self._clasificar_calidad(score)
        }
        
        return self.perfil['calidad']

    def _clasificar_calidad(self, score):
        """Clasifica calidad en categorías."""
        if score >= 90:
            return 'EXCELENTE'
        elif score >= 75:
            return 'BUENA'
        elif score >= 60:
            return 'ACEPTABLE'
        else:
            return 'CRÍTICA'

    def generar_perfil_completo(self):
        """Ejecuta todos los análisis y retorna perfil completo."""
        print(f"\n{'='*80}")
        print(f"PERFILADO DE DATOS: {self.nombre_dataset}")
        print(f"{'='*80}\n")

        # Ejecución de análisis
        print("1. Estadísticas básicas...")
        self.perfil_basico()
        
        print("2. Análisis de nulos...")
        self.analisis_nulos()
        
        print("3. Análisis numérico...")
        self.analisis_numerico()
        
        print("4. Análisis categórico...")
        self.analisis_categorico()
        
        print("5. Detectando patrones de nulos...")
        self.patrones_nulos()
        
        print("6. Correlaciones...")
        self.matriz_correlacion()
        
        print("7. Score de calidad...")
        self.score_calidad()

        return self.perfil

    def guardar_perfil_json(self, ruta='perfil_datos.json'):
        """Guarda perfil en JSON para almacenamiento."""
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(self.perfil, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Perfil guardado: {ruta}")
        return ruta

    def generar_reporte_texto(self, ruta='reporte_profiling.txt'):
        """Genera reporte legible en texto."""
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"REPORTE DE PERFILADO DE DATOS: {self.nombre_dataset}\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write("="*80 + "\n\n")

            # Meta
            meta = self.perfil['meta']
            f.write("INFORMACIÓN BÁSICA\n")
            f.write(f"  Registros: {meta['registros']:,}\n")
            f.write(f"  Columnas: {meta['columnas']}\n")
            f.write(f"  Memoria: {meta['memoria_mb']:.2f} MB\n")
            f.write(f"  Duplicados totales: {meta['duplicados_totales']:,}\n\n")

            # Calidad
            calidad = self.perfil['calidad']
            f.write("SCORE DE CALIDAD\n")
            f.write(f"  Score Global: {calidad['score_global']}/100 ({calidad['estado']})\n")
            f.write(f"  Completitud: {calidad['completitud']}%\n")
            f.write(f"  Consistencia: {calidad['consistencia']}%\n\n")

            # Nulos
            f.write("ANÁLISIS DE NULOS\n")
            nulos_df = pd.DataFrame(self.perfil['nulos']).T
            nulos_df_sorted = nulos_df.sort_values('cantidad', ascending=False)
            f.write(nulos_df_sorted.to_string())
            f.write("\n\n")

            # Numéricos
            if self.perfil['numerico']:
                f.write("ANÁLISIS NUMÉRICO (seleccionado)\n")
                for col, stats in list(self.perfil['numerico'].items())[:5]:
                    f.write(f"  {col}:\n")
                    f.write(f"    Media: {stats['media']:,.2f} | Mediana: {stats['mediana']:,.2f}\n")
                    f.write(f"    Ceros: {stats['ceros']:,} ({stats['pct_ceros']}%)\n")
                    f.write(f"    Outliers: {stats['outliers']:,} ({stats['pct_outliers']}%)\n")
                    f.write(f"    Confiabilidad: {stats['confiabilidad']}%\n\n")

            # Patrones de nulos
            if self.perfil['patrones_nulos']:
                f.write("PATRONES DE NULOS CORRELACIONADOS\n")
                for pair, info in self.perfil['patrones_nulos'].items():
                    f.write(f"  {pair}: {info['registros_ambos_nulos']:,} ({info['porcentaje']}%)\n")
                f.write("\n")

            # Correlaciones
            if self.perfil.get('correlaciones_altas'):
                f.write("CORRELACIONES ALTAS (r > 0.5)\n")
                for pair, corr in self.perfil['correlaciones_altas'].items():
                    f.write(f"  {pair}: {corr}\n")

        print(f"✓ Reporte guardado: {ruta}")
        return ruta

    def imprimir_resumen(self):
        """Imprime resumen en consola."""
        print(f"\n{'─'*80}")
        print("RESUMEN EJECUTIVO")
        print(f"{'─'*80}")
        
        meta = self.perfil['meta']
        print(f"📊 Registros: {meta['registros']:,} | Columnas: {meta['columnas']}")
        print(f"💾 Memoria: {meta['memoria_mb']:.2f} MB | Duplicados: {meta['duplicados_totales']:,}")
        
        calidad = self.perfil['calidad']
        print(f"\n🎯 Calidad Global: {calidad['score_global']}/100 ({calidad['estado']})")
        print(f"   Completitud: {calidad['completitud']}% | Consistencia: {calidad['consistencia']}%")
        
        # Columnas críticas
        nulos = self.perfil['nulos']
        cols_criticas = {k: v for k, v in nulos.items() if v['porcentaje'] > 20}
        
        if cols_criticas:
            print(f"\n⚠️  COLUMNAS CRÍTICAS (>20% nulos):")
            for col, info in cols_criticas.items():
                print(f"   {col}: {info['porcentaje']}% nulos")
        
        print(f"{'─'*80}\n")


# ================================================================================
# Configuración de Base de Datos
# ================================================================================

from sqlalchemy import create_engine

# Credenciales PostgreSQL (CAMBIAR SI ES NECESARIO)
DB_CONFIG = {
    'user': 'catastro_jmm9_user',
    'password': 'W4q6uMkHT6BTaRDUF58XYY7AV2CUatBW',
    'host': 'pg-d7t01mq8qa3s73f28r4g-a.oregon-postgres.render.com',
    'port': '5432',
    'database': 'catastro_jmm9'
}

def crear_engine_postgres(config=DB_CONFIG):
    """Crea conexión SQLAlchemy a PostgreSQL."""
    url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    return create_engine(url)


# ================================================================================
# Ejemplo de uso
# ================================================================================

if __name__ == "__main__":
    try:
        # Conectar a PostgreSQL
        engine = crear_engine_postgres()
        print("✓ Conexión a PostgreSQL establecida con SQLAlchemy\n")
        
        # Cargar datos desde base
        # AJUSTA LA TABLA SEGÚN TU ESQUEMA
        query = """
        SELECT 
            nm_mtcla_prdio AS id_predio,
            estrato_pre AS estrato,
            ds_barrio AS barrio_nombre,
            ava_total_ava AS avaluo_total,
            area_con AS area_construida,
            nm_ptje AS puntaje,
            ds_tipo_construccion AS tipo_construccion
        FROM catastro.insertar_predios_construccion
        --LIMIT 10000
        
        """
        
        print("Cargando datos desde PostgreSQL...")
        df = pd.read_sql_query(query, con=engine)
        print(f"✓ {len(df):,} registros cargados\n")
        
        # Ejecutar profiling
        profiler = DataProfiler(df, nombre_dataset='EAGIC_Catastro')
        perfil = profiler.generar_perfil_completo()
        profiler.imprimir_resumen()
        
        # Crear directorio de outputs
        Path('outputs').mkdir(exist_ok=True)
        
        # Guardar resultados
        ruta_json = profiler.guardar_perfil_json(
            f'outputs/perfil_datos_{profiler.timestamp}.json'
        )
        ruta_txt = profiler.generar_reporte_texto(
            f'outputs/reporte_profiling_{profiler.timestamp}.txt'
        )
        
        print(f"\n✓ Perfilado completado. Revisa outputs/ para detalles.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Verifica credenciales y conexión a PostgreSQL.")
