import streamlit as st
import pandas as pd

st.set_page_config(page_title="Registros por Monitor", layout="wide")
st.title("📊 Registros por Monitor y Publicador")

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
        
        # Métricas generales del monitor
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Registros", len(df_monitor))
        with col2:
            st.metric("Publicadores Únicos", df_monitor['publicador'].nunique())
        with col3:
            st.metric("Días Activos", df_monitor['date'].nunique())
        with col4:
            st.metric("Duración Total", f"{df_monitor['duration'].sum():.1f} min")
        
        st.markdown("---")
        
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
        tabla_pivot.columns = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in tabla_pivot.columns]
        
        # Resetear índice para mostrar publicador como columna
        tabla_pivot_reset = tabla_pivot.reset_index()
        tabla_pivot_reset.columns.name = None
        
        st.markdown("### 📅 Registros por Publicador y Fecha")
        
        # Mostrar tabla con formato mejorado
        st.dataframe(
            tabla_pivot_reset,
            use_container_width=True,
            hide_index=True,
            column_config={
                "publicador": st.column_config.TextColumn("Publicador", width="medium"),
                "TOTAL": st.column_config.NumberColumn("TOTAL", width="small", help="Total de registros del publicador")
            }
        )
        
        st.markdown("---")
        
        # Resumen adicional por publicador
        st.markdown("### 📈 Resumen por Publicador")
        
        resumen_publicador = df_monitor.groupby('publicador').agg(
            total_registros=('key', 'count'),
            dias_activos=('date', 'nunique'),
            duracion_promedio=('duration', 'mean'),
            duracion_total=('duration', 'sum'),
            distritos_unicos=('DISTRITO', 'nunique')
        ).reset_index()
        
        resumen_publicador['promedio_por_dia'] = (resumen_publicador['total_registros'] / resumen_publicador['dias_activos']).round(1)
        resumen_publicador['duracion_promedio'] = resumen_publicador['duracion_promedio'].round(2)
        resumen_publicador['duracion_total'] = resumen_publicador['duracion_total'].round(2)
        
        resumen_publicador.columns = [
            'Publicador', 'Total Registros', 'Días Activos', 
            'Duración Promedio (min)', 'Duración Total (min)', 
            'Distritos Únicos', 'Promedio por Día'
        ]
        
        st.dataframe(
            resumen_publicador.sort_values('Total Registros', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de barras por publicador
        st.markdown("### 📊 Distribución de Registros")
        st.bar_chart(resumen_publicador.set_index('Publicador')['Total Registros'])

# Agregar sección de resumen general al final
st.markdown("---")
st.subheader("🌍 Resumen General por Monitor")

resumen_general = df.groupby('Monitor').agg(
    total_registros=('key', 'count'),
    publicadores_unicos=('publicador', 'nunique'),
    dias_activos=('date', 'nunique'),
    duracion_total=('duration', 'sum'),
    distritos_unicos=('DISTRITO', 'nunique')
).reset_index()

resumen_general['promedio_por_dia'] = (resumen_general['total_registros'] / resumen_general['dias_activos']).round(1)
resumen_general['duracion_total'] = resumen_general['duracion_total'].round(2)

resumen_general.columns = [
    'Monitor', 'Total Registros', 'Publicadores Únicos', 
    'Días Activos', 'Duración Total (min)', 'Distritos Únicos', 
    'Promedio por Día'
]

st.dataframe(
    resumen_general.sort_values('Total Registros', ascending=False),
    use_container_width=True,
    hide_index=True
)
