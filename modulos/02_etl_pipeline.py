"""
================================================================================
02_ETL_PIPELINE.py - FILTRO DE PUREZA (ESTANDARIZACIÓN Y VALIDACIÓN)
================================================================================

Módulo ETL:
- Validación de esquema y tipos de datos
- Estandarización de formatos
- Corrección de llaves primarias
- Eliminación de duplicados y registros inválidos
- Generación de reportes de limpieza

Salida: datos_limpios_TIMESTAMP.csv + reporte_etl.json


================================================================================
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    Pipeline ETL para limpieza y validación de datos catastales.
    """

    def __init__(self, df, nombre='dataset'):
        """
        Args:
            df: DataFrame a procesar
            nombre: Nombre del dataset
        """
        self.df_original = df.copy()
        self.df = df.copy()
        self.nombre = nombre
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.reporte = {
            'timestamp': self.timestamp,
            'dataset': nombre,
            'etapas': {}
        }
        self.n_registros_inicial = len(df)

    def validar_esquema(self, esquema_esperado=None):
        """
        Valida esquema de datos.
        
        Args:
            esquema_esperado: dict con {columna: tipo_esperado}
        """
        logger.info("Etapa 1: Validación de esquema")
        
        etapa = {'nombre': 'Validación de esquema', 'validaciones': []}
        
        # Esquema por defecto para catastro
        if esquema_esperado is None:
            esquema_esperado = {
                'id_predio': 'int64',
                'estrato': 'object',  # Categórico
                'barrio_nombre': 'object',
                'avaluo_total': 'float64',
                'area_construida': 'float64',
                'puntaje': 'float64',
                'tipo_construccion': 'object'
            }
        
        for col, tipo_esperado in esquema_esperado.items():
            if col not in self.df.columns:
                etapa['validaciones'].append({
                    'columna': col,
                    'estado': 'FALTANTE',
                    'accion': 'Columna no encontrada'
                })
                logger.warning(f"  ⚠️  Columna faltante: {col}")
            else:
                tipo_actual = str(self.df[col].dtype)
                etapa['validaciones'].append({
                    'columna': col,
                    'tipo_esperado': tipo_esperado,
                    'tipo_actual': tipo_actual,
                    'estado': 'OK' if tipo_actual in tipo_esperado else 'TIPO_INCORRECTO'
                })
        
        self.reporte['etapas']['esquema'] = etapa
        logger.info(f"  ✓ Esquema validado\n")
        return self

    def estandarizar_tipos(self):
        """Convierte tipos de datos a los esperados."""
        logger.info("Etapa 2: Estandarización de tipos")
        
        etapa = {'nombre': 'Estandarización de tipos', 'conversiones': []}
        
        # Conversiones específicas
        conversiones = {
            'estrato': str,
            'barrio_nombre': str,
            'tipo_construccion': str,
            'avaluo_total': float,
            'area_construida': float,
            'puntaje': float
        }
        
        for col, tipo in conversiones.items():
            if col in self.df.columns:
                try:
                    before = self.df[col].dtype
                    if tipo == str:
                        self.df[col] = self.df[col].astype(str)
                    else:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    
                    etapa['conversiones'].append({
                        'columna': col,
                        'tipo_antes': str(before),
                        'tipo_despues': str(self.df[col].dtype),
                        'estado': 'OK'
                    })
                    logger.info(f"  ✓ {col}: {before} → {self.df[col].dtype}")
                except Exception as e:
                    etapa['conversiones'].append({
                        'columna': col,
                        'error': str(e)
                    })
                    logger.error(f"  ❌ {col}: {e}")
        
        self.reporte['etapas']['tipos'] = etapa
        logger.info("")
        return self

    def limpiar_duplicados(self):
        """Elimina duplicados exactos (mantiene el primero)."""
        logger.info("Etapa 3: Eliminación de duplicados")
        
        etapa = {'nombre': 'Eliminación de duplicados'}
        
        n_antes = len(self.df)
        
        # Duplicados exactos
        duplicados_exactos = self.df.duplicated().sum()
        self.df = self.df.drop_duplicates(keep='first')
        
        n_despues = len(self.df)
        eliminados = n_antes - n_despues
        
        etapa['duplicados_exactos'] = int(duplicados_exactos)
        etapa['registros_eliminados'] = int(eliminados)
        etapa['registros_antes'] = int(n_antes)
        etapa['registros_despues'] = int(n_despues)
        
        logger.info(f"  Duplicados exactos: {duplicados_exactos:,}")
        logger.info(f"  Registros eliminados: {eliminados:,}")
        logger.info(f"  Registros restantes: {n_despues:,}\n")
        
        self.reporte['etapas']['duplicados'] = etapa
        return self

    def validar_llave_primaria(self, col_pk='id_predio'):
        """
        Valida que la llave primaria sea única.
        
        Args:
            col_pk: Nombre de la columna llave primaria
        """
        logger.info(f"Etapa 4: Validación de llave primaria ({col_pk})")
        
        etapa = {'nombre': f'Validación PK: {col_pk}'}
        
        if col_pk not in self.df.columns:
            logger.warning(f"  ⚠️  Columna PK no encontrada: {col_pk}")
            etapa['estado'] = 'COLUMNA_NO_ENCONTRADA'
            self.reporte['etapas']['pk'] = etapa
            logger.info("")
            return self
        
        n_total = len(self.df)
        n_nulos_pk = self.df[col_pk].isnull().sum()
        n_unicos = self.df[col_pk].nunique()
        duplicados_pk = self.df.duplicated(subset=[col_pk], keep=False).sum()
        
        etapa['registros_totales'] = int(n_total)
        etapa['nulos_pk'] = int(n_nulos_pk)
        etapa['valores_unicos'] = int(n_unicos)
        etapa['duplicados_pk'] = int(duplicados_pk)
        
        # Eliminar nulos en PK
        if n_nulos_pk > 0:
            logger.warning(f"  ⚠️  {n_nulos_pk:,} valores nulos en PK (serán eliminados)")
            self.df = self.df[self.df[col_pk].notna()].copy()
        
        # Detectar duplicados
        if duplicados_pk > 0:
            logger.warning(f"  ⚠️  {duplicados_pk:,} registros duplicados en PK")
            # Mantener primer ocurrencia
            self.df = self.df.drop_duplicates(subset=[col_pk], keep='first')
            logger.info(f"  ✓ Duplicados eliminados, mantenido primer registro")
        else:
            logger.info(f"  ✓ PK válida (todos únicos)")
        
        etapa['estado'] = 'OK' if duplicados_pk == 0 else 'DUPLICADOS_CORREGIDOS'
        self.reporte['etapas']['pk'] = etapa
        logger.info("")
        return self

    def limpiar_numericos(self):
        """
        Limpia columnas numéricas:
        - Convierte a NaN valores inválidos
        - Elimina registros con avalúos <= 0
        - Marca ceros en áreas (posibles datos faltantes)
        """
        logger.info("Etapa 5: Limpieza de numéricos")
        
        etapa = {'nombre': 'Limpieza de numéricos', 'reglas_aplicadas': []}
        
        # Regla 1: Avalúo > 0
        if 'avaluo_total' in self.df.columns:
            mask_avaluo_invalido = self.df['avaluo_total'] <= 0
            n_invalidos = mask_avaluo_invalido.sum()
            
            if n_invalidos > 0:
                self.df = self.df[~mask_avaluo_invalido].copy()
                logger.info(f"  ✓ Eliminados {n_invalidos:,} registros con avalúo <= 0")
                etapa['reglas_aplicadas'].append({
                    'regla': 'avaluo_total > 0',
                    'registros_eliminados': int(n_invalidos)
                })
        
        # Regla 2: Puntaje en rango válido (0-100 típicamente)
        if 'puntaje' in self.df.columns:
            # Detectar outliers extremos
            mask_puntaje_invalido = (self.df['puntaje'] < 0) | (self.df['puntaje'] > 100)
            n_invalidos = mask_puntaje_invalido.sum()
            
            if n_invalidos > 0:
                self.df.loc[mask_puntaje_invalido, 'puntaje'] = np.nan
                logger.info(f"  ⚠️  {n_invalidos:,} puntajes fuera de rango [0-100] → NaN")
                etapa['reglas_aplicadas'].append({
                    'regla': 'puntaje en [0, 100]',
                    'registros_convertidos_nan': int(n_invalidos)
                })
        
        # Regla 3: Área construida >= 0 (pero marca ceros)
        if 'area_construida' in self.df.columns:
            n_ceros = (self.df['area_construida'] == 0).sum()
            mask_negativos = self.df['area_construida'] < 0
            n_negativos = mask_negativos.sum()
            
            if n_negativos > 0:
                self.df.loc[mask_negativos, 'area_construida'] = np.nan
                logger.info(f"  ⚠️  {n_negativos:,} áreas negativas → NaN")
                etapa['reglas_aplicadas'].append({
                    'regla': 'area_construida >= 0',
                    'registros_convertidos_nan': int(n_negativos)
                })
            
            if n_ceros > 0:
                logger.info(f"  ℹ️  {n_ceros:,} áreas = 0 (posibles nulos, se imputarán)")
                etapa['reglas_aplicadas'].append({
                    'regla': 'area_construida = 0',
                    'registros_detectados': int(n_ceros),
                    'accion': 'Marcados para imputación'
                })
        
        self.reporte['etapas']['numericos'] = etapa
        logger.info("")
        return self

    def estandarizar_categoricas(self):
        """
        Estandariza columnas categóricas:
        - Convierte a minúsculas
        - Elimina espacios en blanco
        - Trata valores raros
        """
        logger.info("Etapa 6: Estandarización de categóricas")
        
        etapa = {'nombre': 'Estandarización de categóricas', 'transformaciones': []}
        
        cat_cols = ['estrato', 'barrio_nombre', 'tipo_construccion']
        
        for col in cat_cols:
            if col not in self.df.columns:
                continue
            
            n_antes = self.df[col].nunique()
            
            # Limpiar espacios
            self.df[col] = self.df[col].str.strip()
            
            # Minúsculas (excepto estrato que es numérico como string)
            if col != 'estrato':
                self.df[col] = self.df[col].str.lower()
            
            n_despues = self.df[col].nunique()
            
            etapa['transformaciones'].append({
                'columna': col,
                'valores_unicos_antes': int(n_antes),
                'valores_unicos_despues': int(n_despues),
                'acciones': ['strip', 'lower']
            })
            logger.info(f"  ✓ {col}: {n_antes} → {n_despues} valores únicos")
        
        self.reporte['etapas']['categoricas'] = etapa
        logger.info("")
        return self

    def crear_features_derivadas(self):
        """Crea features derivadas para análisis posterior."""
        logger.info("Etapa 7: Creación de features derivadas")
        
        etapa = {'nombre': 'Features derivadas', 'features_creadas': []}
        
        # Feature: es_comercial (estrato = '0')
        if 'estrato' in self.df.columns:
            self.df['es_comercial'] = (self.df['estrato'].astype(str) == '0').astype(int)
            etapa['features_creadas'].append({
                'nombre': 'es_comercial',
                'descripcion': 'Indicador si estrato = 0 (comercial)',
                'tipo': 'int'
            })
            logger.info(f"  ✓ es_comercial (estrato='0'): {self.df['es_comercial'].sum():,} comerciales")
        
        # Feature: avaluo_por_m2 (solo donde area > 0)
        if 'avaluo_total' in self.df.columns and 'area_construida' in self.df.columns:
            self.df['avaluo_por_m2'] = np.where(
                (self.df['area_construida'].notna()) & (self.df['area_construida'] > 0),
                self.df['avaluo_total'] / self.df['area_construida'],
                np.nan
            )
            etapa['features_creadas'].append({
                'nombre': 'avaluo_por_m2',
                'descripcion': 'Avalúo dividido por área construida',
                'tipo': 'float'
            })
            logger.info(f"  ✓ avaluo_por_m2 calculado")
        
        # Feature: flags de imputación (inicialmente todo = 0)
        self.df['area_construida_imputada'] = 0
        self.df['puntaje_imputado'] = 0
        self.df['tipo_construccion_imputado'] = 0
        
        etapa['features_creadas'].extend([
            {'nombre': 'area_construida_imputada', 'descripcion': 'Flag de imputación'},
            {'nombre': 'puntaje_imputado', 'descripcion': 'Flag de imputación'},
            {'nombre': 'tipo_construccion_imputado', 'descripcion': 'Flag de imputación'}
        ])
        
        logger.info(f"  ✓ Flags de imputación creados")
        
        self.reporte['etapas']['features'] = etapa
        logger.info("")
        return self

    def generar_resumen_limpieza(self):
        """Genera resumen de cambios en los datos."""
        logger.info("Etapa 8: Resumen de limpieza")
        
        etapa = {
            'nombre': 'Resumen general',
            'registros_inicial': int(self.n_registros_inicial),
            'registros_final': int(len(self.df)),
            'registros_eliminados': int(self.n_registros_inicial - len(self.df)),
            'porcentaje_retencion': float(round(100 * len(self.df) / self.n_registros_inicial, 2)),
            'columnas_final': int(len(self.df.columns)),
            'nulos_finales': int(self.df.isnull().sum().sum()),
            'duplicados_finales': int(self.df.duplicated().sum())
        }
        
        self.reporte['etapas']['resumen'] = etapa
        
        logger.info(f"  Registros: {self.n_registros_inicial:,} → {len(self.df):,}")
        logger.info(f"  Retencion: {etapa['porcentaje_retencion']}%")
        logger.info(f"  Columnas finales: {etapa['columnas_final']}")
        logger.info(f"  Nulos finales: {etapa['nulos_finales']:,}")
        logger.info(f"  Duplicados finales: {etapa['duplicados_finales']:,}")
        logger.info("")
        
        return self

    def ejecutar_pipeline_completo(self, col_pk='id_predio'):
        """Ejecuta el pipeline completo."""
        logger.info("="*80)
        logger.info("INICIANDO PIPELINE ETL DE PUREZA")
        logger.info("="*80 + "\n")
        
        self.validar_esquema()
        self.estandarizar_tipos()
        self.limpiar_duplicados()
        self.validar_llave_primaria(col_pk=col_pk)
        self.limpiar_numericos()
        self.estandarizar_categoricas()
        self.crear_features_derivadas()
        self.generar_resumen_limpieza()
        
        logger.info("="*80)
        logger.info("PIPELINE COMPLETADO EXITOSAMENTE")
        logger.info("="*80 + "\n")
        
        return self.df, self.reporte

    def guardar_datos_limpios(self, ruta='datos_limpios.csv'):
        """Guarda datos limpios en CSV."""
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(ruta, index=False)
        logger.info(f"✓ Datos limpios guardados: {ruta}")
        return ruta

    def guardar_reporte_json(self, ruta='reporte_etl.json'):
        """Guarda reporte en JSON."""
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(self.reporte, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Reporte ETL guardado: {ruta}")
        return ruta

    def obtener_datos_limpios(self):
        """Retorna DataFrame limpio."""
        return self.df.copy()


# ================================================================================
# Ejemplo de uso con PostgreSQL
# ================================================================================

if __name__ == "__main__":
    from sqlalchemy import create_engine
    
    # Configuración BD
    DB_CONFIG = {
        'user': 'catastro_jmm9_user',
        'password': 'W4q6uMkHT6BTaRDUF58XYY7AV2CUatBW',
        'host': 'pg-d7t01mq8qa3s73f28r4g-a.oregon-postgres.render.com',
        'port': '5432',
        'database': 'catastro_jmm9'
    }
    
    try:
        # Conectar
        url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(url)
        
        # Cargar datos
        print("Cargando datos desde PostgreSQL...\n")
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
        LIMIT 50000
        """
        
        df = pd.read_sql_query(query, con=engine)
        print(f"✓ {len(df):,} registros cargados\n")
        
        # Ejecutar pipeline
        pipeline = ETLPipeline(df, nombre='EAGIC_Catastro')
        df_limpio, reporte = pipeline.ejecutar_pipeline_completo(col_pk='id_predio')
        
        # Crear directorio de outputs
        Path('outputs').mkdir(exist_ok=True)
        
        # Guardar resultados
        ruta_csv = pipeline.guardar_datos_limpios(
            f'outputs/datos_limpios_{pipeline.timestamp}.csv'
        )
        ruta_json = pipeline.guardar_reporte_json(
            f'outputs/reporte_etl_{pipeline.timestamp}.json'
        )
        
        print(f"\n✓ Pipeline completado. Archivos en outputs/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
