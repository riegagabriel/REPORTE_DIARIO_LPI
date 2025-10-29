import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Registros por Publicador", layout="wide")

# Título principal
st.title("📊 Registros por Publicador y Día")

# Cargar el dataframe (asume que ya lo tienes cargado como 'df')
# df = pd.read_csv('tu_archivo.csv')  # Descomenta y ajusta según tu caso

# Para este ejemplo, asumimos que el dataframe está disponible como 'df'
# Asegurarse de que 'date' sea datetime
if 'df' in st.session_state:
    df = st.session_state.df
else:
    st.warning("Por favor, carga tu dataframe en st.session_state.df")
    st.stop()

# Convertir date a datetime si no lo está
df['date'] = pd.to_datetime(df['date'])

# Obtener lista única de publicadores ordenada
publicadores = sorted(df['publicador'].unique())

# Crear pestañas para cada publicador
tabs = st.tabs(publicadores)

# Iterar sobre cada pestaña
for i, publicador in enumerate(publicadores):
    with tabs[i]:
        # Filtrar datos del publicador
        df_publicador = df[df['publicador'] == publicador].copy()
        
        # Agrupar por fecha y contar registros
        resumen = df_publicador.groupby('date').agg(
            cantidad_registros=('key', 'count'),
            duracion_promedio=('duration', 'mean'),
            duracion_total=('duration', 'sum')
        ).reset_index()
        
        # Formatear la fecha para mejor visualización
        resumen['date'] = resumen['date'].dt.strftime('%Y-%m-%d')
        resumen['duracion_promedio'] = resumen['duracion_promedio'].round(2)
        resumen['duracion_total'] = resumen['duracion_total'].round(2)
        
        # Renombrar columnas para mejor presentación
        resumen.columns = ['Fecha', 'Cantidad de Registros', 'Duración Promedio (min)', 'Duración Total (min)']
        
        # Mostrar información del publicador
        st.subheader(f"📋 {publicador}")
        
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Registros", len(df_publicador))
        with col2:
            st.metric("Días Activos", len(resumen))
        with col3:
            st.metric("Promedio por Día", f"{len(df_publicador)/len(resumen):.1f}")
        with col4:
            st.metric("Duración Total", f"{df_publicador['duration'].sum():.1f} min")
        
        st.markdown("---")
        
        # Mostrar tabla
        st.dataframe(
            resumen,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Fecha": st.column_config.TextColumn("Fecha", width="medium"),
                "Cantidad de Registros": st.column_config.NumberColumn("Cantidad de Registros", width="medium"),
                "Duración Promedio (min)": st.column_config.NumberColumn("Duración Promedio (min)", format="%.2f"),
                "Duración Total (min)": st.column_config.NumberColumn("Duración Total (min)", format="%.2f")
            }
        )
        
        # Gráfico de barras
        st.bar_chart(resumen.set_index('Fecha')['Cantidad de Registros'])

# Agregar sección de resumen general al final
st.markdown("---")
st.subheader("📈 Resumen General")

resumen_general = df.groupby(['publicador']).agg(
    total_registros=('key', 'count'),
    dias_activos=('date', 'nunique'),
    duracion_total=('duration', 'sum')
).reset_index()

resumen_general['promedio_por_dia'] = (resumen_general['total_registros'] / resumen_general['dias_activos']).round(1)
resumen_general['duracion_total'] = resumen_general['duracion_total'].round(2)

resumen_general.columns = ['Publicador', 'Total Registros', 'Días Activos', 'Duración Total (min)', 'Promedio por Día']

st.dataframe(
    resumen_general.sort_values('Total Registros', ascending=False),
    use_container_width=True,
    hide_index=True
)
