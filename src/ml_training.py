"""
================================================================================
03_ML_TRAINING.py - IMPUTACIÓN INTELIGENTE CON MACHINE LEARNING
================================================================================

Módulo de entrenamiento de modelos ML para imputación:
- Regresión para area_construida
- Regresión para puntaje
- Clasificación para tipo_construccion
- Validación cruzada exhaustiva
- Persistencia de modelos (MLOps ready)

Salida: modelo_*.pkl + metricas_entrenamiento.json

================================================================================
"""

import pandas as pd
import numpy as np
import json
import joblib
from datetime import datetime
from pathlib import Path
import logging
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Scikit-learn
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, classification_report, confusion_matrix
)
from sklearn.base import clone

# Modelos
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import Ridge

# Progreso (con fallback si no está instalado)
try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, iterable=None, **kwargs):
            self.iterable = iterable
        def __iter__(self):
            for obj in (self.iterable if self.iterable else []):
                yield obj
        def __enter__(self):
            return self
        def __exit__(self, *args, **kwargs):
            pass


class ModeloRegresion:
    """
    Modelo de regresión para imputación de variables continuas.
    Implementa validación cruzada, evaluación y persistencia.
    """

    def __init__(self, nombre='modelo_regresion', random_state=42):
        """
        Args:
            nombre: Nombre del modelo
            random_state: Seed para reproducibilidad
        """
        self.nombre = nombre
        self.random_state = random_state
        self.pipeline = None
        self.metricas = {}
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def crear_preprocesador(self, cat_features, num_features):
        """Crea ColumnTransformer para features categóricas y numéricas."""
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = OneHotEncoder(
            handle_unknown='ignore',
            sparse_output=False,
            max_categories=50
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, num_features),
                ('cat', categorical_transformer, cat_features)
            ],
            remainder='drop'
        )
        return preprocessor

    def entrenar(self, X_train, y_train, X_test, y_test, 
                 cat_features, num_features, n_splits=5):
        """
        Entrena múltiples modelos y selecciona el mejor.
        
        Args:
            X_train, y_train: Datos de entrenamiento
            X_test, y_test: Datos de prueba
            cat_features: Lista de columnas categóricas
            num_features: Lista de columnas numéricas
            n_splits: Folds para validación cruzada
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Entrenando: {self.nombre}")
        logger.info(f"{'='*80}")
        logger.info(f"Train: {len(X_train):,} muestras | Test: {len(X_test):,} muestras | Folds: {n_splits}")

        # Modelos candidatos
        modelos = {
            'RandomForest': RandomForestRegressor(
                n_estimators=150, max_depth=20, min_samples_leaf=3,
                n_jobs=-1, random_state=self.random_state
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=150, max_depth=6, learning_rate=0.1,
                subsample=0.8, random_state=self.random_state
            ),
            'Ridge': Ridge(alpha=1.0)
        }

        resultados_modelos = {}
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)

        for nombre_mod, modelo in modelos.items():
            logger.info(f"\n  • {nombre_mod}...")

            # Preprocesador fresco para este modelo
            preprocessor = self.crear_preprocesador(cat_features, num_features)

            # === VALIDACIÓN CRUZADA MANUAL CON PROGRESO ===
            cv_r2_scores = []
            cv_mae_scores = []
            folds = list(cv.split(X_train))

            for fold_idx, (train_idx, val_idx) in enumerate(
                tqdm(folds, desc=f"    CV {nombre_mod}", total=n_splits, leave=False, ncols=80), 1
            ):
                # Indexado seguro (DataFrame o numpy)
                if hasattr(X_train, 'iloc'):
                    X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
                    y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
                else:
                    X_tr, X_val = X_train[train_idx], X_train[val_idx]
                    y_tr, y_val = y_train[train_idx], y_train[val_idx]

                # Pipeline fresco por fold (evita estado contaminado)
                fold_pipeline = Pipeline(steps=[
                    ('preprocessor', self.crear_preprocesador(cat_features, num_features)),
                    ('regressor', clone(modelo))
                ])

                fold_pipeline.fit(X_tr, y_tr)
                y_pred_val = fold_pipeline.predict(X_val)

                cv_r2_scores.append(r2_score(y_val, y_pred_val))
                cv_mae_scores.append(mean_absolute_error(y_val, y_pred_val))

            cv_r2 = np.array(cv_r2_scores)
            cv_mae = np.array(cv_mae_scores)

            # === ENTRENAMIENTO FINAL EN TRAIN COMPLETO ===
            pipeline = Pipeline(steps=[
                ('preprocessor', preprocessor),
                ('regressor', modelo)
            ])

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)

            r2_test = r2_score(y_test, y_pred)
            mae_test = mean_absolute_error(y_test, y_pred)
            rmse_test = np.sqrt(mean_squared_error(y_test, y_pred))

            resultados_modelos[nombre_mod] = {
                'pipeline': pipeline,
                'cv_r2_mean': cv_r2.mean(),
                'cv_r2_std': cv_r2.std(),
                'cv_mae_mean': cv_mae.mean(),
                'test_r2': r2_test,
                'test_mae': mae_test,
                'test_rmse': rmse_test
            }

            logger.info(f"    CV R²: {cv_r2.mean():.4f} (±{cv_r2.std():.4f}) | MAE: {cv_mae.mean():,.0f}")
            logger.info(f"    Test R²: {r2_test:.4f} | MAE: {mae_test:,.0f} | RMSE: {rmse_test:,.0f}")

        # === CORRECCIÓN CRÍTICA: seleccionar por CV R², NO por test R² ===
        mejor = max(resultados_modelos, key=lambda k: resultados_modelos[k]['cv_r2_mean'])
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🏆 MEJOR MODELO: {mejor} (seleccionado por CV R²)")
        logger.info(f"   CV R² = {resultados_modelos[mejor]['cv_r2_mean']:.4f} (±{resultados_modelos[mejor]['cv_r2_std']:.4f})")
        logger.info(f"   Test R² = {resultados_modelos[mejor]['test_r2']:.4f} | MAE = {resultados_modelos[mejor]['test_mae']:,.0f}")
        logger.info(f"{'='*80}")

        # Guardar mejor modelo
        self.pipeline = resultados_modelos[mejor]['pipeline']
        self.metricas = {
            'modelo_seleccionado': mejor,
            'criterio_seleccion': 'cv_r2_mean',
            'todos_modelos': {
                k: {
                    'cv_r2': float(v['cv_r2_mean']),
                    'cv_r2_std': float(v['cv_r2_std']),
                    'test_r2': float(v['test_r2']),
                    'test_mae': float(v['test_mae']),
                    'test_rmse': float(v['test_rmse'])
                }
                for k, v in resultados_modelos.items()
            },
            'metricas_mejor': {
                'cv_r2': float(resultados_modelos[mejor]['cv_r2_mean']),
                'cv_r2_std': float(resultados_modelos[mejor]['cv_r2_std']),
                'r2': float(resultados_modelos[mejor]['test_r2']),
                'mae': float(resultados_modelos[mejor]['test_mae']),
                'rmse': float(resultados_modelos[mejor]['test_rmse'])
            }
        }

        return self

    def predecir(self, X):
        """Genera predicciones."""
        if self.pipeline is None:
            raise ValueError("Modelo no entrenado. Ejecuta entrenar() primero.")
        return self.pipeline.predict(X)

    def guardar(self, ruta='modelo.pkl'):
        """Persiste modelo en archivo."""
        if self.pipeline is None:
            raise ValueError("Modelo no entrenado.")
        
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, ruta)
        logger.info(f"✓ Modelo guardado: {ruta}")
        return ruta

    def cargar(self, ruta):
        """Carga modelo desde archivo."""
        self.pipeline = joblib.load(ruta)
        logger.info(f"✓ Modelo cargado: {ruta}")
        return self


class ModeloClasificacion:
    """
    Modelo de clasificación para imputación de variables categóricas.
    """

    def __init__(self, nombre='modelo_clasificacion', random_state=42):
        """
        Args:
            nombre: Nombre del modelo
            random_state: Seed para reproducibilidad
        """
        self.nombre = nombre
        self.random_state = random_state
        self.pipeline = None
        self.metricas = {}
        self.clases = None
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def crear_preprocesador(self, cat_features, num_features):
        """Crea ColumnTransformer."""
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = OneHotEncoder(
            handle_unknown='ignore',
            sparse_output=False,
            max_categories=50
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, num_features),
                ('cat', categorical_transformer, cat_features)
            ],
            remainder='drop'
        )
        return preprocessor

    def entrenar(self, X_train, y_train, X_test, y_test,
                 cat_features, num_features, n_splits=5):
        """
        Entrena modelo de clasificación.
        
        Args:
            X_train, y_train: Datos de entrenamiento
            X_test, y_test: Datos de prueba
            cat_features: Lista de columnas categóricas
            num_features: Lista de columnas numéricas
            n_splits: Folds para validación cruzada
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Entrenando: {self.nombre} (CLASIFICACIÓN)")
        logger.info(f"{'='*80}")

        self.clases = sorted(y_train.unique())
        logger.info(f"Clases: {len(self.clases)} → {self.clases}\n")

        modelos = {
            'RandomForest': RandomForestClassifier(
                n_estimators=150, max_depth=20, min_samples_leaf=2,
                class_weight='balanced', n_jobs=-1, random_state=self.random_state
            ),
            'GradientBoosting': GradientBoostingClassifier(
                n_estimators=150, max_depth=5, learning_rate=0.1,
                subsample=0.8, random_state=self.random_state
            )
        }

        resultados_modelos = {}
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)

        for nombre_mod, modelo in modelos.items():
            logger.info(f"  • {nombre_mod}...")

            # === VALIDACIÓN CRUZADA MANUAL CON PROGRESO ===
            cv_acc_scores = []
            folds = list(cv.split(X_train))

            for fold_idx, (train_idx, val_idx) in enumerate(
                tqdm(folds, desc=f"    CV {nombre_mod}", total=n_splits, leave=False, ncols=80), 1
            ):
                if hasattr(X_train, 'iloc'):
                    X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
                    y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
                else:
                    X_tr, X_val = X_train[train_idx], X_train[val_idx]
                    y_tr, y_val = y_train[train_idx], y_train[val_idx]

                fold_pipeline = Pipeline(steps=[
                    ('preprocessor', self.crear_preprocesador(cat_features, num_features)),
                    ('classifier', clone(modelo))
                ])

                fold_pipeline.fit(X_tr, y_tr)
                y_pred_val = fold_pipeline.predict(X_val)
                cv_acc_scores.append(accuracy_score(y_val, y_pred_val))

            cv_acc = np.array(cv_acc_scores)

            # === ENTRENAMIENTO FINAL Y EVALUACIÓN EN TEST ===
            preprocessor = self.crear_preprocesador(cat_features, num_features)
            pipeline = Pipeline(steps=[
                ('preprocessor', preprocessor),
                ('classifier', modelo)
            ])

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            acc_test = accuracy_score(y_test, y_pred)

            resultados_modelos[nombre_mod] = {
                'pipeline': pipeline,
                'cv_acc_mean': cv_acc.mean(),
                'cv_acc_std': cv_acc.std(),
                'test_acc': acc_test
            }

            logger.info(f"    CV Accuracy: {cv_acc.mean():.4f} (±{cv_acc.std():.4f})")
            logger.info(f"    Test Accuracy: {acc_test:.4f}")

        # === CORRECCIÓN CRÍTICA: seleccionar por CV accuracy, NO por test accuracy ===
        mejor = max(resultados_modelos, key=lambda k: resultados_modelos[k]['cv_acc_mean'])
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🏆 MEJOR MODELO: {mejor} (seleccionado por CV Accuracy)")
        logger.info(f"   CV Acc = {resultados_modelos[mejor]['cv_acc_mean']:.4f} (±{resultados_modelos[mejor]['cv_acc_std']:.4f})")
        logger.info(f"   Test Acc = {resultados_modelos[mejor]['test_acc']:.4f}")
        logger.info(f"{'='*80}")

        # Evaluar
        y_pred_mejor = resultados_modelos[mejor]['pipeline'].predict(X_test)
        logger.info(f"\n📊 Reporte de clasificación:")
        logger.info(classification_report(y_test, y_pred_mejor, zero_division=0))

        self.pipeline = resultados_modelos[mejor]['pipeline']
        self.metricas = {
            'modelo_seleccionado': mejor,
            'criterio_seleccion': 'cv_acc_mean',
            'todos_modelos': {
                k: {
                    'cv_acc': float(v['cv_acc_mean']),
                    'cv_acc_std': float(v['cv_acc_std']),
                    'test_acc': float(v['test_acc'])
                }
                for k, v in resultados_modelos.items()
            },
            'metricas_mejor': {
                'cv_acc': float(resultados_modelos[mejor]['cv_acc_mean']),
                'cv_acc_std': float(resultados_modelos[mejor]['cv_acc_std']),
                'accuracy': float(resultados_modelos[mejor]['test_acc'])
            }
        }

        return self

    def predecir(self, X):
        """Genera predicciones."""
        if self.pipeline is None:
            raise ValueError("Modelo no entrenado.")
        return self.pipeline.predict(X)

    def guardar(self, ruta='modelo.pkl'):
        """Persiste modelo."""
        if self.pipeline is None:
            raise ValueError("Modelo no entrenado.")
        
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, ruta)
        logger.info(f"✓ Modelo guardado: {ruta}")
        return ruta

    def cargar(self, ruta):
        """Carga modelo."""
        self.pipeline = joblib.load(ruta)
        logger.info(f"✓ Modelo cargado: {ruta}")
        return self


class TuberiaImputacionML:
    """
    Orquestador de la tubería completa de imputación con ML.
    """

    def __init__(self, df, nombre_dataset='dataset', random_state=42):
        """
        Args:
            df: DataFrame con datos limpios (pre-procesados)
            nombre_dataset: Nombre del dataset
            random_state: Seed para reproducibilidad
        """
        self.df = df.copy()
        self.nombre_dataset = nombre_dataset
        self.random_state = random_state
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.modelo_area = None
        self.modelo_puntaje = None
        self.modelo_tipo = None
        self.reporte = {}

    def entrenar_area_construida(self):
        """Entrena modelo para area_construida."""
        logger.info("\n" + "#"*80)
        logger.info("IMPUTACIÓN 1: area_construida")
        logger.info("#"*80)

        # Datos completos para entrenamiento
        df_train = self.df[self.df['area_construida'].notna()].copy()
        logger.info(f"Registros con area_construida: {len(df_train):,} / {len(self.df):,}")

        X = df_train[['estrato', 'barrio_nombre', 'avaluo_total', 'puntaje', 'tipo_construccion']].copy()
        y = df_train['area_construida'].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        self.modelo_area = ModeloRegresion('area_construida', self.random_state)
        self.modelo_area.entrenar(
            X_train, y_train, X_test, y_test,
            cat_features=['estrato', 'barrio_nombre', 'tipo_construccion'],
            num_features=['avaluo_total', 'puntaje']
        )

        self.reporte['area_construida'] = self.modelo_area.metricas
        return self

    def imputar_area_construida(self):
        """Imputa area_construida usando modelo entrenado."""
        mask_nulo = self.df['area_construida'].isnull()
        n_nulos = mask_nulo.sum()

        if n_nulos == 0:
            logger.info("No hay valores nulos en area_construida.")
            return self

        logger.info(f"Imputando {n_nulos:,} valores de area_construida...")

        X_imputar = self.df.loc[mask_nulo, ['estrato', 'barrio_nombre', 'avaluo_total', 'puntaje', 'tipo_construccion']].copy()
        predicciones = self.modelo_area.predecir(X_imputar)
        predicciones = np.maximum(predicciones, 0)  # Sin negativos

        self.df.loc[mask_nulo, 'area_construida'] = predicciones
        self.df.loc[mask_nulo, 'area_construida_imputada'] = 1

        logger.info(f"✓ Imputadas {n_nulos:,} áreas. Media: {predicciones.mean():,.0f} m²")
        return self

    def entrenar_puntaje(self):
        """Entrena modelo para puntaje."""
        logger.info("\n" + "#"*80)
        logger.info("IMPUTACIÓN 2: puntaje")
        logger.info("#"*80)

        df_train = self.df[self.df['puntaje'].notna()].copy()
        logger.info(f"Registros con puntaje: {len(df_train):,} / {len(self.df):,}")

        X = df_train[['estrato', 'barrio_nombre', 'avaluo_total', 'area_construida', 'tipo_construccion']].copy()
        y = df_train['puntaje'].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        self.modelo_puntaje = ModeloRegresion('puntaje', self.random_state)
        self.modelo_puntaje.entrenar(
            X_train, y_train, X_test, y_test,
            cat_features=['estrato', 'barrio_nombre', 'tipo_construccion'],
            num_features=['avaluo_total', 'area_construida']
        )

        self.reporte['puntaje'] = self.modelo_puntaje.metricas
        return self

    def imputar_puntaje(self):
        """Imputa puntaje."""
        mask_nulo = self.df['puntaje'].isnull()
        n_nulos = mask_nulo.sum()

        if n_nulos == 0:
            logger.info("No hay valores nulos en puntaje.")
            return self

        logger.info(f"Imputando {n_nulos:,} valores de puntaje...")

        X_imputar = self.df.loc[mask_nulo, ['estrato', 'barrio_nombre', 'avaluo_total', 'area_construida', 'tipo_construccion']].copy()
        predicciones = self.modelo_puntaje.predecir(X_imputar)
        predicciones = np.clip(predicciones, self.df['puntaje'].min(), self.df['puntaje'].max())

        self.df.loc[mask_nulo, 'puntaje'] = predicciones
        self.df.loc[mask_nulo, 'puntaje_imputado'] = 1

        logger.info(f"✓ Imputados {n_nulos:,} puntajes. Media: {predicciones.mean():.0f}")
        return self

    def entrenar_tipo_construccion(self):
        """Entrena modelo para tipo_construccion."""
        logger.info("\n" + "#"*80)
        logger.info("IMPUTACIÓN 3: tipo_construccion")
        logger.info("#"*80)

        df_train = self.df[self.df['tipo_construccion'].notna()].copy()
        logger.info(f"Registros con tipo_construccion: {len(df_train):,} / {len(self.df):,}")

        X = df_train[['estrato', 'barrio_nombre', 'avaluo_total', 'area_construida', 'puntaje']].copy()
        y = df_train['tipo_construccion'].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )

        self.modelo_tipo = ModeloClasificacion('tipo_construccion', self.random_state)
        self.modelo_tipo.entrenar(
            X_train, y_train, X_test, y_test,
            cat_features=['estrato', 'barrio_nombre'],
            num_features=['avaluo_total', 'area_construida', 'puntaje']
        )

        self.reporte['tipo_construccion'] = self.modelo_tipo.metricas
        return self

    def imputar_tipo_construccion(self):
        """Imputa tipo_construccion."""
        mask_nulo = self.df['tipo_construccion'].isnull()
        n_nulos = mask_nulo.sum()

        if n_nulos == 0:
            logger.info("No hay valores nulos en tipo_construccion.")
            return self

        logger.info(f"Imputando {n_nulos:,} valores de tipo_construccion...")

        X_imputar = self.df.loc[mask_nulo, ['estrato', 'barrio_nombre', 'avaluo_total', 'area_construida', 'puntaje']].copy()
        predicciones = self.modelo_tipo.predecir(X_imputar)

        self.df.loc[mask_nulo, 'tipo_construccion'] = predicciones
        self.df.loc[mask_nulo, 'tipo_construccion_imputado'] = 1

        logger.info(f"✓ Imputados {n_nulos:,} tipos de construcción")
        return self

    def ejecutar_tuberia_completa(self):
        """Ejecuta la tubería completa de entrenamiento e imputación."""
        logger.info("\n" + "="*80)
        logger.info("TUBERÍA DE IMPUTACIÓN CON MACHINE LEARNING")
        logger.info("="*80)

        # Entrenar modelos
        self.entrenar_area_construida()
        self.entrenar_puntaje()
        self.entrenar_tipo_construccion()

        # Imputar en orden
        self.imputar_area_construida()
        self.imputar_puntaje()
        self.imputar_tipo_construccion()

        # Reporte final
        logger.info("\n" + "="*80)
        logger.info("VERIFICACIÓN FINAL")
        logger.info("="*80)
        logger.info(f"Registros totales: {len(self.df):,}")
        logger.info(f"Nulos finales: {self.df.isnull().sum().sum()}")
        logger.info(f"area_construida_imputada: {self.df['area_construida_imputada'].sum():,}")
        logger.info(f"puntaje_imputado: {self.df['puntaje_imputado'].sum():,}")
        logger.info(f"tipo_construccion_imputado: {self.df['tipo_construccion_imputado'].sum():,}")
        logger.info("="*80 + "\n")

        return self.df

    def guardar_modelos(self, prefijo='modelo_catastro'):
        """Guarda todos los modelos entrenados."""
        Path('outputs').mkdir(exist_ok=True)

        if self.modelo_area:
            ruta_area = self.modelo_area.guardar(f'outputs/{prefijo}_area_{self.timestamp}.pkl')
        if self.modelo_puntaje:
            ruta_puntaje = self.modelo_puntaje.guardar(f'outputs/{prefijo}_puntaje_{self.timestamp}.pkl')
        if self.modelo_tipo:
            ruta_tipo = self.modelo_tipo.guardar(f'outputs/{prefijo}_tipo_{self.timestamp}.pkl')

        logger.info(f"\n💾 Modelos guardados en outputs/")
        return self

    def guardar_reporte(self, ruta='outputs/reporte_ml.json'):
        """Guarda reporte de métricas."""
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)

        reporte_completo = {
            'timestamp': self.timestamp,
            'dataset': self.nombre_dataset,
            'modelos': self.reporte
        }

        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(reporte_completo, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Reporte guardado: {ruta}")
        return ruta

    def obtener_datos_imputados(self):
        """Retorna DataFrame con datos imputados."""
        return self.df.copy()


# ================================================================================
# Ejecución principal con PostgreSQL
# ================================================================================

if __name__ == "__main__":
    from sqlalchemy import create_engine

    DB_CONFIG = {
        'user': 'catastro_jmm9_user',
        'password': 'W4q6uMkHT6BTaRDUF58XYY7AV2CUatBW',
        'host': 'pg-d7t01mq8qa3s73f28r4g-a.oregon-postgres.render.com',
        'port': '5432',
        'database': 'catastro_jmm9'
    }

    try:
        url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(url)

        logger.info("Cargando datos desde PostgreSQL...")
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
        WHERE area_con IS NOT NULL OR puntaje IS NOT NULL OR ds_tipo_construccion IS NOT NULL
        LIMIT 100000
        """

        df = pd.read_sql_query(query, con=engine)
        logger.info(f"✓ {len(df):,} registros cargados\n")

        # Estandarización básica
        df['estrato'] = df['estrato'].astype(str)
        df['area_construida_imputada'] = 0
        df['puntaje_imputado'] = 0
        df['tipo_construccion_imputado'] = 0

        # Ejecutar tubería
        tuberia = TuberiaImputacionML(df, nombre_dataset='EAGIC_Catastro')
        df_imputado = tuberia.ejecutar_tuberia_completa()

        # Guardar resultados
        Path('outputs').mkdir(exist_ok=True)
        tuberia.guardar_modelos()
        tuberia.guardar_reporte(f'outputs/reporte_ml_{tuberia.timestamp}.json')

        # Guardar datos imputados
        df_imputado.to_csv(f'outputs/datos_imputados_{tuberia.timestamp}.csv', index=False)
        logger.info(f"✓ Datos imputados guardados\n")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
