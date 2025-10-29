import streamlit as st
import pandas as pd

st.set_page_config(page_title="Seguimiento de Publicadores", layout="wide")
st.title("📊 Seguimiento de Publicadores por Monitor")

# Cargar datos
df = pd.read_excel('dashboard_lpi.xlsx')

# Asegurar que date sea datetime
df['date'] = pd.to_datetime(df['date'])

# Información general
st.info(f"📅 Total de fechas: {df['date'].nunique()} | Total de monitores: {df['Monitor'].nunique()} | Total de publicadores: {df['publicador'].nunique()} | Total de registros: {len(df)}")

# Obtener lista única de monitores ordenados
monitores = sorted(df['Monitor'].unique())

# Crear pestañas para cada monitor
tabs = st.tabs(monitores)

# Iterar sobre cada pestaña (monitor)
for i, monitor in enumerate(monitores):
    with tabs[i]:
        # Filtrar datos del monitor
        df_monitor = df[df['Monitor'] == monitor].copy()
        
        st.subheader(f"👤 Monitor: {monitor}")
        st.caption(f"Supervisa a {df_monitor['publicador'].nunique()} publicadores")
        
        st.markdown("---")
        
        # TABLA PRINCIPAL: Registros por Publicador y Fecha
        st.markdown("### 📅 Registros Diarios por Publicador")
        
        # Crear tabla pivote: Publicadores (filas) x Fechas (columnas)
        tabla_registros = df_monitor.groupby(['publicador', 'date']).size().reset_index(name='registros')
        
        # Pivotar para tener fechas como columnas
        tabla_pivot = tabla_registros.pivot(
            index='publicador',
            columns='date',
            values='registros'
        ).fillna(0).astype(int)
        
        # Agregar columna de total
        tabla_pivot['TOTAL'] = tabla_pivot.sum(axis=1)
        
        # Ordenar por total descendente
        tabla_pivot = tabla_pivot.sort_values('TOTAL', ascending=False)
        
        # Formatear nombres de columnas (fechas)
        tabla_pivot.columns = [col.strftime('%d/%m') if isinstance(col, pd.Timestamp) else col for col in tabla_pivot.columns]
        
        # Resetear índice para mostrar publicador como columna
        tabla_pivot_reset = tabla_pivot.reset_index()
        tabla_pivot_reset.columns.name = None
        
        # Mostrar tabla con formato mejorado
        st.dataframe(
            tabla_pivot_reset,
            use_container_width=True,
            hide_index=True,
            column_config={
                "publicador": st.column_config.TextColumn("Publicador", width="large"),
                "TOTAL": st.column_config.NumberColumn("TOTAL", width="small", help="Total de registros del publicador")
            },
            height=400
        )
        
        st.markdown("---")
        
        # RESUMEN DE DESEMPEÑO POR PUBLICADOR
        st.markdown("### 📈 Desempeño de Publicadores")
        
        resumen_publicador = df_monitor.groupby('publicador').agg(
            total_registros=('key', 'count'),
            dias_activos=('date', 'nunique')
        ).reset_index()
        
        resumen_publicador['promedio_por_dia'] = (resumen_publicador['total_registros'] / resumen_publicador['dias_activos']).round(1)
        
        resumen_publicador.columns = [
            'Publicador', 'Total Registros', 'Días Activos', 'Promedio por Día'
        ]
        
        # Ordenar por total de registros
        resumen_publicador = resumen_publicador.sort_values('Total Registros', ascending=False)
        
        st.dataframe(
            resumen_publicador,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Publicador": st.column_config.TextColumn("Publicador", width="medium"),
                "Total Registros": st.column_config.NumberColumn("Total Registros", help="Total de registros realizados"),
                "Días Activos": st.column_config.NumberColumn("Días Activos", help="Días en los que realizó registros"),
                "Promedio por Día": st.column_config.NumberColumn("Prom/Día", format="%.1f", help="Promedio de registros por día activo"),
                "Distritos": st.column_config.NumberColumn("Distritos", help="Distritos únicos visitados"),
                "Provincias": st.column_config.NumberColumn("Provincias", help="Provincias únicas visitadas")
            }
        )
        
        st.markdown("---")
        
        # GRÁFICOS DE DESEMPEÑO
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Total de Registros por Publicador")
            st.bar_chart(resumen_publicador.set_index('Publicador')['Total Registros'])
        
        with col2:
            st.markdown("### 📍 Cobertura Geográfica")
            st.bar_chart(resumen_publicador.set_index('Publicador')['Distritos'])
        
        st.markdown("---")
        
        # IDENTIFICAR PUBLICADORES CON BAJO DESEMPEÑO
        st.markdown("### ⚠️ Alertas de Seguimiento")
        
        dias_totales = df_monitor['date'].nunique()
        umbral_dias = dias_totales * 0.5  # Menos del 50% de días activos
        umbral_registros = resumen_publicador['Total Registros'].median()  # Menos de la mediana
        
        publicadores_alerta = resumen_publicador[
            (resumen_publicador['Días Activos'] < umbral_dias) | 
            (resumen_publicador['Total Registros'] < umbral_registros)
        ]
        
        if len(publicadores_alerta) > 0:
            st.warning(f"⚠️ {len(publicadores_alerta)} publicador(es) requieren seguimiento:")
            
            for idx, row in publicadores_alerta.iterrows():
                motivos = []
                if row['Días Activos'] < umbral_dias:
                    motivos.append(f"solo {row['Días Activos']} de {dias_totales} días activos")
                if row['Total Registros'] < umbral_registros:
                    motivos.append(f"solo {row['Total Registros']} registros (mediana: {umbral_registros:.0f})")
                
                st.markdown(f"- **{row['Publicador']}**: {', '.join(motivos)}")
        else:
            st.success("✅ Todos los publicadores están cumpliendo con las metas esperadas")

# Agregar sección de comparación entre monitores
st.markdown("---")
st.subheader("🌍 Comparación entre Monitores")

resumen_monitores = df.groupby('Monitor').agg(
    total_registros=('key', 'count'),
    publicadores=('publicador', 'nunique'),
    dias_activos=('date', 'nunique'),
    duracion_total=('duration', 'sum'),
    distritos=('DISTRITO', 'nunique'),
    provincias=('PROVINCIA', 'nunique')
).reset_index()

resumen_monitores['registros_por_publicador'] = (resumen_monitores['total_registros'] / resumen_monitores['publicadores']).round(1)
resumen_monitores['duracion_total'] = resumen_monitores['duracion_total'].round(2)

resumen_monitores.columns = [
    'Monitor', 'Total Registros', 'Publicadores', 
    'Días Activos', 'Duración Total (min)', 'Distritos', 
    'Provincias', 'Registros/Publicador'
]

st.dataframe(
    resumen_monitores.sort_values('Total Registros', ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Registros/Publicador": st.column_config.NumberColumn(
            "Reg/Pub", 
            format="%.1f",
            help="Promedio de registros por publicador"
        )
    }
)
