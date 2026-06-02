"""
Mapa profesional con datos catastrales completos por barrio
"""

import json
import pandas as pd
from pathlib import Path

try:
    import folium
    from folium import plugins
except:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "folium", "--quiet"])
    import folium
    from folium import plugins

print("\n" + "="*90)
print("  MAPA PROFESIONAL - DATOS CATASTRALES COMPLETOS")
print("="*90 + "\n")

# Cargar GeoJSON enriquecido
print("[1/4] Cargando datos catastrales...")
with open('barrios_enriquecido.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

print(f"    > {len(geojson_data['features'])} barrios cargados\n")

# Colores por prestigio
colores_prestigio = {
    'PREMIUM': '#1a4d2e',
    'ALTO': '#2d7a4d',
    'MEDIO ALTO': '#7cb342',
    'MEDIO': '#fbc02d',
    'BAJO': '#e53935'
}

# Crear mapa
print("[2/4] Creando mapa interactivo...")
medellin_center = [6.2442, -75.5812]

mapa = folium.Map(
    location=medellin_center,
    zoom_start=12,
    tiles='CartoDB positron',
    prefer_canvas=True
)

# Agregar cada barrio como GeoJSON con popup personalizado
print("[3/4] Agregando barrios con información detallada...")

def get_color(feature):
    prestigio = feature['properties'].get('prestigio', 'MEDIO')
    return colores_prestigio.get(prestigio, '#999999')

def get_popup_html(feature):
    """Crea HTML profesional para el popup"""
    props = feature['properties']
    barrio = props.get('nombre', 'Desconocido')
    estrato = props.get('estrato', 'N/A')
    prestigio = props.get('prestigio', 'N/A')
    predios = props.get('cantidad_predios', 0)
    avaluo_total = props.get('avaluo_total', 0)
    avaluo_prom = props.get('avaluo_promedio', 0)
    area_const = props.get('area_construida_prom', 0)
    area_lote = props.get('area_lote_prom', 0)
    antiguedad = props.get('antiguedad_prom', 0)
    tipo_cons = props.get('tipo_construccion_dominante', 'N/A')
    densidad = props.get('densidad', 0)
    valor_m2 = props.get('valormetro', 0)
    color_hex = colores_prestigio.get(prestigio, '#999999')

    html = f"""
    <div style="font-family: 'Segoe UI', Arial; width: 380px; background: white; border-radius: 10px; overflow: hidden;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, {color_hex}, {color_hex}); color: white; padding: 15px;">
            <h2 style="margin: 0; font-size: 18px; font-weight: bold;">{barrio.upper()}</h2>
            <p style="margin: 8px 0 0 0; opacity: 0.95; font-size: 13px;">
                <b>Prestigio:</b> {prestigio} | <b>Estrato:</b> {estrato}/6
            </p>
        </div>

        <!-- Datos Principales -->
        <div style="background: #f8f9fa; padding: 12px; border-bottom: 1px solid #ddd;">
            <h4 style="margin: 0 0 10px 0; color: #1a3a52; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                INFORMACION CATASTRAL
            </h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <tr>
                    <td style="padding: 6px; font-weight: bold; color: #666;">Cantidad de Predios:</td>
                    <td style="padding: 6px; text-align: right; color: #1a3a52; font-weight: bold;">{predios:,}</td>
                </tr>
                <tr style="background: white;">
                    <td style="padding: 6px; font-weight: bold; color: #666;">Avaluo Total:</td>
                    <td style="padding: 6px; text-align: right; color: #e53935; font-weight: bold;">${avaluo_total:,.0f}</td>
                </tr>
                <tr>
                    <td style="padding: 6px; font-weight: bold; color: #666;">Avaluo Promedio:</td>
                    <td style="padding: 6px; text-align: right; color: #1a3a52; font-weight: bold;">${avaluo_prom:,.0f}</td>
                </tr>
            </table>
        </div>

        <!-- Características de Construcción -->
        <div style="background: white; padding: 12px; border-bottom: 1px solid #ddd;">
            <h4 style="margin: 0 0 10px 0; color: #1a3a52; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                CARACTERISTICAS DE CONSTRUCCION
            </h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <tr>
                    <td style="padding: 6px; font-weight: bold; color: #666;">Area Construida Prom:</td>
                    <td style="padding: 6px; text-align: right; color: #1a3a52;">{area_const:,.0f} m²</td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 6px; font-weight: bold; color: #666;">Area de Lote Prom:</td>
                    <td style="padding: 6px; text-align: right; color: #1a3a52;">{area_lote:,.0f} m²</td>
                </tr>
                <tr>
                    <td style="padding: 6px; font-weight: bold; color: #666;">Antiguedad Prom:</td>
                    <td style="padding: 6px; text-align: right; color: #1a3a52;">{antiguedad:,.1f} años</td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 6px; font-weight: bold; color: #666;">Tipo Construcción:</td>
                    <td style="padding: 6px; text-align: right; color: #1a3a52;"><b>{tipo_cons}</b></td>
                </tr>
            </table>
        </div>

        <!-- Indicadores de Valor -->
        <div style="background: #f8f9fa; padding: 12px; border-bottom: 1px solid #ddd;">
            <h4 style="margin: 0 0 10px 0; color: #1a3a52; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                INDICADORES DE VALOR
            </h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <tr>
                    <td style="padding: 6px; font-weight: bold; color: #666;">Valor por m²:</td>
                    <td style="padding: 6px; text-align: right; color: #2c5aa0; font-weight: bold;">${valor_m2:,.0f}</td>
                </tr>
                <tr style="background: white;">
                    <td style="padding: 6px; font-weight: bold; color: #666;">Densidad (predios/km²):</td>
                    <td style="padding: 6px; text-align: right; color: #2c5aa0; font-weight: bold;">{densidad:,.0f}</td>
                </tr>
            </table>
        </div>

        <!-- Footer -->
        <div style="background: #e8eef7; padding: 10px; text-align: center; font-size: 11px; color: #666;">
            <i>Click en el barrio para actualizar los datos | Datos de catastro 2026</i>
        </div>
    </div>
    """
    return html

# Agregar cada barrio como polígono con hover personalizado
for feature in geojson_data['features']:
    props = feature['properties']
    barrio_nombre = props.get('nombre', 'Desconocido')
    popup_html = get_popup_html(feature)

    # Agregar polígono con popup
    iframe = folium.IFrame(html=popup_html, width=380, height=520)
    folium.GeoJson(
        feature,
        style_function=lambda x, color=get_color(feature): {
            'fillColor': color,
            'color': 'white',
            'weight': 1,
            'opacity': 0.8,
            'fillOpacity': 0.6,
            'dashArray': '2, 2'
        },
        popup=folium.Popup(
            iframe,
            max_width=420
        ),
        tooltip=folium.Tooltip(
            f"<b>{barrio_nombre}</b><br>"
            f"Predios: {props.get('cantidad_predios', 0):,}<br>"
            f"Avaluo Prom: ${props.get('avaluo_promedio', 0):,.0f}",
            style="background-color: white; border: 2px solid #333; border-radius: 5px; "
                  "padding: 10px; font-weight: bold; font-size: 12px; color: #1a3a52;"
        )
    ).add_to(mapa)

# Leyenda profesional
print("[4/4] Agregando leyenda y finalizando...\n")

legend_html = '''
<div style="
    position: fixed;
    bottom: 50px;
    right: 50px;
    width: 320px;
    background-color: white;
    border: 3px solid #333;
    z-index: 9999;
    font-size: 13px;
    padding: 0;
    border-radius: 10px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    overflow: hidden;
">
    <div style="background: linear-gradient(135deg, #1a3a52, #2c5aa0); color: white; padding: 15px; text-align: center;">
        <h3 style="margin: 0; font-size: 14px; font-weight: bold;">CLASIFICACION POR PRESTIGIO</h3>
        <p style="margin: 5px 0 0 0; font-size: 11px; opacity: 0.9;">332 Barrios - Datos Catastrales</p>
    </div>

    <div style="padding: 15px;">
        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #1a4d2e; border-radius: 3px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b style="color: #1a3a52;">PREMIUM</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 5-6 | Avaluo $300M+</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #2d7a4d; border-radius: 3px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b style="color: #1a3a52;">ALTO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 4 | Avaluo $250M+</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #7cb342; border-radius: 3px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b style="color: #1a3a52;">MEDIO ALTO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 3 | Avaluo $200M+</span>
            </div>
        </div>

        <div style="margin-bottom: 12px; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #fbc02d; border-radius: 3px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b style="color: #1a3a52;">MEDIO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 2 | Avaluo $150M+</span>
            </div>
        </div>

        <div style="margin-bottom: 0; display: flex; align-items: center;">
            <div style="width: 24px; height: 24px; background: #e53935; border-radius: 3px; margin-right: 12px; border: 2px solid #333;"></div>
            <div>
                <b style="color: #1a3a52;">BAJO</b><br>
                <span style="font-size: 11px; color: #666;">Estrato 1 | Avaluo < $150M</span>
            </div>
        </div>
    </div>

    <div style="background: #f5f5f5; padding: 12px; border-top: 1px solid #ddd; font-size: 11px; color: #666; line-height: 1.5;">
        <p style="margin: 0 0 8px 0;"><b>Interactividad:</b></p>
        <p style="margin: 0 0 5px 0;">• Click = Ver información completa</p>
        <p style="margin: 0;">• Hover = Resumen rápido</p>
    </div>
</div>
'''

mapa.get_root().html.add_child(folium.Element(legend_html))

# Guardar mapa
output_path = 'outputs/visualizaciones/mapa_catastral_completo.html'
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
mapa.save(output_path)

print(f"[OK] Mapa guardado: {output_path}\n")

# Estadísticas finales
print("="*90)
print("RESUMEN FINAL")
print("="*90 + "\n")

# Calcular estadísticas globales
total_predios = sum([f['properties']['cantidad_predios'] for f in geojson_data['features']])
total_avaluo = sum([f['properties']['avaluo_total'] for f in geojson_data['features']])

print(f"Total de barrios mapeados: {len(geojson_data['features'])}")
print(f"Total de predios: {total_predios:,}")
print(f"Avaluo total catastral: ${total_avaluo:,.0f}")
print(f"Avaluo promedio por predio: ${total_avaluo/total_predios:,.0f}")

# Contar por prestigio
for prestigio in ['PREMIUM', 'ALTO', 'MEDIO ALTO', 'MEDIO', 'BAJO']:
    count = len([f for f in geojson_data['features'] if f['properties'].get('prestigio') == prestigio])
    print(f"\nBarrios {prestigio}: {count}")

print("\n" + "="*90)
print(f"\nAbriendo mapa en navegador...\n")

# Abrir en navegador
import webbrowser
import time
webbrowser.open(f'file:///{Path(output_path).resolve()}')
time.sleep(2)

print(f"URL: {Path(output_path).resolve()}\n")
