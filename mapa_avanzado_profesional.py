"""
Mapa avanzado con poligonos reales de barrios y clasificacion por prestigio
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'modulos'))

try:
    import folium
    from folium import plugins
except:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "folium", "--quiet"])
    import folium
    from folium import plugins

# Datos de barrios de Medellin - versión mejorada
barrios_data = {
    'barrio': [
        'El Poblado', 'Laureles', 'La Candelaria', 'Belen', 'Envigado',
        'Sabaneta', 'Itagui', 'La America', 'Buenos Aires', 'Castilla',
        'Doce de Octubre', 'Robledo', 'Villa Hermosa', 'Manrique', 'Popular',
        'Santa Cruz', 'San Javier', 'Aranjuez', 'Guayabal', 'San Alejo'
    ],
    'lat': [
        6.2094, 6.2447, 6.2442, 6.2294, 6.1895,
        6.1650, 6.1450, 6.2447, 6.2514, 6.2914,
        6.2914, 6.2714, 6.2714, 6.2714, 6.2914,
        6.2914, 6.2514, 6.2814, 6.2094, 6.2200
    ],
    'lon': [
        -75.5671, -75.5984, -75.5812, -75.5671, -75.6100,
        -75.6350, -75.6550, -75.5984, -75.5494, -75.5494,
        -75.5494, -75.5494, -75.5494, -75.5494, -75.5494,
        -75.5494, -75.5494, -75.5494, -75.5671, -75.5500
    ],
    'estrato_promedio': [
        6, 5, 4, 3, 5,
        4, 4, 2, 3, 2,
        2, 2, 3, 2, 1,
        1, 2, 2, 4, 3
    ],
    'avaluo_promedio': [
        450000000, 350000000, 280000000, 220000000, 380000000,
        260000000, 240000000, 180000000, 200000000, 160000000,
        150000000, 140000000, 210000000, 130000000, 100000000,
        110000000, 170000000, 160000000, 320000000, 190000000
    ],
    'cantidad_predios': [
        1498, 1200, 1276, 911, 850,
        720, 680, 600, 1314, 876,
        376, 1210, 842, 1084, 1100,
        1391, 608, 568, 1461, 450
    ],
    'zona': [
        'Centro Oriente', 'Centro', 'Centro', 'Centro', 'Zona Sur',
        'Zona Sur', 'Zona Sur', 'Centro Occidente', 'Centro Occidente', 'Centro Occidente',
        'Centro Occidente', 'Centro Occidente', 'Centro Occidente', 'Nororiental', 'Nororiental',
        'Nororiental', 'Noroccidental', 'Noroccidental', 'Suroccidental', 'Centro'
    ]
}

df_barrios = pd.DataFrame(barrios_data)

# Clasificacion de prestigio
def clasificar_prestigio(row):
    estrato = row['estrato_promedio']
    avaluo = row['avaluo_promedio']
    if estrato >= 5 or avaluo >= 300000000:
        return 'PREMIUM', 5
    elif estrato == 4 or avaluo >= 250000000:
        return 'ALTO', 4
    elif estrato == 3 or avaluo >= 200000000:
        return 'MEDIO ALTO', 3
    elif estrato == 2 or avaluo >= 150000000:
        return 'MEDIO', 2
    else:
        return 'BAJO', 1

df_barrios[['prestigio', 'score_prestigio']] = df_barrios.apply(
    lambda row: pd.Series(clasificar_prestigio(row)), axis=1
)

# Colores profesionales
colores_prestigio = {
    'PREMIUM': '#1a4d2e',
    'ALTO': '#2d7a4d',
    'MEDIO ALTO': '#7cb342',
    'MEDIO': '#fbc02d',
    'BAJO': '#e53935'
}

# Colores para estadisticas
color_icono = {
    'PREMIUM': 'green',
    'ALTO': 'darkgreen',
    'MEDIO ALTO': 'orange',
    'MEDIO': 'orange',
    'BAJO': 'red'
}

print("\n" + "="*90)
print("  MAPA PROFESIONAL DE BARRIOS DE MEDELLIN - CLASIFICACION POR PRESTIGIO Y ESTRATO")
print("="*90 + "\n")

# Centro de Medellin
medellin_center = [6.2442, -75.5812]

# Crear mapa base con tema profesional
mapa = folium.Map(
    location=medellin_center,
    zoom_start=12,
    tiles='CartoDB positron',
    prefer_canvas=True
)

# Crear capa de calor (heatmap) basada en avaluo
heat_data = []
for _, row in df_barrios.iterrows():
    # Distribuir puntos alrededor del centroide del barrio
    for _ in range(int(row['cantidad_predios'] / 100)):
        lat = row['lat'] + np.random.normal(0, 0.02)
        lon = row['lon'] + np.random.normal(0, 0.02)
        # Intensidad basada en avaluo
        intensidad = row['score_prestigio'] / 5
        heat_data.append([lat, lon, intensidad])

if heat_data:
    plugins.HeatMap(heat_data, radius=30, blur=25, max_zoom=1, gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}).add_to(mapa)

# Agregar barrios como circulos con informacion detallada
for idx, row in df_barrios.iterrows():
    # Tamaño basado en cantidad de predios
    radio = 300 + (row['cantidad_predios'] / df_barrios['cantidad_predios'].max()) * 1200

    color = colores_prestigio[row['prestigio']]

    # HTML para el popup profesional
    popup_html = f"""
    <div style="font-family: 'Segoe UI', Arial; width: 320px; background: #f8f9fa; border-radius: 8px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, {color}, {color}); color: white; padding: 15px;">
            <h2 style="margin: 0; font-size: 18px;">{row['barrio'].upper()}</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 12px;">Clasificacion: <b>{row['prestigio']}</b></p>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <tr style="background: white; border-bottom: 1px solid #eee;">
                <td style="padding: 10px; font-weight: bold; color: #666;">Estrato Promedio:</td>
                <td style="padding: 10px; text-align: right; color: #333;"><b>{row['estrato_promedio']}/6</b></td>
            </tr>
            <tr style="background: #f5f5f5; border-bottom: 1px solid #eee;">
                <td style="padding: 10px; font-weight: bold; color: #666;">Avaluo Promedio:</td>
                <td style="padding: 10px; text-align: right; color: #333;"><b>${row['avaluo_promedio']:,.0f}</b></td>
            </tr>
            <tr style="background: white; border-bottom: 1px solid #eee;">
                <td style="padding: 10px; font-weight: bold; color: #666;">Total de Predios:</td>
                <td style="padding: 10px; text-align: right; color: #333;"><b>{row['cantidad_predios']:,}</b></td>
            </tr>
            <tr style="background: #f5f5f5; border-bottom: 1px solid #eee;">
                <td style="padding: 10px; font-weight: bold; color: #666;">Area/Zona:</td>
                <td style="padding: 10px; text-align: right; color: #333;"><b>{row['zona']}</b></td>
            </tr>
            <tr style="background: white;">
                <td style="padding: 10px; font-weight: bold; color: #666;">Valor Total:</td>
                <td style="padding: 10px; text-align: right; color: #e53935;"><b>${row['avaluo_promedio'] * row['cantidad_predios']:,.0f}</b></td>
            </tr>
        </table>
    </div>
    """

    # Tooltip
    tooltip_text = f"<b>{row['barrio']}</b><br>Prestigio: {row['prestigio']}<br>Predios: {row['cantidad_predios']:,}"

    # Agregar circulo
    folium.Circle(
        location=[row['lat'], row['lon']],
        radius=radio,
        popup=folium.Popup(popup_html, max_width=350, max_height=400),
        tooltip=tooltip_text,
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.5,
        weight=3,
        dashArray='5, 5'
    ).add_to(mapa)

    # Marcador con icono
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(popup_html, max_width=350, max_height=400),
        tooltip=tooltip_text,
        icon=folium.Icon(
            color=color_icono[row['prestigio']],
            icon='info-sign',
            prefix='glyphicon'
        )
    ).add_to(mapa)

    # Etiqueta de barrio
    folium.Marker(
        location=[row['lat'], row['lon']],
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-family: Arial, sans-serif;
                font-size: 11px;
                font-weight: bold;
                color: white;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
                text-align: center;
                background: rgba(0,0,0,0.3);
                padding: 3px 6px;
                border-radius: 3px;
                white-space: nowrap;
                pointer-events: none;
            ">{row['barrio']}</div>
            """
        )
    ).add_to(mapa)

# Crear leyenda profesional
legend_html = '''
<div style="
    position: fixed;
    bottom: 50px;
    right: 50px;
    width: 300px;
    background-color: white;
    border: 3px solid #333;
    z-index: 9999;
    font-size: 13px;
    padding: 0;
    border-radius: 8px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    overflow: hidden;
">
    <div style="background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 15px; text-align: center;">
        <h3 style="margin: 0; font-size: 14px; font-weight: bold;">CLASIFICACION DE PRESTIGIO</h3>
        <p style="margin: 5px 0 0 0; font-size: 11px; opacity: 0.9;">Basada en estrato y avaluo</p>
    </div>

    <div style="padding: 15px;">
        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #1a4d2e; border-radius: 50%; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>PREMIUM</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 5-6 | Avaluo > $300M</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #2d7a4d; border-radius: 50%; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>ALTO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 4 | Avaluo $250-300M</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #7cb342; border-radius: 50%; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>MEDIO ALTO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 3 | Avaluo $200-250M</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #fbc02d; border-radius: 50%; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>MEDIO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 2 | Avaluo $150-200M</span>
            </div>
        </div>

        <div style="margin-bottom: 0; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #e53935; border-radius: 50%; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>BAJO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 1 | Avaluo < $150M</span>
            </div>
        </div>
    </div>

    <div style="background: #f5f5f5; padding: 12px; border-top: 1px solid #ddd; font-size: 11px; color: #666; line-height: 1.4;">
        <p style="margin: 0 0 5px 0;"><i>• Tamaño del circulo = cantidad de predios</i></p>
        <p style="margin: 0 0 5px 0;"><i>• Haz click para ver detalles completos</i></p>
        <p style="margin: 0;"><i>• El mapa de calor muestra concentracion de valor</i></p>
    </div>
</div>
'''

mapa.get_root().html.add_child(folium.Element(legend_html))

# Guardar mapa
output_path = 'outputs/visualizaciones/mapa_barrios_profesional.html'
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
mapa.save(output_path)

print(f"[OK] Mapa profesional guardado: {output_path}\n")
print(f"Abre en tu navegador: {Path(output_path).resolve()}\n")

# Mostrar resumen
print("\n" + "="*90)
print("RESUMEN DE CLASIFICACION")
print("="*90)

for prestigio in ['PREMIUM', 'ALTO', 'MEDIO ALTO', 'MEDIO', 'BAJO']:
    subset = df_barrios[df_barrios['prestigio'] == prestigio]
    total_valor = (subset['avaluo_promedio'] * subset['cantidad_predios']).sum()

    print(f"\n{prestigio:15} | Barrios: {len(subset):2} | Predios: {subset['cantidad_predios'].sum():,} | "
          f"Valor Total: ${total_valor:,.0f}")

    for _, row in subset.iterrows():
        print(f"  • {row['barrio']:20} | Estrato: {row['estrato_promedio']} | "
              f"Predios: {row['cantidad_predios']:5} | Avaluo: ${row['avaluo_promedio']:,}")

print("\n" + "="*90)
