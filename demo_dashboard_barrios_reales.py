"""
Demostración del DASHBOARD actualizado con mapa de barrios reales
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'modulos'))
from dashboard import DashboardSaludDato

# Crear datos de muestra
np.random.seed(42)

barrios = [
    'El Poblado', 'Laureles', 'La Candelaria', 'Belén', 'Buenos Aires',
    'Castilla', 'Doce de Octubre', 'Robledo', 'Villa Hermosa', 'Manrique',
    'Popular', 'Santa Cruz', 'San Javier', 'Aranjuez', 'Guayabal'
]

data = []
for barrio in barrios:
    n_predios = np.random.randint(150, 1500)
    for _ in range(n_predios):
        data.append({
            'id_predio': f'PRED_{barrio.replace(" ", "")}_{_:05d}',
            'barrio_nombre': barrio,
            'estrato': np.random.choice([1, 2, 3, 4, 5, 6], p=[0.15, 0.20, 0.25, 0.20, 0.15, 0.05]),
            'avaluo_total': np.random.uniform(50000000, 500000000),
            'area_construida': np.random.uniform(50, 500),
            'puntaje': np.random.randint(1, 100),
            'tipo_construccion': np.random.choice(['Residencial', 'Comercial', 'Mixto']),
        })

df = pd.DataFrame(data)

print("\n" + "="*90)
print("  DASHBOARD ACTUALIZADO - MAPA CON BARRIOS REALES")
print("="*90 + "\n")

print(f"[OK] Datos: {len(df):,} predios en {len(barrios)} barrios\n")

# Crear dashboard
print("Generando dashboard con mapa actualizado...\n")

dashboard = DashboardSaludDato(
    df_original=df,
    df_limpio=df,
    df_imputado=df,
    nombre='Analisis_Barrios_Medellin'
)

# Generar mapa
dashboard.crear_mapa_geografico()

# Generar dashboard completo
timestamp = dashboard.timestamp
ruta_dashboard = f'outputs/visualizaciones/dashboard_barrios_reales_{timestamp}.html'

dashboard.crear_dashboard_html(ruta_dashboard)

print(f"\n[OK] Dashboard generado: {ruta_dashboard}")
print(f"\nAbriendo en navegador...\n")

# Abrir en navegador
import webbrowser
import time

webbrowser.open(f'file:///{Path(ruta_dashboard).resolve()}')
time.sleep(2)

print(f"Dashboard URL: {Path(ruta_dashboard).resolve()}\n")
