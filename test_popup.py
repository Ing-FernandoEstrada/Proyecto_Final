"""Test para depurar popup de Folium"""
import folium
import json
from pathlib import Path

# Cargar barrios
barrios_path = Path(__file__).parent / 'barrios.geojson'
with open(barrios_path, 'r', encoding='utf-8') as f:
    geojson = json.load(f)

# Tomar solo el primer barrio para prueba
feature = geojson['features'][0]
props = feature['properties']

print(f"Probando con barrio: {props.get('nombre')}")

# Crear mapa
mapa = folium.Map(location=[6.2442, -75.5812], zoom_start=12)

# Intento 1: HTML simple sin IFrame
popup_simple = folium.Popup("Esto es un popup simple de prueba", max_width=300)

# Intento 2: HTML con estilos básicos
html_basic = "<h3>Título del Barrio</h3><p>Contenido simple</p>"
popup_basic = folium.Popup(html_basic, max_width=300)

# Intento 3: HTML con estilos inline
html_styled = """
<div style="font-family: Arial; width: 300px;">
    <h2 style="color: #fbc02d; margin: 0;">PAJARITO</h2>
    <p style="color: #666;">Prestigio: MEDIO | Estrato: 2/6</p>
    <table style="width: 100%; font-size: 12px;">
        <tr><td>Predios:</td><td align="right"><b>2,090</b></td></tr>
        <tr><td>Avalúo:</td><td align="right"><b>$282B</b></td></tr>
    </table>
</div>
"""
popup_styled = folium.Popup(html_styled, max_width=350)

# Intento 4: Usando IFrame
iframe = folium.IFrame(html=html_styled, width=350, height=300)
popup_iframe = folium.Popup(iframe, max_width=350)

# Agregar popups de prueba
coords = feature['geometry']['coordinates'][0][0]
folium.Marker(
    location=[coords[1], coords[0]],
    popup=popup_styled,
    tooltip="Intento con estilos",
    icon=folium.Icon(color='blue', icon='info')
).add_to(mapa)

# Guardar
output = 'test_popup_map.html'
mapa.save(output)
print(f"[OK] Mapa guardado: {output}")

# Abrir
import webbrowser
webbrowser.open(f'file:///{Path(output).resolve()}')
print("Abierto en navegador - prueba hacer clic en el marcador")
