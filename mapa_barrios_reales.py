"""
Mapa profesional con poligonos reales de barrios de Medellin del area metropolitana
Usando barrios.geojson con clasificacion por prestigio
"""

import json
import pandas as pd
import numpy as np
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

print("\n" + "="*90)
print("  MAPA INTERACTIVO DE BARRIOS - AREA METROPOLITANA DE MEDELLIN")
print("="*90 + "\n")

# Cargar GeoJSON con los barrios reales
print("[1/5] Cargando GeoJSON con barrios...")
with open('barrios.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

print(f"    > {len(geojson_data['features'])} barrios cargados")

# Crear mapeo de estratos para los barrios conocidos
estratos_barrios = {
    'EL POBLADO': 6, 'LAURELES': 5, 'ALTOS DEL POBLADO': 6, 'GUAYABAL': 5,
    'LA CANDELARIA': 4, 'BELEN': 3, 'BUENOS AIRES': 3, 'VILLA HERMOSA': 3,
    'ARANJUEZ': 2, 'CASTILLA': 2, 'DOCE DE OCTUBRE #1': 2, 'DOCE DE OCTUBRE #2': 2,
    'ROBLEDO': 2, 'MANRIQUE CENTRAL #1': 2, 'MANRIQUE CENTRAL #2': 2, 'POPULAR': 1,
    'SANTA CRUZ': 1, 'SAN JAVIER #1': 2, 'SAN JAVIER #2': 2, 'MORAVIA': 1,
    'VILLATINA': 1, 'SANTO DOMINGO SAVIO #1': 1, 'SANTO DOMINGO SAVIO #2': 1,
    'LA AMÉRICA': 2, 'PABLO VI': 2, 'MANRIQUE ORIENTAL': 2,
}

# Clasificación por defecto según zona (comunas)
zonas_comunas = {
    '01': {'nombre': 'Popular', 'estrato': 1},
    '02': {'nombre': 'Santa Cruz', 'estrato': 1},
    '03': {'nombre': 'Manrique', 'estrato': 2},
    '04': {'nombre': 'Aranjuez', 'estrato': 2},
    '05': {'nombre': 'Castilla', 'estrato': 2},
    '06': {'nombre': 'Doce de Octubre', 'estrato': 2},
    '07': {'nombre': 'Robledo', 'estrato': 2},
    '08': {'nombre': 'Villa Hermosa', 'estrato': 3},
    '09': {'nombre': 'Buenos Aires', 'estrato': 3},
    '10': {'nombre': 'La Candelaria', 'estrato': 4},
    '11': {'nombre': 'Laureles', 'estrato': 5},
    '12': {'nombre': 'La América', 'estrato': 2},
    '13': {'nombre': 'San Javier', 'estrato': 2},
    '14': {'nombre': 'El Poblado', 'estrato': 6},
    '15': {'nombre': 'Guayabal', 'estrato': 5},
    '16': {'nombre': 'Belén', 'estrato': 3},
}

# Enriquecer GeoJSON con estratos
print("[2/5] Enriqueciendo datos con clasificacion de prestigio...")

barrios_procesados = []
for feature in geojson_data['features']:
    props = feature['properties']
    barrio_nombre = props.get('nombre', '').upper().strip()
    codigo = props.get('codigo', '')[:2]  # Primera parte es la comuna

    # Obtener estrato
    if barrio_nombre in estratos_barrios:
        estrato = estratos_barrios[barrio_nombre]
    elif codigo in zonas_comunas:
        estrato = zonas_comunas[codigo]['estrato']
    else:
        estrato = 2  # Defecto

    # Clasificar prestigio
    if estrato >= 5:
        prestigio = 'PREMIUM'
        score = 5
    elif estrato == 4:
        prestigio = 'ALTO'
        score = 4
    elif estrato == 3:
        prestigio = 'MEDIO ALTO'
        score = 3
    elif estrato == 2:
        prestigio = 'MEDIO'
        score = 2
    else:
        prestigio = 'BAJO'
        score = 1

    feature['properties']['estrato'] = estrato
    feature['properties']['prestigio'] = prestigio
    feature['properties']['score'] = score

    barrios_procesados.append({
        'nombre': props.get('nombre', ''),
        'estrato': estrato,
        'prestigio': prestigio,
        'score': score,
        'area': props.get('st_area(shape)', 0)
    })

df_barrios = pd.DataFrame(barrios_procesados)

print(f"    > Barrios Premium: {len(df_barrios[df_barrios['prestigio']=='PREMIUM'])}")
print(f"    > Barrios Alto: {len(df_barrios[df_barrios['prestigio']=='ALTO'])}")
print(f"    > Barrios Medio Alto: {len(df_barrios[df_barrios['prestigio']=='MEDIO ALTO'])}")
print(f"    > Barrios Medio: {len(df_barrios[df_barrios['prestigio']=='MEDIO'])}")
print(f"    > Barrios Bajo: {len(df_barrios[df_barrios['prestigio']=='BAJO'])}")

# Colores
colores_prestigio = {
    'PREMIUM': '#1a4d2e',
    'ALTO': '#2d7a4d',
    'MEDIO ALTO': '#7cb342',
    'MEDIO': '#fbc02d',
    'BAJO': '#e53935'
}

# Crear mapa
print("[3/5] Creando mapa interactivo...")
medellin_center = [6.2442, -75.5812]

mapa = folium.Map(
    location=medellin_center,
    zoom_start=12,
    tiles='CartoDB positron',
    prefer_canvas=True
)

# Agregar barrios como GeoJSON con polígonos
def get_color(feature):
    return colores_prestigio.get(feature['properties']['prestigio'], '#999999')

def get_popup(feature):
    props = feature['properties']
    barrio = props.get('nombre', 'Desconocido')
    estrato = props.get('estrato', 'N/A')
    prestigio = props.get('prestigio', 'N/A')
    area = props.get('st_area(shape)', 0)

    popup_html = f"""
    <div style="font-family: 'Segoe UI', Arial; width: 300px; background: #f8f9fa; border-radius: 8px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, {colores_prestigio.get(prestigio, '#999')}, {colores_prestigio.get(prestigio, '#999')}); color: white; padding: 12px;">
            <h3 style="margin: 0; font-size: 16px; word-wrap: break-word;">{barrio.title()}</h3>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <tr style="background: white; border-bottom: 1px solid #eee;">
                <td style="padding: 8px; font-weight: bold;">Prestigio:</td>
                <td style="padding: 8px; text-align: right;"><b>{prestigio}</b></td>
            </tr>
            <tr style="background: #f5f5f5; border-bottom: 1px solid #eee;">
                <td style="padding: 8px; font-weight: bold;">Estrato:</td>
                <td style="padding: 8px; text-align: right;"><b>{estrato}/6</b></td>
            </tr>
            <tr style="background: white;">
                <td style="padding: 8px; font-weight: bold;">Area:</td>
                <td style="padding: 8px; text-align: right;"><b>{area:,.0f} m²</b></td>
            </tr>
        </table>
    </div>
    """
    return folium.Popup(popup_html, max_width=350)

# Agregar capa de GeoJSON
print("[4/5] Agregando polígonos de barrios...")
folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        'fillColor': get_color(feature),
        'color': 'white',
        'weight': 1.5,
        'opacity': 0.8,
        'fillOpacity': 0.7,
        'dashArray': '2, 2'
    },
    popup=folium.GeoJsonPopup(
        fields=['nombre', 'estrato', 'prestigio'],
        aliases=['Barrio', 'Estrato', 'Prestigio'],
        localize=True
    ),
    tooltip=folium.GeoJsonTooltip(
        fields=['nombre', 'prestigio'],
        aliases=['Barrio', 'Clasificacion'],
        localize=True
    )
).add_to(mapa)

# Leyenda profesional
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
        <p style="margin: 5px 0 0 0; font-size: 11px; opacity: 0.9;">332 Barrios - Area Metropolitana</p>
    </div>

    <div style="padding: 15px;">
        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #1a4d2e; border-radius: 0px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>PREMIUM</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 5-6</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #2d7a4d; border-radius: 0px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>ALTO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 4</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #7cb342; border-radius: 0px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>MEDIO ALTO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 3</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #fbc02d; border-radius: 0px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>MEDIO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 2</span>
            </div>
        </div>

        <div style="margin-bottom: 0; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #e53935; border-radius: 0px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b>BAJO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 1</span>
            </div>
        </div>
    </div>

    <div style="background: #f5f5f5; padding: 12px; border-top: 1px solid #ddd; font-size: 11px; color: #666; line-height: 1.4;">
        <p style="margin: 0 0 5px 0;"><i>• Haz click en los barrios para ver detalles</i></p>
        <p style="margin: 0;"><i>• Pasa el cursor para ver el nombre</i></p>
    </div>
</div>
'''

mapa.get_root().html.add_child(folium.Element(legend_html))

# Guardar mapa
print("[5/5] Guardando mapa...")
output_path = 'outputs/visualizaciones/mapa_barrios_reales_medellin.html'
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
mapa.save(output_path)

print(f"\n[OK] Mapa guardado: {output_path}\n")

# Estadísticas
print("\n" + "="*90)
print("RESUMEN POR CLASIFICACION DE PRESTIGIO")
print("="*90)

for prestigio in ['PREMIUM', 'ALTO', 'MEDIO ALTO', 'MEDIO', 'BAJO']:
    subset = df_barrios[df_barrios['prestigio'] == prestigio]
    area_total = subset['area'].sum()
    print(f"\n{prestigio:15} | Barrios: {len(subset):3} | Area Total: {area_total:,.0f} m²")

print("\n" + "="*90)
print(f"\nAbriendo mapa en navegador...\n")

# Abrir en navegador
import webbrowser
webbrowser.open(f'file:///{Path(output_path).resolve()}')

import time
time.sleep(2)
