# Technical Documentation - Cadastral Data Imputation Pipeline

## 1. Architecture Overview

The pipeline follows a modular, sequential design:

```
Data Source (PostgreSQL)
    ↓
Data Profiling (Quality Assessment)
    ↓
ETL Pipeline (Cleaning & Validation)
    ↓
ML Training (Model Development)
    ↓
Dashboard & Reporting (Visualization)
```

### Design Principles
- Modularity: Each stage operates independently
- Traceability: All transformations logged with timestamps
- Reproducibility: Deterministic processing with fixed random seeds
- Scalability: Batch processing compatible with large datasets

## 2. Data Profiling Module

### Objective
Perform comprehensive quality diagnostics on raw data.

### Methodology

#### Missing Value Analysis
```
- Count and percentage per column
- Pattern detection (MCAR, MAR, MNAR)
- Correlation with other missing values
```

#### Statistical Analysis
```
- Distribution analysis (mean, median, std, quartiles)
- Outlier detection using IQR method
- Skewness and kurtosis measurement
```

#### Categorical Analysis
```
- Unique value counts (cardinality)
- Frequency distribution
- Dominant category percentage
```

### Quality Score Calculation

```
Score = (Completitud * 0.40) + 
         (Consistencia * 0.30) + 
         (Validez * 0.20) + 
         (Formato * 0.10)
```

Where:
- **Completitud** (Completeness): % of non-null values
- **Consistencia** (Consistency): % of logically valid values
- **Validez** (Validity): % conforming to expected ranges
- **Formato** (Format): % matching expected data types

### Output

Generates:
- JSON profile with detailed metrics
- Text report with summary statistics
- Quality scorecard (0-100)

## 3. ETL Pipeline Module

### Data Cleaning Stages

#### 1. Validation
```python
- Schema validation (expected columns present)
- Data type checking
- Value range validation
- Required field verification
```

#### 2. Deduplication
```python
- Primary key uniqueness check
- Full record comparison for exact duplicates
- Fuzzy matching for near-duplicates
- Retention strategy (keep first occurrence)
```

#### 3. Standardization
```python
- String normalization (trim, lowercase where appropriate)
- Date format standardization
- Numeric precision alignment
- Category value normalization
```

#### 4. Feature Engineering
```python
- Commercial property flag: is_comercial
- Valuation per m2: avaluo_por_m2
- Imputation indicator flags
- Derived geospatial features
```

### Quality Metrics

Tracks:
- Records retained (%)
- Duplicates removed
- Invalid values corrected
- Features added

## 4. Machine Learning Module

### Problem Framing

Three separate regression/classification tasks:

#### Task 1: Area Imputation
- Target: area_construida (numeric)
- Type: Regression
- Features: estrato, barrio, avaluo_total, puntaje, tipo_construccion

#### Task 2: Score Imputation
- Target: puntaje (numeric, 0-100)
- Type: Regression
- Features: estrato, barrio, avaluo_total, area_construida, tipo_construccion

#### Task 3: Construction Type Prediction
- Target: tipo_construccion (categorical)
- Type: Classification
- Features: estrato, barrio, avaluo_total, area_construida, puntaje

### Model Selection

#### Regression Models Evaluated
1. **Random Forest Regressor**
   - n_estimators: 200
   - max_depth: 25
   - min_samples_leaf: 3
   - Strengths: Handles non-linear relationships, robust to outliers

2. **Gradient Boosting Regressor**
   - n_estimators: 100
   - learning_rate: 0.1
   - max_depth: 5
   - Strengths: High accuracy, captures complex patterns

3. **Ridge Regression**
   - alpha: 1.0
   - Strengths: Fast, interpretable, regularized

#### Classification Models Evaluated
1. **Random Forest Classifier**
   - n_estimators: 200
   - max_depth: 20
   - Strengths: Multi-class handling, feature importance

2. **Gradient Boosting Classifier**
   - n_estimators: 100
   - learning_rate: 0.1
   - Strengths: Superior accuracy, handles class imbalance

### Validation Strategy

**Cross-Validation Approach:**
- 5-Fold Stratified Cross-Validation
- Maintains class distribution in splits
- Reports mean and std of each metric

**Metrics Computed:**

Regression:
```
- R-squared (R²): Variance explained (0-1)
- Mean Absolute Error (MAE): Average absolute deviation (units)
- Root Mean Square Error (RMSE): Penalizes large errors
- Mean Absolute Percentage Error (MAPE): Relative error (%)
```

Classification:
```
- Accuracy: Correct predictions (%)
- Precision: True positives / all positives
- Recall: True positives / all actual positives
- F1-Score: Harmonic mean of precision and recall
- Confusion Matrix: Detailed classification breakdown
```

### Preprocessing Pipeline

```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('onehot', OneHotEncoder(categorical_features=['barrio', 'tipo_construccion'])),
    ('scaler', StandardScaler()),
    ('model', RandomForestRegressor())
])
```

### Model Persistence

Selected model saved via joblib:
```python
import joblib
joblib.dump(model, 'modelo_catastro_area.pkl')
model_loaded = joblib.load('modelo_catastro_area.pkl')
```

## 5. Dashboard Module

### Visualization Components

#### 1. Quality Score Card
- Global score (0-100)
- Color-coded status (Red < 60, Yellow 60-75, Green > 75)
- Trend indicator vs. previous run

#### 2. Completeness Chart
- Bar chart of non-null percentages per feature
- Highlights most problematic columns
- Compares before/after ETL

#### 3. Imputation Summary
- Count of imputed records per variable
- Imputation method used
- Confidence score distribution

#### 4. Missing Value Heatmap
- Feature correlation with missingness
- Identifies patterns (e.g., "when X is null, Y tends to be null")
- Helps detect systematic issues

#### 5. Model Performance
- R² scores for regression tasks
- Accuracy scores for classification
- Cross-validation results

#### 6. Comparison Visualization
- Before/after niche distribution
- Outlier count comparison
- Data quality timeline

### Technology Stack

- **Plotly**: Interactive, responsive visualizations
- **HTML5**: Standalone outputs (no dependencies)
- **Bootstrap**: Responsive layout
- **JSON**: Data interchange for charts

## 6. Database Integration

### PostgreSQL Connection

```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@host:5432/database')
df = pd.read_sql_query(query, con=engine)
```

### Query Structure

```sql
SELECT 
    nm_mtcla_prdio AS id_predio,
    estrato_pre AS estrato,
    ds_barrio AS barrio_nombre,
    ava_total_ava AS avaluo_total,
    area_con AS area_construida,
    nm_ptje AS puntaje,
    ds_tipo_constru AS tipo_construccion
FROM catastro.insertar_predios_construccion
LIMIT 100000
```

### Connection Pooling

SQLAlchemy manages connection pooling automatically:
- Max connections: 20 (configurable)
- Timeout: 30 seconds
- Auto-recycling after 3600 seconds

## 7. Error Handling & Logging

### Logging Configuration

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
```

### Exception Handling

All modules implement try-except blocks:
- Database connection failures
- File I/O errors
- Model training failures
- Missing dependencies

### Validation Checkpoints

```
Load Data → Validate Schema → Profile → ETL → Validate Again → ML → Dashboard
      ↓              ↓           ↓      ↓          ↓          ↓        ↓
   Check OK?     Check OK?   Save    Check OK?  Check OK?  Save    Success
```

## 8. Performance Characteristics

### Typical Runtime Breakdown
(For 100,000 records)

```
Data Profiling:    2-3 minutes
ETL Pipeline:      3-5 minutes
Model Training:    5-10 minutes (includes CV)
Dashboard:         1-2 minutes
Total:             ~15 minutes
```

### Memory Requirements

```
100K records:     ~500 MB (with pandas overhead)
1M records:       ~5 GB
```

### Optimization Opportunities

1. **Batch Processing**: Split large datasets
2. **Caching**: Store intermediate results
3. **Parallel Training**: Use n_jobs=-1 in models
4. **Feature Selection**: Reduce feature dimensionality
5. **Early Stopping**: In gradient boosting

## 9. Reproducibility

### Deterministic Processing

All sources of randomness controlled:

```python
import random
import numpy as np
from sklearn.utils.validation import check_random_state

random.seed(42)
np.random.seed(42)
random_state = 42

# In model constructors:
RandomForestRegressor(random_state=42)
train_test_split(..., random_state=42)
cross_val_score(..., random_state=42)
```

### Timestamp Tracking

All outputs include timestamp:
```
01_perfil_datos_20250527_091500.json
02_datos_limpios_20250527_091500.csv
03_datos_imputados_20250527_091500.csv
04_reporte_dashboard_20250527_091500.json
```

### Configuration Management

Settings centralized in `main.py`:
```python
DB_CONFIG = {...}
QUERY_DATOS = """..."""
CANTIDAD_REGISTROS = "FULL"
```

## 10. Monitoring & Alerts

### Quality Thresholds

```python
if quality_score < 60:
    logger.warning("CRITICAL: Quality score below 60")
if retention_rate < 0.90:
    logger.warning("WARNING: Data retention below 90%")
if model_r2 < 0.60:
    logger.warning("WARNING: Model R² below 0.60")
```

### Logging Output

All stages logged to console and optionally to file:
```
[2025-05-27 09:15:00] INFO - Data Profiling: Completitud: 73.45%
[2025-05-27 09:15:30] INFO - ETL Pipeline: 100,000 → 98,756 records
[2025-05-27 09:15:45] INFO - ML Training: Best model R² = 0.8923
[2025-05-27 09:16:00] INFO - Dashboard: Generated successfully
```

## 11. Extension Points

### Adding New Features

1. **Custom Models**: Inherit from BaseEstimator
2. **New Visualizations**: Use Plotly templates
3. **Additional Metrics**: Extend metric calculation functions
4. **External Data Sources**: Use pandas I/O methods

### API Development

```python
# Future: FastAPI endpoints
@app.post("/predict/area")
def predict_area(features: FeatureSchema):
    model = joblib.load('modelo_catastro_area.pkl')
    return model.predict(features)
```

## 12. References

### Libraries & Documentation
- [Pandas Documentation](https://pandas.pydata.org/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Plotly Documentation](https://plotly.com/)

### Machine Learning References
- Scikit-learn User Guide: Cross-Validation
- Feature Engineering principles
- Imbalanced learning techniques
- Time series considerations

---

**Last Updated:** May 2025  
**Version:** 1.0  
**Status:** Production Ready
