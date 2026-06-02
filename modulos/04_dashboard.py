"""
================================================================================
04_DASHBOARD.py - TABLERO DE SALUD DEL DATO
================================================================================

Módulo de visualización de calidad de datos:
- Genera dashboard interactivo con Plotly
- Métricas de confiabilidad por columna
- Análisis de imputaciones
- Comparativa antes/después
- Exporta a HTML para visualización

Salida: dashboard_salud_dato_TIMESTAMP.html + gráficos individuales

Autor: Proyecto Final - Data Quality Visualization
================================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DashboardSaludDato:
    """
    Generador de dashboard visual para monitoreo de calidad de datos.
    """

    def __init__(self, df_original=None, df_limpio=None, df_imputado=None, nombre='dataset'):
        """
        Args:
            df_original: DataFrame original (antes de ETL)
            df_limpio: DataFrame después de ETL
            df_imputado: DataFrame después de imputación
            nombre: Nombre del dataset
        """
        self.df_original = df_original
        self.df_limpio = df_limpio
        self.df_imputado = df_imputado
        self.nombre = nombre
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.figs = {}

    def crear_resumen_ejecutivo(self):
        """Crea cards de resumen ejecutivo."""
        logger.info("Generando resumen ejecutivo...")

        # Calcular métricas
        if self.df_imputado is not None:
            df = self.df_imputado
        elif self.df_limpio is not None:
            df = self.df_limpio
        else:
            df = self.df_original

        total_registros = len(df)
        total_columnas = len(df.columns)
        total_celdas = total_registros * total_columnas
        celdas_nulas = df.isnull().sum().sum()
        completitud = 100 * (1 - celdas_nulas / total_celdas) if total_celdas > 0 else 100
        duplicados = df.duplicated().sum()

        # Crear figura
        fig = go.Figure()

        # Cards de métricas principales
        cards = [
            dict(
                x=[0.15], y=[0.5], 
                text=[f"<b>REGISTROS</b><br>{total_registros:,}"],
                mode="text", showlegend=False
            ),
            dict(
                x=[0.4], y=[0.5],
                text=[f"<b>COMPLETITUD</b><br>{completitud:.1f}%"],
                mode="text", showlegend=False
            ),
            dict(
                x=[0.65], y=[0.5],
                text=[f"<b>DUPLICADOS</b><br>{duplicados:,}"],
                mode="text", showlegend=False
            ),
            dict(
                x=[0.9], y=[0.5],
                text=[f"<b>COLUMNAS</b><br>{total_columnas}"],
                mode="text", showlegend=False
            )
        ]

        for card in cards:
            fig.add_trace(go.Scatter(**card))

        fig.update_layout(
            title_text="<b>RESUMEN EJECUTIVO</b>",
            title_x=0.5,
            height=150,
            margin=dict(l=0, r=0, t=50, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='rgba(240,240,240,0.5)'
        )

        self.figs['resumen'] = fig
        return fig

    def crear_grafico_completitud(self):
        """Gráfico de completitud por columna."""
        logger.info("Generando gráfico de completitud...")

        if self.df_imputado is not None:
            df = self.df_imputado
        elif self.df_limpio is not None:
            df = self.df_limpio
        else:
            df = self.df_original

        completitud_por_col = 100 * (1 - df.isnull().sum() / len(df))
        completitud_por_col = completitud_por_col.sort_values(ascending=True)

        # Color por completitud
        colors = ['#d62728' if c < 80 else '#ff7f0e' if c < 95 else '#2ca02c' 
                  for c in completitud_por_col.values]

        fig = go.Figure(
            data=[go.Bar(
                y=completitud_por_col.index,
                x=completitud_por_col.values,
                orientation='h',
                marker=dict(color=colors),
                text=[f'{v:.1f}%' for v in completitud_por_col.values],
                textposition='outside'
            )]
        )

        fig.update_layout(
            title_text="<b>COMPLETITUD POR COLUMNA</b>",
            title_x=0.5,
            xaxis_title="Completitud (%)",
            yaxis_title="Columna",
            height=400,
            template="plotly_white",
            showlegend=False
        )

        self.figs['completitud'] = fig
        return fig

    def crear_grafico_comparativa_etapas(self):
        """Compara nulos antes/después ETL/imputación."""
        logger.info("Generando comparativa de etapas...")

        dfs = {}
        if self.df_original is not None:
            dfs['Original'] = self.df_original
        if self.df_limpio is not None:
            dfs['Limpio'] = self.df_limpio
        if self.df_imputado is not None:
            dfs['Imputado'] = self.df_imputado

        if len(dfs) < 2:
            logger.warning("Se necesitan al menos 2 etapas para comparar")
            return None

        data_comparativa = []

        for etapa, df in dfs.items():
            nulos_por_col = df.isnull().sum()
            data_comparativa.append({
                'Etapa': etapa,
                'Total Nulos': nulos_por_col.sum(),
                'Duplicados': df.duplicated().sum(),
                'Registros': len(df)
            })

        df_comp = pd.DataFrame(data_comparativa)

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'bar'}, {'type': 'bar'}]],
            subplot_titles=('Nulos Totales', 'Duplicados')
        )

        fig.add_trace(
            go.Bar(x=df_comp['Etapa'], y=df_comp['Total Nulos'], 
                   name='Nulos', marker_color='#d62728'),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(x=df_comp['Etapa'], y=df_comp['Duplicados'],
                   name='Duplicados', marker_color='#ff7f0e'),
            row=1, col=2
        )

        fig.update_layout(height=400, title_text="<b>COMPARATIVA ANTES/DESPUÉS</b>", 
                         title_x=0.5, showlegend=False)

        self.figs['comparativa'] = fig
        return fig

    def crear_grafico_imputaciones(self):
        """Muestra registro de imputaciones realizadas."""
        logger.info("Generando gráfico de imputaciones...")

        if self.df_imputado is None:
            logger.warning("No hay datos imputados para visualizar")
            # Crear figura vacía
            fig = go.Figure()
            fig.add_annotation(text="Sin datos de imputación disponibles")
            self.figs['imputaciones'] = fig
            return fig

        df = self.df_imputado

        # Detectar flags de imputación
        flags = [col for col in df.columns if col.endswith('_imputada') or col.endswith('_imputado')]
        
        if not flags:
            logger.warning("No se detectaron flags de imputación")
            fig = go.Figure()
            fig.add_annotation(text="Sin flags de imputación detectados")
            self.figs['imputaciones'] = fig
            return fig

        imputaciones = {}
        for flag in flags:
            if flag in df.columns:
                nombre_limpio = flag.replace('_imputada', '').replace('_imputado', '')
                imputaciones[nombre_limpio] = int(df[flag].sum())

        if not imputaciones:
            fig = go.Figure()
            fig.add_annotation(text="Todas las imputaciones son 0")
            self.figs['imputaciones'] = fig
            return fig

        fig = go.Figure(
            data=[go.Bar(
                x=list(imputaciones.keys()),
                y=list(imputaciones.values()),
                marker=dict(color='#1f77b4'),
                text=[f'{v:,.0f}' for v in imputaciones.values()],
                textposition='outside'
            )]
        )

        fig.update_layout(
            title_text="<b>REGISTROS IMPUTADOS POR VARIABLE</b>",
            title_x=0.5,
            xaxis_title="Variable",
            yaxis_title="Cantidad de registros",
            height=400,
            template="plotly_white"
        )

        self.figs['imputaciones'] = fig
        return fig

    def crear_grafico_score_calidad(self):
        """Muestra score de calidad global."""
        logger.info("Generando score de calidad...")

        if self.df_imputado is not None:
            df = self.df_imputado
        elif self.df_limpio is not None:
            df = self.df_limpio
        else:
            df = self.df_original

        # Calcular score
        n_celdas = len(df) * len(df.columns)
        n_nulos = df.isnull().sum().sum()
        completitud = 100 * (1 - n_nulos / n_celdas)

        n_duplicados = df.duplicated().sum()
        consistencia = 100 * (1 - n_duplicados / len(df)) if len(df) > 0 else 100

        score_global = (completitud * 0.6 + consistencia * 0.4)

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score_global,
            title={'text': "SCORE DE CALIDAD GLOBAL"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': 'darkblue'},
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(255, 0, 0, 0.3)'},
                    {'range': [60, 75], 'color': 'rgba(255, 165, 0, 0.3)'},
                    {'range': [75, 90], 'color': 'rgba(144, 238, 144, 0.3)'},
                    {'range': [90, 100], 'color': 'rgba(0, 128, 0, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            },
            number={'suffix': '%'}
        ))

        fig.update_layout(height=400, template="plotly_white")

        self.figs['score'] = fig
        return fig

    def crear_grafico_top_barrios(self):
        """Top barrios por cantidad de predios y avalúo total."""
        logger.info("Generando gráfico top barrios...")

        if self.df_imputado is not None:
            df = self.df_imputado
        elif self.df_limpio is not None:
            df = self.df_limpio
        else:
            df = self.df_original

        if 'barrio_nombre' not in df.columns:
            logger.warning("Columna 'barrio_nombre' no encontrada para gráfico de barrios")
            fig = go.Figure()
            fig.add_annotation(text="Sin datos de barrio para gráfico top barrios")
            self.figs['top_barrios'] = fig
            return fig

        barrio_stats = df.groupby('barrio_nombre').agg({
            'id_predio': 'count',
            'avaluo_total': 'sum'
        }).reset_index()
        barrio_stats.columns = ['barrio', 'cantidad_predios', 'avaluo_total']
        barrio_stats['avaluo_promedio'] = barrio_stats['avaluo_total'] / barrio_stats['cantidad_predios']
        barrio_stats = barrio_stats.sort_values('cantidad_predios', ascending=False).head(12)

        hover_texts = [
            f"<b>{row['barrio'].title()}</b><br>Predios: {row['cantidad_predios']:,}<br>Avalúo total: ${row['avaluo_total']:,.0f}<br>Avalúo promedio: ${row['avaluo_promedio']:,.0f}"
            for _, row in barrio_stats[::-1].iterrows()
        ]

        fig = go.Figure(
            data=[go.Bar(
                x=barrio_stats['cantidad_predios'][::-1],
                y=barrio_stats['barrio'][::-1],
                orientation='h',
                marker=dict(
                    color=barrio_stats['avaluo_promedio'][::-1],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title='Avalúo promedio')
                ),
                text=hover_texts,
                hoverinfo='text',
                hovertemplate='%{text}<extra></extra>'
            )]
        )

        fig.update_layout(
            title_text="<b>TOP 12 BARRIOS POR CANTIDAD DE PREDIOS</b>",
            title_x=0.5,
            xaxis_title="Cantidad de predios",
            yaxis_title="Barrio",
            height=500,
            template="plotly_white"
        )

        self.figs['top_barrios'] = fig
        return fig

    def crear_distribucion_nulos(self):
        """Heatmap de patrón de nulos."""
        logger.info("Generando mapa de nulos...")

        if self.df_imputado is not None:
            df = self.df_imputado
        elif self.df_limpio is not None:
            df = self.df_limpio
        else:
            df = self.df_original

        # Matriz de nulos (muestreo para visualización)
        n_mostrar = min(1000, len(df))
        df_muestra = df.iloc[:n_mostrar]
        matriz_nulos = df_muestra.isnull().astype(int)

        fig = go.Figure(
            data=go.Heatmap(
                z=matriz_nulos.T.values,
                y=matriz_nulos.columns,
                colorscale='RdYlGn_r',
                showscale=False
            )
        )

        fig.update_layout(
            title_text=f"<b>PATRÓN DE NULOS (primeros {n_mostrar} registros)</b>",
            title_x=0.5,
            xaxis_title="Número de registro",
            yaxis_title="Columna",
            height=300,
            template="plotly_white"
        )

        self.figs['nulos_heatmap'] = fig
        return fig

    def crear_mapa_geografico(self):
        """Crea mapa geografico con poligonos reales de barrios de Medellin."""
        logger.info("Generando mapa geografico con barrios reales...")

        import json

        # Verificar si existe el archivo barrios.geojson
        barrios_geojson_path = Path(__file__).parent.parent / 'barrios.geojson'

        if not barrios_geojson_path.exists():
            logger.warning("Archivo barrios.geojson no encontrado")
            fig = go.Figure()
            fig.add_annotation(text="Archivo barrios.geojson no encontrado")
            self.figs['mapa_geografico'] = fig
            return fig

        # Cargar GeoJSON
        try:
            with open(barrios_geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
        except Exception as e:
            logger.error(f"Error cargando GeoJSON: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error cargando barrios: {e}")
            self.figs['mapa_geografico'] = fig
            return fig

        # Mapeo de estratos por barrio
        estratos_barrios = {
            'EL POBLADO': 6, 'LAURELES': 5, 'ALTOS DEL POBLADO': 6, 'GUAYABAL': 5,
            'LA CANDELARIA': 4, 'BELEN': 3, 'BUENOS AIRES': 3, 'VILLA HERMOSA': 3,
            'ARANJUEZ': 2, 'CASTILLA': 2, 'DOCE DE OCTUBRE #1': 2, 'DOCE DE OCTUBRE #2': 2,
            'ROBLEDO': 2, 'MANRIQUE CENTRAL #1': 2, 'MANRIQUE CENTRAL #2': 2, 'POPULAR': 1,
            'SANTA CRUZ': 1, 'SAN JAVIER #1': 2, 'SAN JAVIER #2': 2, 'MORAVIA': 1,
            'VILLATINA': 1, 'SANTO DOMINGO SAVIO #1': 1, 'SANTO DOMINGO SAVIO #2': 1,
            'LA AMÉRICA': 2, 'PABLO VI': 2, 'MANRIQUE ORIENTAL': 2,
        }

        # Clasificacion por comunas
        zonas_comunas = {
            '01': 1, '02': 1, '03': 2, '04': 2, '05': 2, '06': 2, '07': 2,
            '08': 3, '09': 3, '10': 4, '11': 5, '12': 2, '13': 2, '14': 6, '15': 5, '16': 3,
        }

        # Enriquecer GeoJSON con estratos y prestigio
        for feature in geojson_data['features']:
            props = feature['properties']
            barrio_nombre = props.get('nombre', '').upper().strip()
            codigo = props.get('codigo', '')[:2]

            # Obtener estrato
            if barrio_nombre in estratos_barrios:
                estrato = estratos_barrios[barrio_nombre]
            elif codigo in zonas_comunas:
                estrato = zonas_comunas[codigo]
            else:
                estrato = 2

            # Clasificar prestigio
            if estrato >= 5:
                prestigio = 'PREMIUM'
            elif estrato == 4:
                prestigio = 'ALTO'
            elif estrato == 3:
                prestigio = 'MEDIO ALTO'
            elif estrato == 2:
                prestigio = 'MEDIO'
            else:
                prestigio = 'BAJO'

            feature['properties']['estrato'] = estrato
            feature['properties']['prestigio'] = prestigio

        # Crear mapa con folium
        try:
            import folium
            from folium import plugins

            medellin_center = [6.2442, -75.5812]
            mapa_folium = folium.Map(
                location=medellin_center,
                zoom_start=12,
                tiles='CartoDB positron',
                prefer_canvas=True
            )

            # Colores por prestigio
            colores = {
                'PREMIUM': '#1a4d2e',
                'ALTO': '#2d7a4d',
                'MEDIO ALTO': '#7cb342',
                'MEDIO': '#fbc02d',
                'BAJO': '#e53935'
            }

            def get_color(feature):
                return colores.get(feature['properties'].get('prestigio', 'MEDIO'), '#999999')

            def crear_popup(feature):
                """Crea popup con información formateada"""
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

                popup_html = f"""
                <div style="font-family: Arial, sans-serif; width: 380px; background: white;">
                    <h2 style="background-color: #fbc02d; color: white; margin: 0; padding: 12px; font-size: 16px; text-align: center;">
                        {barrio.upper()}
                    </h2>
                    <p style="margin: 8px 12px; font-size: 11px; color: #666;">
                        <b>Prestigio:</b> {prestigio} | <b>Estrato:</b> {estrato}/6
                    </p>

                    <h4 style="margin: 12px 12px 8px 12px; color: #1a3a52; font-size: 12px; border-bottom: 2px solid #fbc02d; padding-bottom: 4px;">
                        INFORMACION CATASTRAL
                    </h4>
                    <table style="width: 100%; font-size: 11px; margin: 0 12px 12px 12px;">
                        <tr style="background: #f5f5f5;">
                            <td style="padding: 6px;"><b>Cantidad de Predios:</b></td>
                            <td style="padding: 6px; text-align: right; color: #1a3a52; font-weight: bold;">{predios:,}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px;"><b>Avalúo Total:</b></td>
                            <td style="padding: 6px; text-align: right; color: #e53935; font-weight: bold;">${avaluo_total:,.0f}</td>
                        </tr>
                        <tr style="background: #f5f5f5;">
                            <td style="padding: 6px;"><b>Avalúo Promedio:</b></td>
                            <td style="padding: 6px; text-align: right; color: #1a3a52; font-weight: bold;">${avaluo_prom:,.0f}</td>
                        </tr>
                    </table>

                    <h4 style="margin: 12px 12px 8px 12px; color: #1a3a52; font-size: 12px; border-bottom: 2px solid #fbc02d; padding-bottom: 4px;">
                        CARACTERISTICAS DE CONSTRUCCION
                    </h4>
                    <table style="width: 100%; font-size: 11px; margin: 0 12px 12px 12px;">
                        <tr style="background: #f5f5f5;">
                            <td style="padding: 6px;"><b>Área Construida Prom:</b></td>
                            <td style="padding: 6px; text-align: right;">{area_const:,.0f} m²</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px;"><b>Área de Lote Prom:</b></td>
                            <td style="padding: 6px; text-align: right;">{area_lote:,.0f} m²</td>
                        </tr>
                        <tr style="background: #f5f5f5;">
                            <td style="padding: 6px;"><b>Antigüedad Prom:</b></td>
                            <td style="padding: 6px; text-align: right;">{antiguedad:,.1f} años</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px;"><b>Tipo Construcción:</b></td>
                            <td style="padding: 6px; text-align: right;"><b>{tipo_cons}</b></td>
                        </tr>
                    </table>

                    <h4 style="margin: 12px 12px 8px 12px; color: #1a3a52; font-size: 12px; border-bottom: 2px solid #fbc02d; padding-bottom: 4px;">
                        INDICADORES DE VALOR
                    </h4>
                    <table style="width: 100%; font-size: 11px; margin: 0 12px 12px 12px;">
                        <tr style="background: #f5f5f5;">
                            <td style="padding: 6px;"><b>Valor por m²:</b></td>
                            <td style="padding: 6px; text-align: right; color: #2c5aa0; font-weight: bold;">${valor_m2:,.0f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px;"><b>Densidad (predios/km²):</b></td>
                            <td style="padding: 6px; text-align: right; color: #2c5aa0; font-weight: bold;">{densidad:,.0f}</td>
                        </tr>
                    </table>

                    <div style="background: #e8eef7; padding: 8px 12px; font-size: 10px; color: #666; text-align: center; border-top: 1px solid #ddd;">
                        Datos de catastro 2026
                    </div>
                </div>
                """
                return folium.Popup(popup_html, max_width=400)

            # Agregar cada barrio como feature individual
            for feature in geojson_data['features']:
                folium.GeoJson(
                    feature,
                    style_function=lambda x, color=get_color(feature): {
                        'fillColor': color,
                        'color': 'white',
                        'weight': 1.5,
                        'opacity': 0.8,
                        'fillOpacity': 0.6
                    },
                    popup=crear_popup(feature),
                    tooltip=folium.Tooltip(
                        f"{feature['properties'].get('nombre', 'N/A')}: {feature['properties'].get('cantidad_predios', 0):,} predios",
                        style="background-color: white; border: 2px solid #333; border-radius: 5px; "
                              "padding: 8px; font-weight: bold; font-size: 11px; color: #1a3a52;"
                    )
                ).add_to(mapa_folium)

            # Leyenda mejorada
            legend_html = '''
            <div style="position: fixed; bottom: 50px; right: 50px; width: 300px; background: white;
                        border: 3px solid #333; z-index: 999; padding: 15px; border-radius: 10px;
                        box-shadow: 0 8px 16px rgba(0,0,0,0.3); font-size: 12px;">
                <h4 style="margin: 0 0 12px 0; color: white; background: linear-gradient(135deg, #1a3a52, #2c5aa0);
                          padding: 10px; border-radius: 5px; text-align: center; font-size: 13px;">
                    CLASIFICACIÓN DE PRESTIGIO
                </h4>
                <div style="margin-bottom: 10px;"><div style="width: 18px; height: 18px; background: #1a4d2e;
                    display: inline-block; margin-right: 10px; border-radius: 2px;"></div><b>PREMIUM</b> Est. 5-6</div>
                <div style="margin-bottom: 10px;"><div style="width: 18px; height: 18px; background: #2d7a4d;
                    display: inline-block; margin-right: 10px; border-radius: 2px;"></div><b>ALTO</b> Est. 4</div>
                <div style="margin-bottom: 10px;"><div style="width: 18px; height: 18px; background: #7cb342;
                    display: inline-block; margin-right: 10px; border-radius: 2px;"></div><b>MEDIO ALTO</b> Est. 3</div>
                <div style="margin-bottom: 10px;"><div style="width: 18px; height: 18px; background: #fbc02d;
                    display: inline-block; margin-right: 10px; border-radius: 2px;"></div><b>MEDIO</b> Est. 2</div>
                <div><div style="width: 18px; height: 18px; background: #e53935;
                    display: inline-block; margin-right: 10px; border-radius: 2px;"></div><b>BAJO</b> Est. 1</div>
                <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                <div style="font-size: 11px; color: #666;">
                    <p style="margin: 5px 0;"><i>Click = Ver detalle completo</i></p>
                    <p style="margin: 5px 0;"><i>Hover = Información rápida</i></p>
                </div>
            </div>
            '''
            mapa_folium.get_root().html.add_child(folium.Element(legend_html))

            # Guardar mapa temporalmente
            mapa_temp_path = Path(self.timestamp_dir) / f'mapa_temporal_{self.timestamp}.html'
            mapa_folium.save(str(mapa_temp_path))

            # Leer el HTML del mapa
            with open(mapa_temp_path, 'r', encoding='utf-8') as f:
                mapa_html = f.read()

            # Crear figura con el mapa
            fig = go.Figure()
            fig.add_annotation(
                text=f"<iframe srcdoc=\"{mapa_html.replace(chr(34), '&quot;')}\" style=\"width:100%; height:100%; border:none;\"></iframe>",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor="center", yanchor="middle",
                showarrow=False,
                xshift=0, yshift=0
            )

            fig.update_layout(
                title=dict(
                    text="<b>🗺️ MAPA DE BARRIOS - ÁREA METROPOLITANA DE MEDELLÍN</b><br><sub>332 Barrios | Datos Catastrales Completos</sub>",
                    x=0.5, xanchor='center',
                    font=dict(size=18, color='#1a3a52')
                ),
                height=800,
                margin=dict(l=0, r=0, t=80, b=20),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='white'
            )

            self.figs['mapa_geografico'] = fig
            return fig

        except ImportError:
            logger.info("Instalando folium...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "folium", "--quiet"])
            return self.crear_mapa_geografico()

        except Exception as e:
            logger.error(f"Error creando mapa: {e}")
            import traceback
            traceback.print_exc()
            fig = go.Figure()
            fig.add_annotation(text=f"Error creando mapa: {str(e)}")
            self.figs['mapa_geografico'] = fig
            return fig

    def crear_dashboard_html(self, ruta_output='dashboard.html'):
        """
        Genera dashboard HTML interactivo con todos los gráficos.
        """
        logger.info(f"Compilando dashboard HTML...")

        Path(ruta_output).parent.mkdir(parents=True, exist_ok=True)

        # Crear todos los gráficos
        self.crear_resumen_ejecutivo()
        self.crear_grafico_completitud()
        self.crear_grafico_comparativa_etapas()
        # No crear el mapa geográfico plotly; usar el mapa catastral completo generado externamente
        self.crear_grafico_imputaciones()
        self.crear_grafico_score_calidad()
        self.crear_grafico_top_barrios()
        self.crear_distribucion_nulos()

        # Compilar en HTML usando to_html con divs incluidos
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Salud del Dato</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 24px;
            background: linear-gradient(135deg, #eef3f8 0%, #d8e3ef 100%);
            color: #2a3d55;
        }}
        .header {{
            text-align: center;
            color: #1b2f47;
            margin-bottom: 28px;
            background: rgba(255,255,255,0.95);
            padding: 28px 24px;
            border-radius: 18px;
            box-shadow: 0 12px 34px rgba(34, 60, 80, 0.12);
            border: 1px solid rgba(200, 210, 220, 0.35);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.6em;
            letter-spacing: 0.01em;
            line-height: 1.1;
        }}
        .header p {{
            margin: 14px auto 0;
            color: #4b6078;
            font-size: 1rem;
            max-width: 860px;
            line-height: 1.6;
        }}
        .container {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 24px;
            max-width: 1680px;
            margin: 0 auto;
        }}
        .card {{
            background: rgba(255,255,255,0.96);
            border-radius: 20px;
            box-shadow: 0 12px 30px rgba(34, 60, 80, 0.08);
            padding: 22px;
            min-height: 500px;
            border: 1px solid rgba(200, 210, 220, 0.35);
            display: flex;
            flex-direction: column;
        }}
        .card-full {{
            grid-column: 1 / -1;
        }}
        .card h2 {{
            margin-top: 0;
            margin-bottom: 16px;
            font-size: 1.45rem;
            color: #1b2f47;
            text-align: center;
            letter-spacing: 0.01em;
        }}
        .chart {{
            width: 100%;
            height: 100%;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #5e6f88;
            font-size: 0.95em;
        }}
        @media (max-width: 1200px) {{
            .container {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 DASHBOARD DE SALUD DEL DATO - MEDELLÍN</h1>
        <p>Visión estratégica de calidad catastral para predios y barrios, con métricas de completitud, imputación y evaluación de avalúos.</p>
        <p>Dataset: {self.nombre} | Generado: {self.timestamp}</p>
    </div>
    
    <div class="container">
"""

        # Agregar cada gráfico usando to_html directamente
        for nombre, fig in self.figs.items():
            # to_html retorna el HTML completo incluyendo script y div
            # Usar include_plotlyjs='require' para no repetir la librería
            html_graph = fig.to_html(
                include_plotlyjs=False,  # Ya está en el header
                full_html=False,
                div_id=nombre,
                config={'responsive': True, 'displayModeBar': True}
            )
            
            full_width = nombre in ['resumen', 'comparativa', 'nulos_heatmap', 'top_barrios', 'mapa_geografico']
            card_class = 'card card-full' if full_width else 'card'
            
            html_content += f'        <div class="{card_class}">\n'
            html_content += f'            {html_graph}\n'
            html_content += '        </div>\n'

        # Agregar el mapa catastral completo en lugar del mapa geográfico Plotly
        mapa_catastral_path = Path(ruta_output).parent / 'mapa_catastral_completo.html'
        if mapa_catastral_path.exists():
            html_content += '        <div class="card card-full">\n'
            html_content += '            <h2 style="margin-top:0;">MAPA CATASTRAL COMPLETO</h2>\n'
            html_content += f'            <iframe src="{mapa_catastral_path.name}" width="100%" height="780" style="border:1px solid #ddd; border-radius: 10px; overflow:hidden;" loading="lazy"></iframe>\n'
            html_content += '        </div>\n'
        else:
            html_content += '        <div class="card card-full">\n'
            html_content += '            <h2 style="margin-top:0;">MAPA CATASTRAL COMPLETO</h2>\n'
            html_content += '            <div style="padding:24px; color:#525f7f; background:#fbfcfd; border:1px solid #dfe4ed; border-radius: 12px;">\n'
            html_content += '                <p style="margin:0; font-size:1rem;">El archivo <strong>mapa_catastral_completo.html</strong> no se encontró.</p>\n'
            html_content += '                <p style="margin:10px 0 0 0; font-size:0.95rem;">Ejecuta <code>python mapa_catastral_completo.py</code> en la raíz del proyecto para generarlo.</p>\n'
            html_content += '            </div>\n'
            html_content += '        </div>\n'

        html_content += """
    </div>
    
    <div class="footer">
        <p>Sistema de Monitoreo de Calidad de Datos - Proyecto Final MLOps</p>
    </div>
</body>
</html>
"""

        with open(ruta_output, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"✓ Dashboard guardado: {ruta_output}")
        return ruta_output

    def generar_reporte_json(self, ruta='reporte_dashboard.json'):
        """Genera reporte de métricas en JSON."""
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)

        if self.df_imputado is not None:
            df = self.df_imputado
        elif self.df_limpio is not None:
            df = self.df_limpio
        else:
            df = self.df_original

        reporte = {
            'timestamp': self.timestamp,
            'dataset': self.nombre,
            'registros': int(len(df)),
            'columnas': int(len(df.columns)),
            'nulos_totales': int(df.isnull().sum().sum()),
            'duplicados': int(df.duplicated().sum()),
            'completitud': float(round(100 * (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))), 2)),
            'columnas_completitud': {
                col: float(round(100 * (1 - df[col].isnull().sum() / len(df)), 2))
                for col in df.columns
            }
        }

        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Reporte JSON guardado: {ruta}")
        return ruta


# ================================================================================
# Ejemplo de uso
# ================================================================================

if __name__ == "__main__":
    from sqlalchemy import create_engine

    DB_CONFIG = {
        'user': 'catastro_jmm9_user',
        'password': 'W4q6uMkHT6BTaRDUF58XYY7AV2CUatBW',
        'host': 'pg-d7t01mq8qa3s73f28r4g-a.oregon-postgres.render.com',
        'port': '5432',
        'database': 'catastro_jmm9'
    }

    try:
        # Cargar datos
        url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/" \
              f"{DB_CONFIG['database']}"
        engine = create_engine(url)

        query = """
        SELECT 
            nm_mtcla_prdio AS id_predio,
            estrato_pre AS estrato,
            ds_barrio AS barrio_nombre,
            ava_total_ava AS avaluo_total,
            area_con AS area_construida,
            nm_ptje AS puntaje,
            ds_tipo_construccion AS tipo_construccion
        FROM catastro.insertar_predios_construccion
        LIMIT 50000
        """

        df = pd.read_sql_query(query, con=engine)

        # Crear dashboard
        dashboard = DashboardSaludDato(
            df_original=df,
            nombre='EAGIC_Catastro'
        )

        Path('outputs').mkdir(exist_ok=True)
        ruta_html = dashboard.crear_dashboard_html(
            f'outputs/dashboard_salud_dato_{dashboard.timestamp}.html'
        )
        ruta_json = dashboard.generar_reporte_json(
            f'outputs/reporte_dashboard_{dashboard.timestamp}.json'
        )

        print(f"\n✓ Dashboard generado: {ruta_html}")
        print(f"✓ Reporte JSON: {ruta_json}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
