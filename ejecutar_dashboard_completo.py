"""
Ejecutar DASHBOARD COMPLETO con mapa corregido
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent / 'modulos'))

print("\n" + "="*90)
print("  GENERANDO DASHBOARD COMPLETO - MAPA CON POPUPS CORREGIDOS")
print("="*90 + "\n")

# Crear datos de muestra si no existen
try:
    # Intentar cargar datos existentes
    df_limpio = pd.read_csv('outputs/datos/02_datos_limpios.csv')
    logger.info(f"[OK] Datos cargados: {len(df_limpio)} registros")
except:
    # Crear datos de demostración
    logger.info("Creando datos de demostración...")
    np.random.seed(42)

    barrios = [
        'El Poblado', 'Laureles', 'La Candelaria', 'Belén', 'Buenos Aires',
        'Castilla', 'Doce de Octubre', 'Robledo', 'Villa Hermosa', 'Manrique',
        'Popular', 'Santa Cruz', 'San Javier', 'Aranjuez', 'Guayabal',
        'Moravia', 'Villatina', 'Santo Domingo Savio', 'La América', 'Pablo VI'
    ]

    data = []
    for barrio in barrios:
        n_predios = np.random.randint(200, 1200)
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

    df_limpio = pd.DataFrame(data)
    logger.info(f"[OK] {len(df_limpio):,} registros generados")

print(f"\nDataset: {len(df_limpio):,} predios en {df_limpio['barrio_nombre'].nunique()} barrios\n")

# Importar y crear dashboard
try:
    from dashboard import DashboardSaludDato

    print("[1/3] Inicializando dashboard...\n")

    dashboard = DashboardSaludDato(
        df_original=df_limpio,
        df_limpio=df_limpio,
        df_imputado=df_limpio,
        nombre='Dashboard_Completo_Barrios'
    )

    print("[2/3] Generando gráficos y mapa...\n")

    # Generar dashboard completo
    timestamp = dashboard.timestamp
    output_html = f'outputs/visualizaciones/dashboard_salud_dato_{timestamp}.html'

    dashboard.crear_dashboard_html(output_html)

    print(f"\n[3/3] Dashboard completado\n")

    print("="*90)
    print(f"\n✅ ARCHIVO GENERADO: {output_html}\n")

    # Verificar que existe el archivo
    if Path(output_html).exists():
        print(f"Tamaño: {Path(output_html).stat().st_size / 1024 / 1024:.2f} MB")
        print(f"\nAbriendo en navegador...\n")

        # Abrir en navegador
        import webbrowser
        import time

        webbrowser.open(f'file:///{Path(output_html).resolve()}')
        time.sleep(3)

        print(f"URL: file:///{Path(output_html).resolve()}\n")
        print("="*90)
        print("\n✅ Dashboard abierto en navegador")
        print("\n📍 PRUEBA EL MAPA:")
        print("   1. Pasa el cursor sobre los barrios para ver resumen")
        print("   2. Haz CLICK en un barrio para ver información completa")
        print("   3. Verifica que los datos se muestren correctamente\n")

    else:
        logger.error(f"Error: Archivo no generado")

except Exception as e:
    logger.error(f"Error generando dashboard: {e}")
    import traceback
    traceback.print_exc()

print("="*90 + "\n")
