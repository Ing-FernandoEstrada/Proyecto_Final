"""
Script de demostracion del mapa geografico mejorado
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'modulos'))
from dashboard import DashboardSaludDato

# Crear datos de muestra realistas para Medellin
np.random.seed(42)

barrios = [
    'La Candelaria', 'Laureles', 'El Poblado', 'Belen', 'Aranjuez',
    'Castilla', 'Doce de Octubre', 'Robledo', 'Villa Hermosa', 'Buenos Aires',
    'Manrique', 'Popular', 'Santa Cruz', 'San Javier', 'Guayabal'
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
            'tipo_construccion': np.random.choice(['Residencial', 'Comercial', 'Mixto', 'Industrial']),
        })

df = pd.DataFrame(data)

print("\n" + "="*80)
print("DEMOSTRACION: MAPA GEOGRAFICO MEJORADO DE MEDELLIN")
print("="*80 + "\n")

print(f"[OK] Datos creados: {len(df):,} predios en {len(barrios)} barrios")
print(f"[OK] Columnas: {', '.join(df.columns)}\n")

# Crear dashboard
print("Generando dashboard con mapa mejorado...")
dashboard = DashboardSaludDato(
    df_original=df,
    df_limpio=df,
    df_imputado=df,
    nombre='EAGIC_Catastro_Demo'
)

# Generar solo el mapa
dashboard.crear_mapa_geografico()

# Crear HTML
html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa de Predios - Medellin</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            letter-spacing: 1px;
        }}
        .header p {{
            margin: 15px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            padding: 20px;
            overflow: hidden;
        }}
        .chart {{
            width: 100%;
            height: 100%;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: white;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MAP INTERACTIVO DE PREDIOS</h1>
        <p>Medellin - Analisis Catastral 2026</p>
        <p style="font-size: 0.9em; margin-top: 20px;">Pasa el cursor sobre los puntos para ver informacion detallada</p>
    </div>

    <div class="container">
        <div class="info-grid">
            <div class="stat-card">
                <h3>Total de Predios</h3>
                <div class="value">{len(df):,}</div>
            </div>
            <div class="stat-card">
                <h3>Barrios Analizados</h3>
                <div class="value">{df['barrio_nombre'].nunique()}</div>
            </div>
            <div class="stat-card">
                <h3>Avaluo Promedio</h3>
                <div class="value">${df['avaluo_total'].mean():,.0f}</div>
            </div>
            <div class="stat-card">
                <h3>Estrato Promedio</h3>
                <div class="value">{df['estrato'].mean():.1f}</div>
            </div>
        </div>

        <div class="card">
            {dashboard.figs['mapa_geografico'].to_html(include_plotlyjs=False, div_id='mapa')}
        </div>
    </div>

    <div class="footer">
        <p>SISTEMA DE MONITOREO DE CALIDAD CATASTRAL | Dashboard Interactivo</p>
        <p>Generado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""

output_path = 'outputs/visualizaciones/mapa_mejorado_demo.html'
Path(output_path).parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n[OK] Dashboard generado: {output_path}")
print("\nPara ver el mapa, abre en el navegador:")
print(f"  {Path(output_path).resolve()}\n")

# Mostrar estadisticas por barrio
print("\n" + "="*80)
print("ESTADISTICAS POR BARRIO")
print("="*80 + "\n")

barrio_stats = df.groupby('barrio_nombre').agg({
    'id_predio': 'count',
    'avaluo_total': ['sum', 'mean'],
    'area_construida': 'mean',
    'estrato': 'mean'
}).round(2)

barrio_stats.columns = ['Predios', 'Avaluo Total', 'Avaluo Prom', 'Area Prom', 'Estrato']
barrio_stats = barrio_stats.sort_values('Predios', ascending=False)

print(barrio_stats.to_string())
print("\n")
