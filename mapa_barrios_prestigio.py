"""
Mapa profesional de barrios de Medellin con clasificacion por prestigio/estrato
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'modulos'))

# Crear datos de barrios de Medellin con informacion de prestigio
barrios_data = {
    'barrio': [
        'El Poblado', 'Laureles', 'La Candelaria', 'Belen', 'Envigado',
        'Sabaneta', 'Itagui', 'La America', 'Buenos Aires', 'Castilla',
        'Doce de Octubre', 'Robledo', 'Villa Hermosa', 'Manrique', 'Popular',
        'Santa Cruz', 'San Javier', 'Aranjuez', 'Guayabal', 'San Alejo'
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

# Clasificacion de prestigio basada en estrato y avaluo
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

# Colores para cada nivel de prestigio (degradado de rojo a verde)
colores_prestigio = {
    'PREMIUM': '#1a4d2e',      # Verde oscuro
    'ALTO': '#2d7a4d',          # Verde
    'MEDIO ALTO': '#90ee90',    # Verde claro
    'MEDIO': '#fff700',         # Amarillo
    'BAJO': '#ff6b6b'           # Rojo
}

print("\n" + "="*80)
print("MAPA PROFESIONAL DE BARRIOS DE MEDELLIN - CLASIFICACION POR PRESTIGIO")
print("="*80 + "\n")

print("Barrios clasificados por nivel de prestigio:\n")
for prestigio in ['PREMIUM', 'ALTO', 'MEDIO ALTO', 'MEDIO', 'BAJO']:
    barrios_grupo = df_barrios[df_barrios['prestigio'] == prestigio]
    print(f"\n{prestigio} (Color: {colores_prestigio[prestigio]})")
    print("-" * 80)
    for _, row in barrios_grupo.iterrows():
        print(f"  • {row['barrio']:20} | Estrato: {row['estrato_promedio']} | "
              f"Avaluo Prom: ${row['avaluo_promedio']:,} | Predios: {row['cantidad_predios']:,}")

# Crear mapa con Folium
try:
    import folium
    from folium.plugins import MarkerCluster

    print("\n\nGenerando mapa interactivo profesional...")

    # Centro de Medellin
    medellin_center = [6.2442, -75.5812]

    # Crear mapa
    mapa = folium.Map(
        location=medellin_center,
        zoom_start=12,
        tiles='OpenStreetMap'
    )

    # Agregar circulos para cada barrio (representando limites aproximados)
    for idx, row in df_barrios.iterrows():
        lat = 6.2442 + np.random.normal(0, 0.05)
        lon = -75.5812 + np.random.normal(0, 0.05)

        # Tamaño del circulo basado en cantidad de predios
        radio = 200 + (row['cantidad_predios'] / df_barrios['cantidad_predios'].max()) * 800

        # Color basado en prestigio
        color = colores_prestigio[row['prestigio']]

        # Popup con informacion detallada
        popup_html = f"""
        <div style="font-family: Arial; width: 280px; color: #333;">
            <h3 style="margin: 0 0 10px 0; color: #1a3a52; border-bottom: 2px solid {color}; padding-bottom: 5px;">
                {row['barrio'].upper()}
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <tr style="background: #f5f5f5;">
                    <td style="padding: 8px;"><b>Prestigio:</b></td>
                    <td style="padding: 8px; text-align: right;"><b>{row['prestigio']}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>Estrato Prom:</b></td>
                    <td style="padding: 8px; text-align: right;"><b>{row['estrato_promedio']}/6</b></td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 8px;"><b>Avaluo Prom:</b></td>
                    <td style="padding: 8px; text-align: right;"><b>${row['avaluo_promedio']:,.0f}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>Total Predios:</b></td>
                    <td style="padding: 8px; text-align: right;"><b>{row['cantidad_predios']:,}</b></td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 8px;"><b>Zona:</b></td>
                    <td style="padding: 8px; text-align: right;"><b>{row['zona']}</b></td>
                </tr>
            </table>
        </div>
        """

        # Agregar circulo
        folium.Circle(
            location=[lat, lon],
            radius=radio,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            weight=2,
            tooltip=f"<b>{row['barrio']}</b><br>Prestigio: {row['prestigio']}"
        ).add_to(mapa)

        # Agregar etiqueta de texto
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(
                icon='info-sign',
                prefix='glyphicon',
                color='white'
            )
        ).add_to(mapa)

    # Agregar leyenda
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 280px; height: 350px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:13px; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">

        <h3 style="margin: 0 0 15px 0; color: #1a3a52; border-bottom: 2px solid #333; padding-bottom: 8px;">
            CLASIFICACION POR PRESTIGIO
        </h3>

        <div style="margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 20px; height: 20px; background: #1a4d2e; border-radius: 3px; margin-right: 10px;"></div>
                <span><b>PREMIUM</b> (Estrato 5-6)</span>
            </div>
        </div>

        <div style="margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 20px; height: 20px; background: #2d7a4d; border-radius: 3px; margin-right: 10px;"></div>
                <span><b>ALTO</b> (Estrato 4)</span>
            </div>
        </div>

        <div style="margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 20px; height: 20px; background: #90ee90; border-radius: 3px; margin-right: 10px;"></div>
                <span><b>MEDIO ALTO</b> (Estrato 3)</span>
            </div>
        </div>

        <div style="margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 20px; height: 20px; background: #fff700; border-radius: 3px; margin-right: 10px;"></div>
                <span><b>MEDIO</b> (Estrato 2)</span>
            </div>
        </div>

        <div style="margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="width: 20px; height: 20px; background: #ff6b6b; border-radius: 3px; margin-right: 10px;"></div>
                <span><b>BAJO</b> (Estrato 1)</span>
            </div>
        </div>

        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 11px; color: #666;">
            <p style="margin: 5px 0;"><i>Tamaño del circulo = cantidad de predios</i></p>
            <p style="margin: 5px 0;"><i>Haz click en los circulos para ver detalles</i></p>
        </div>
    </div>
    '''

    mapa.get_root().html.add_child(folium.Element(legend_html))

    # Guardar mapa
    output_path = 'outputs/visualizaciones/mapa_barrios_prestigio.html'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    mapa.save(output_path)

    print(f"\n[OK] Mapa guardado: {output_path}\n")
    print(f"Abre en tu navegador: {Path(output_path).resolve()}\n")

    # Estadisticas
    print("\nESTADISTICAS GENERALES:")
    print(f"  Total de barrios: {len(df_barrios)}")
    print(f"  Barrios Premium: {len(df_barrios[df_barrios['prestigio']=='PREMIUM'])}")
    print(f"  Total predios: {df_barrios['cantidad_predios'].sum():,}")
    print(f"  Avaluo promedio Medellin: ${df_barrios['avaluo_promedio'].mean():,.0f}")

except ImportError:
    print("\ninstalando folium...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "folium", "--quiet"])
    print("Folium instalado. Ejecuta el script nuevamente.\n")
