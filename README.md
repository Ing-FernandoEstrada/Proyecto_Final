# 🚀 PROYECTO FINAL: IMPUTACIÓN INTELIGENTE CON MACHINE LEARNING

**Solución completa MLOps para diagnóstico, limpieza e imputación de datos catastrales de Medellín**

---

## 📋 Descripción General

Este proyecto implementa una **tubería de vanguardia de Ciencia de Datos** para resolver el problema de valores faltantes e ilógicos en el área construida de la ciudad de Medellín.

### Componentes Principales

1. **Data Profiling Automatizado** - Diagnóstico exhaustivo de calidad
2. **ETL Pipeline** - Filtro de pureza con validaciones
3. **Machine Learning Training** - Imputación inteligente con modelos avanzados
4. **Dashboard de Salud** - Visualización interactiva de resultados
5. **🗺️ Mapa Geográfico** - Visualización espacial de predios por barrio

---

## 🌟 Características Destacadas

### 📊 Dashboard Interactivo Completo
- **Métricas de Calidad**: Score global, completitud por columna
- **Análisis de Imputaciones**: Registros imputados por variable
- **Comparativas**: Antes vs Después del procesamiento
- **Mapa de Nulos**: Patrón visual de datos faltantes
- **🗺️ Mapa Geográfico**: Distribución de predios y avalúos por barrio de Medellín

### 🤖 Modelos de Machine Learning
- **Random Forest**: Mejor rendimiento para imputación de área construida
- **Validación Cruzada**: Evaluación robusta de modelos
- **Métricas Avanzadas**: R², MAE, RMSE por modelo

### 📈 Visualizaciones Profesionales
- Gráficos interactivos con Plotly
- Mapas geográficos con OpenStreetMap
- Diseño responsive y moderno
- Exportación a HTML para compartir

### 🗺️ Mapa Geográfico Interactivo
- **Ubicación por Barrio**: Visualización espacial de predios en Medellín
- **Tamaño de Marcadores**: Proporcional a cantidad de predios por barrio
- **Colores**: Escala de avalúo total (más oscuro = mayor valor)
- **Tooltips Informativos**: Cantidad de predios, avalúo total y promedio
- **Navegación**: Zoom y pan interactivos sobre mapa base

---

## 🏗️ Estructura del Proyecto

```
Proyecto_Final/
├── main.py                    # Orquestador principal
├── 01_data_profiling.py      # Diagnóstico automatizado
├── 02_etl_pipeline.py        # Limpieza y validación
├── 03_ml_training.py         # Entrenamiento de modelos
├── 04_dashboard.py           # Visualizaciones
├── pyproject.toml            # Dependencias (uv)
├── README.md                 # Este archivo
└── outputs/                  # Resultados generados
    ├── datos/               # Datos procesados
    ├── modelos/             # Modelos ML persistidos
    ├── reportes/            # Reportes JSON
    └── visualizaciones/     # Dashboard HTML
```

---

## 🔧 Instalación y Configuración

### 1. Requisitos Previos

- **Python 3.10+**
- **PostgreSQL** acceso a base de datos catastral
- **pip** o **uv** (gestor de dependencias)

### 2. Instalar Dependencias

**Con `uv` (recomendado - más rápido):**

```bash
uv pip install pandas numpy scikit-learn sqlalchemy plotly joblib
```

**Con `pip`:**

```bash
pip install pandas numpy scikit-learn sqlalchemy plotly joblib
```

### 3. Configurar Credenciales PostgreSQL

En `main.py`, actualiza las credenciales:

```python
DB_CONFIG = {
    'user': 'tu_usuario',
    'password': 'tu_contraseña',
    'host': 'tu_host',
    'port': '5432',
    'database': 'tu_base_datos'
}
```

**Nota:** Las credenciales actuales en el código apuntan a la BD de producción.

---

## 📊 Resultados y Ejemplos

### Métricas de Calidad Típicas
- **Completitud Global**: 99.74%
- **Registros Procesados**: 97,404
- **Score de Calidad**: 95/100
- **Imputaciones Realizadas**: Área construida, Puntaje, Tipo construcción

### Mapa Geográfico
El dashboard incluye un mapa interactivo que muestra:
- **La Candelaria**: Centro histórico con alta densidad de predios
- **El Poblado**: Zona residencial premium con avalúos elevados
- **Laureles**: Área comercial con mezcla de usos
- **Belén**: Zona en desarrollo con crecimiento urbano
- **Aranjuez**: Distrito industrial y residencial

**Características del Mapa:**
- Marcadores proporcionales al número de predios
- Colores que representan el avalúo total acumulado
- Tooltips con estadísticas detalladas por barrio
- Navegación completa sobre mapa base de OpenStreetMap

---

## 🚀 Uso

## 🚀 Uso

### Opción 1: Ejecutar Tubería Completa (Recomendado)

```bash
python main.py
```

Esto ejecutará secuencialmente:
1. ✅ Data Profiling (diagnóstico)
2. ✅ ETL Pipeline (limpieza)
3. ✅ ML Training (imputación)
4. ✅ Dashboard (visualización)

**Tiempo estimado:** 5-15 minutos (depende del tamaño de datos)

### Opción 2: Ejecutar Módulos Individualmente

**2.1. Data Profiling**

```bash
python 01_data_profiling.py
```

Genera:
- `outputs/reportes/perfil_datos_TIMESTAMP.json` - Perfil completo
- `outputs/reportes/reporte_profiling_TIMESTAMP.txt` - Reporte legible

**2.2. ETL Pipeline**

```bash
python 02_etl_pipeline.py
```

Genera:
- `outputs/datos/datos_limpios_TIMESTAMP.csv` - Datos limpios
- `outputs/reportes/reporte_etl_TIMESTAMP.json` - Reporte de cambios

**2.3. ML Training**

```bash
python 03_ml_training.py
```

Genera:
- `outputs/modelos/modelo_catastro_area_TIMESTAMP.pkl` - Modelo area_construida
- `outputs/modelos/modelo_catastro_puntaje_TIMESTAMP.pkl` - Modelo puntaje
- `outputs/modelos/modelo_catastro_tipo_TIMESTAMP.pkl` - Modelo tipo_construccion
- `outputs/datos/datos_imputados_TIMESTAMP.csv` - Datos con imputaciones
- `outputs/reportes/reporte_ml_TIMESTAMP.json` - Métricas de modelos

**2.4. Dashboard**

```bash
python 04_dashboard.py
```

Genera:
- `outputs/visualizaciones/dashboard_salud_dato_TIMESTAMP.html` - **Abrir en navegador 🌐**

---

## 📊 Resultados y Salidas

### Datos Procesados

| Archivo | Descripción | Uso |
|---------|------------|-----|
| `datos_limpios_*.csv` | Datos después de ETL | Entrada para ML |
| `datos_imputados_*.csv` | Datos con imputaciones completadas | Base limpia para análisis |

### Modelos Entrenados

| Modelo | Variable | Métrica | Descripción |
|--------|----------|---------|-------------|
| `modelo_catastro_area_*.pkl` | area_construida | R² | Predice área en m² |
| `modelo_catastro_puntaje_*.pkl` | puntaje | R² | Predice puntaje (0-100) |
| `modelo_catastro_tipo_*.pkl` | tipo_construccion | Accuracy | Clasifica tipo de construcción |

### Reportes

| Reporte | Contenido | Formato |
|---------|-----------|---------|
| `01_perfil_datos_*.json` | Nulos, ceros, outliers por columna | JSON |
| `02_reporte_etl_*.json` | Cambios en limpieza | JSON |
| `03_reporte_ml_*.json` | Métricas de validación cruzada | JSON |
| `04_reporte_dashboard_*.json` | Resumen de calidad global | JSON |

### Dashboard Interactivo

**Archivo:** `dashboard_salud_dato_TIMESTAMP.html`

Contiene:
- 🎯 **Score de Calidad Global** (0-100)
- 📊 **Completitud por Columna** (gráfico barras)
- 📈 **Comparativa Antes/Después** (nulos, duplicados)
- 🔧 **Registros Imputados** (por variable)
- 🗺️ **Patrón de Nulos** (heatmap)

**Cómo abrir:**
```bash
# En terminal, abre directamente:
open outputs/visualizaciones/dashboard_salud_dato_*.html  # macOS
xdg-open outputs/visualizaciones/dashboard_salud_dato_*.html  # Linux
start outputs/visualizaciones/dashboard_salud_dato_*.html  # Windows
```

---

## 📈 Ejemplo de Ejecución

```
$ python main.py

[2026-05-07 14:30:15] INFO - Proyecto Final: Imputación Inteligente con ML
[2026-05-07 14:30:15] INFO - ✓ Conexión a PostgreSQL establecida
[2026-05-07 14:30:22] INFO - Cargando datos (LIMIT 100000)...
[2026-05-07 14:30:25] INFO - ✓ 100,000 registros cargados

================================================================================
ETAPA 1: DATA PROFILING
================================================================================
[2026-05-07 14:30:26] INFO - Score Global: 72.34/100 (ACEPTABLE)
[2026-05-07 14:30:26] INFO - Completitud: 73.45% | Consistencia: 99.87%

================================================================================
ETAPA 2: ETL PIPELINE
================================================================================
[2026-05-07 14:30:45] INFO - Registros: 100,000 → 98,756
[2026-05-07 14:30:45] INFO - Retención: 98.76%

================================================================================
ETAPA 3: ML TRAINING
================================================================================
[2026-05-07 14:30:46] INFO - IMPUTACIÓN 1: area_construida
[2026-05-07 14:31:12] INFO - 🏆 MEJOR MODELO: GradientBoosting (R² = 0.8923)

[2026-05-07 14:31:15] INFO - IMPUTACIÓN 2: puntaje
[2026-05-07 14:31:28] INFO - 🏆 MEJOR MODELO: RandomForest (R² = 0.7654)

[2026-05-07 14:31:30] INFO - IMPUTACIÓN 3: tipo_construccion
[2026-05-07 14:31:42] INFO - 🏆 MEJOR MODELO: RandomForest (Accuracy = 0.9234)

================================================================================
ETAPA 4: DASHBOARD
================================================================================
[2026-05-07 14:31:50] INFO - ✓ Dashboard guardado: outputs/visualizaciones/...

================================================================================
REPORTE FINAL
================================================================================
📊 Registros: 100,000 → 98,756 (retención: 98.76%)
🎯 Score Final: 94.23/100 (EXCELENTE)
🤖 Modelos: 3 entrenados (R² > 0.76)
📈 Imputaciones: 2,345 área | 1,823 puntaje | 890 tipo

✅ TUBERÍA COMPLETADA EXITOSAMENTE
```

---

## 🔍 Detalles Técnicos

### 1. Data Profiling

- **Nulos:** Cuenta, porcentaje, patrones correlacionados
- **Numéricos:** Distribución, outliers (IQR), ceros
- **Categóricos:** Cardinalidad, dominancia
- **Scores:** Completitud, consistencia, estado general

### 2. ETL Pipeline

- **Validación:** Esquema, tipos de datos
- **Limpieza:** Duplicados, valores inválidos
- **Estandarización:** Formatos, espacios, mayúsculas
- **Features:** es_comercial, avaluo_por_m2, flags de imputación

### 3. Machine Learning

#### Modelos Usados

**Regresión (area_construida, puntaje):**
- Random Forest Regressor
- Gradient Boosting Regressor
- Ridge Regression

**Clasificación (tipo_construccion):**
- Random Forest Classifier
- Gradient Boosting Classifier

#### Técnicas

- ✅ **Validación Cruzada (5-Fold)** para robustez
- ✅ **Hyperparameter Tuning** implícito en modelos
- ✅ **One-Hot Encoding** para categóricas
- ✅ **StandardScaler** para numéricas
- ✅ **Pipeline** para reproducibilidad

#### Features Predictivas

| Variable | Predictores |
|----------|------------|
| area_construida | estrato, barrio, avaluo, puntaje, tipo_construccion |
| puntaje | estrato, barrio, avaluo, area, tipo_construccion |
| tipo_construccion | estrato, barrio, avaluo, area, puntaje |

### 4. Dashboard

- **Tecnología:** Plotly (interactivo)
- **Formatos:** HTML standalone + JSON
- **Gráficos:** 6 visualizaciones dinámicas
- **Compatible:** Cualquier navegador moderno

---

## ⚙️ Configuración Avanzada

### Ajustar Cantidad de Datos

En `main.py`, modifica:

```python
CANTIDAD_REGISTROS = "10000"  # Cambiar este número

QUERY_DATOS = """
...
LIMIT 10000  # Cambiar este también
"""
```

### Cambiar Número de Registros de Entrenamiento

En `03_ml_training.py`, línea ~250:

```python
df = pd.read_sql_query(query, con=engine)
# LIMIT 100000  → cambiar a otra cantidad
```

### Ajustar Hyperparámetros

En `03_ml_training.py`, modifica parámetros de modelos:

```python
RandomForestRegressor(
    n_estimators=200,    # Aumentar para más precisión (más lento)
    max_depth=25,        # Ajustar profundidad
    min_samples_leaf=3   # Muestras mínimas por hoja
)
```

---

## 🎯 Interpretación de Resultados

### Score de Calidad Global

- **90-100:** ✅ EXCELENTE - Datos listos para producción
- **75-89:** ✓ BUENA - Pocas imputaciones necesarias
- **60-74:** ⚠️ ACEPTABLE - Imputaciones significativas realizadas
- **<60:** ❌ CRÍTICA - Revisar fuente de datos

### Métricas de ML

| Métrica | Interpretación | Rango |
|---------|----------------|-------|
| **R²** | % varianza explicada | 0-1 (≥0.70 = bueno) |
| **MAE** | Error medio absoluto en m² | Menor es mejor |
| **RMSE** | Raíz del error cuadrático | Penaliza outliers |
| **Accuracy** | % clasificaciones correctas | 0-1 (≥0.85 = bueno) |

---

## 🐛 Troubleshooting

### Error: "No module named 'sqlalchemy'"

```bash
pip install sqlalchemy
```

### Error: "Connection refused" PostgreSQL

Verificar:
1. Credenciales en `DB_CONFIG` (usuario, password, host, port)
2. Base de datos existe
3. Red tiene acceso a host

### Error: "MemoryError" con muchos registros

Reducir en `main.py`:

```python
QUERY_DATOS = """
...
LIMIT 50000  # Reducir de 100000
"""
```

### Dashboard no se abre en navegador

Abrir manualmente:
1. Ir a `outputs/visualizaciones/`
2. Buscar archivo `dashboard_salud_dato_*.html`
3. Doble-click o arrastra a navegador

---

## 📚 Referencia de Archivos

### Código Principal

- **main.py** - Orquestador. Ejecuta de aquí.
- **01_data_profiling.py** - Diagnóstico. Independiente.
- **02_etl_pipeline.py** - Limpieza. Independiente.
- **03_ml_training.py** - ML. Recibe datos limpios de ETL.
- **04_dashboard.py** - Visualización. Requiere datos procesados.

### Configuración

- **pyproject.toml** - Dependencias de proyecto
- **uv.lock** - Lock file (si usas uv)

---

## 🎓 Aprendizajes y Mejores Prácticas

✅ **Implementado:**
- Pipeline reproducible end-to-end
- Validación cruzada exhaustiva
- Persistencia de modelos (joblib)
- Logging y reportes automáticos
- Código comentado y profesional
- Estructura modular y reutilizable

**Próximos pasos (opcionales):**
- Reentrenamiento automático (cron)
- API REST para predicciones (FastAPI)
- CI/CD con GitHub Actions
- Monitoring en producción (Prometheus)

---

## 📞 Contacto

**Proyecto Final - Ciencia de Datos Avanzada**  
Autores: Juan Diego, Fernando Estrada, Juan Manuel
Dataset: EAGIC - Catastro de Medellín

---

**Última actualización:** 2026-05-07

