import streamlit as st
import pandas as pd

st.set_page_config(page_title="Seguimiento Censo - Publicadores", layout="wide")
st.title("📊 Seguimiento de Censo por Monitor")

# Cargar datos
df = pd.read_excel('dashboard_lpi_reporte_diario.xlsx')

# Asegurar que date sea datetime
df['date'] = pd.to_datetime(df['date'])

# Información general
st.info(f"📅 Total de fechas: {df['date'].nunique()} | Total de monitores: {df['Monitor'].nunique()} | Total de publicadores: {df['publicador'].nunique()} | Total de registros: {len(df)} | Número total: {df['numero_total'].sum()}")

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
        st.caption(f"Supervisa a {df_monitor['publicador'].nunique()} publicadores | Número total: {df_monitor['numero_total'].sum()}")
        
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
        
        # Agregar columna de total de registros
        tabla_pivot['TOTAL REGISTROS'] = tabla_pivot.sum(axis=1)
        
        # Ordenar por total de registros descendente
        tabla_pivot = tabla_pivot.sort_values('TOTAL REGISTROS', ascending=False)
        
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
                "TOTAL REGISTROS": st.column_config.NumberColumn("TOTAL REGISTROS", width="small", help="Total de registros realizados"),
                "NÚMERO TOTAL": st.column_config.NumberColumn("NÚMERO TOTAL", width="small", help="Suma de número total")
            },
            height=600
        )
