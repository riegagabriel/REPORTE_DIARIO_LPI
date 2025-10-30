import streamlit as st
import pandas as pd

st.set_page_config(page_title="Seguimiento Operativo - Todos los Formatos", layout="wide")
st.title("📊 Seguimiento por encuesta y equipo monitor")

# Cargar todos los DataFrames desde Excel
@st.cache_data
def load_data():
    """Carga todos los DataFrames desde archivos Excel"""
    dataframes = {}
    
    try:
        dataframes['📋 Reporte Diario'] = pd.read_excel('merged_reporte_diario.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_reporte_diario.xlsx")
        dataframes['📋 Reporte Diario'] = pd.DataFrame()
    
    try:
        dataframes['📝 Encuesta -Formato de Reclamos-'] = pd.read_excel('merged_reclamo.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_reclamo.xlsx")
        dataframes['📝 Reclamos'] = pd.DataFrame()
    
    try:
        dataframes['❌ Formato de eliminación o tachas'] = pd.read_excel('merged_tacha.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_tacha.xlsx")
        dataframes['❌ Tachas'] = pd.DataFrame()
    
    try:
        dataframes['📑 Formato de razones -reclamo o tacha-'] = pd.read_excel('merged_razones_tacha.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_razones_tacha.xlsx")
        dataframes['📑 Razones Tacha'] = pd.DataFrame()
    
    try:
        dataframes['🗳️ Encuesta Ciudadana'] = pd.read_excel('merged_ciudadana.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_ciudadana.xlsx")
        dataframes['🗳️ Encuesta Ciudadana'] = pd.DataFrame()
    
    try:
        dataframes['🔓 Cuestionario de Apertura'] = pd.read_excel('merged_apertura.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_apertura.xlsx")
        dataframes['🔓 Apertura'] = pd.DataFrame()
    
    try:
        dataframes['🔒 Cuestionario de Cierre'] = pd.read_excel('merged_cierre.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_cierre.xlsx")
        dataframes['🔒 Cierre'] = pd.DataFrame()
    
    try:
        dataframes['⚰️Formato Acta de Defunción'] = pd.read_excel('merged_defuncion.xlsx')
    except FileNotFoundError:
        st.warning("⚠️ No se encontró: merged_defuncion.xlsx")
        dataframes['⚰️ Defunción'] = pd.DataFrame()
    
    return dataframes

# Cargar datos
with st.spinner('Cargando datos...'):
    dataframes = load_data()

# Filtrar DataFrames vacíos para información general
dataframes_con_datos = {k: v for k, v in dataframes.items() if len(v) > 0}

# Información general de todos los datos
if dataframes_con_datos:
    st.info(f"📊 Formatos con datos: {len(dataframes_con_datos)} de {len(dataframes)}")
else:
    st.error("❌ No se cargaron datos. Verifica que los archivos Excel estén en la ubicación correcta.")
    st.stop()

# Crear pestañas principales para cada DataFrame
main_tabs = st.tabs(list(dataframes.keys()))

# Iterar sobre cada pestaña principal (DataFrame)
for tab_idx, (df_name, df) in enumerate(dataframes.items()):
    with main_tabs[tab_idx]:
        st.header(df_name)
        
        # Verificar si el DataFrame está vacío
        if len(df) == 0:
            st.warning(f"⚠️ No hay datos disponibles para {df_name}")
            continue
        
        # Asegurar que date/fecha esté en datetime
        date_col = None
        if 'date' in df.columns:
            date_col = 'date'
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        elif 'fecha_reclamo' in df.columns:
            date_col = 'fecha_reclamo'
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Información general del DataFrame
        if date_col and df[date_col].notna().any():
            st.info(f"📅 Fechas: {df[date_col].nunique()} | 👥 Monitores: {df['Monitor'].nunique()} | 📍 Distritos: {df['DISTRITO'].nunique()} | 📊 Total registros: {len(df)}")
        else:
            st.info(f"👥 Monitores: {df['Monitor'].nunique()} | 📍 Distritos: {df['DISTRITO'].nunique()} | 📊 Total registros: {len(df)}")
        
        # Obtener lista única de monitores ordenados
        monitores = sorted(df['Monitor'].dropna().unique())
        
        if len(monitores) == 0:
            st.warning("⚠️ No hay monitores en este formato")
            continue
        
        # Crear sub-pestañas para cada monitor
        monitor_tabs = st.tabs(monitores)
        
        # Iterar sobre cada sub-pestaña (monitor)
        for monitor_idx, monitor in enumerate(monitores):
            with monitor_tabs[monitor_idx]:
                # Filtrar datos del monitor
                df_monitor = df[df['Monitor'] == monitor].copy()
                
                st.subheader(f"👤 Monitor: {monitor}")
                
                # Determinar columna de identificación (publicador o username)
                id_col = 'publicador' if 'publicador' in df_monitor.columns else 'username'
                
                # Información específica del monitor
                if 'numero_total' in df_monitor.columns:
                    st.caption(f"Supervisa a {df_monitor[id_col].nunique()} publicadores | Registros: {len(df_monitor)} | Número total: {df_monitor['numero_total'].sum()}")
                else:
                    st.caption(f"Supervisa a {df_monitor[id_col].nunique()} publicadores | Registros: {len(df_monitor)}")
                
                st.markdown("---")
                
                # TABLA PRINCIPAL: Registros por Publicador y Fecha
                if date_col and df_monitor[date_col].notna().any():
                    st.markdown(f"### 📅 Registros por {id_col.title()} y Fecha")
                    
                    # Crear tabla pivote: Publicadores (filas) x Fechas (columnas)
                    tabla_registros = df_monitor.groupby([id_col, date_col]).size().reset_index(name='registros')
                    
                    # Pivotar para tener fechas como columnas
                    tabla_pivot = tabla_registros.pivot(
                        index=id_col,
                        columns=date_col,
                        values='registros'
                    ).fillna(0).astype(int)
                    
                    # Agregar columna de total de registros
                    tabla_pivot['TOTAL REGISTROS'] = tabla_pivot.sum(axis=1)
                    
                    # Si existe numero_total, agregarlo también
                    if 'numero_total' in df_monitor.columns:
                        numero_total_por_pub = df_monitor.groupby(id_col)['numero_total'].sum()
                        tabla_pivot['NÚMERO TOTAL'] = numero_total_por_pub
                    
                    # Ordenar por total de registros descendente
                    tabla_pivot = tabla_pivot.sort_values('TOTAL REGISTROS', ascending=False)
                    
                    # Formatear nombres de columnas (fechas)
                    tabla_pivot.columns = [col.strftime('%d/%m') if isinstance(col, pd.Timestamp) else col for col in tabla_pivot.columns]
                    
                    # Resetear índice para mostrar publicador como columna
                    tabla_pivot_reset = tabla_pivot.reset_index()
                    tabla_pivot_reset.columns.name = None
                    
                    # Configurar columnas
                    column_config = {
                        id_col: st.column_config.TextColumn(id_col.title(), width="large"),
                        "TOTAL REGISTROS": st.column_config.NumberColumn("TOTAL REGISTROS", width="small", help="Total de registros realizados")
                    }
                    
                    if 'NÚMERO TOTAL' in tabla_pivot_reset.columns:
                        column_config["NÚMERO TOTAL"] = st.column_config.NumberColumn("NÚMERO TOTAL", width="small", help="Suma de número total")
                    
                    # Mostrar tabla con formato mejorado
                    st.dataframe(
                        tabla_pivot_reset,
                        use_container_width=True,
                        hide_index=True,
                        column_config=column_config,
                        height=600
                    )
                else:
                    # Si no hay columna de fecha, mostrar tabla simple
                    st.markdown(f"### 📊 Resumen por {id_col.title()}")
                    
                    resumen = df_monitor.groupby(id_col).size().reset_index(name='TOTAL REGISTROS')
                    resumen = resumen.sort_values('TOTAL REGISTROS', ascending=False)
                    
                    st.dataframe(
                        resumen,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            id_col: st.column_config.TextColumn(id_col.title(), width="large"),
                            "TOTAL REGISTROS": st.column_config.NumberColumn("TOTAL REGISTROS", width="small")
                        },
                        height=400
                    )
                
                # Mostrar detalles adicionales
                with st.expander("🔍 Ver datos detallados"):
                    st.dataframe(df_monitor, use_container_width=True, height=400)

st.markdown("---")
st.caption("Dashboard generado automáticamente para seguimiento operativo")
