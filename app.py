import streamlit as st
import pyodbc

# Configurar conexión a SQL Server
server = 'DESKTOP-NH69J86'
database = 'PEX'
username = 'Ivan_Calderon'
password = 'Ivan159357*'

conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

# Función para obtener la lista de partidas desde la BD
def obtener_partidas():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Partida FROM Partidas")
        partidas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return partidas
    except Exception as e:
        st.error(f"Error al obtener partidas: {e}")
        return []

# Función para obtener los datos de la partida seleccionada
def obtener_datos_partida(partida):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT CodigoPartida, TipoPrecio, Precio FROM Partidas WHERE Partida = ?", (partida,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {"CodigoPartida": row[0], "TipoPrecio": row[1], "Precio": row[2]}
        else:
            return {"CodigoPartida": "", "TipoPrecio": "", "Precio": 0.0}
    except Exception as e:
        st.error(f"Error al obtener datos de partida: {e}")
        return {"CodigoPartida": "", "TipoPrecio": "", "Precio": 0.0}

# Inicializar session_state
if "mostrar_subvista" not in st.session_state:
    st.session_state.mostrar_subvista = False

if "IP_actual" not in st.session_state:
    st.session_state.IP_actual = ""

if "detalle" not in st.session_state:
    st.session_state.detalle = {"baremos": 1, "cantidad": 1, "precio": 0.0, "partida": "", "codigo_partida": "", "tipo_precio": ""}

# Función para resetear la subvista
def reset_subvista():
    st.session_state.detalle = {"baremos": 1, "cantidad": 1, "precio": 0.0, "partida": "", "codigo_partida": "", "tipo_precio": ""}
    st.rerun()

st.title("Registro de Producción")

if not st.session_state.mostrar_subvista:
    # Formulario principal
    Cliente = st.selectbox("Cliente:", ["TDP", "Pangeaco"])
    IP = st.text_input("IP")
    Area = st.selectbox("Área:", ["Ingeniería", "Mantenimiento", "Ruta", "PIN"])
    Descripcion = st.text_input("Descripción")
    Tipo_Trabajo = st.text_input("Tipo de Trabajo")
    Fecha_IP = st.date_input("Fecha IP")
    Zonal = st.selectbox("Zonal:", ["Chimbote", "Lima", "Huaraz", "Piura", "Otros"])
    Estado_en_Campo = st.selectbox("Estado en Campo:", ["Otros", "Finalizado", "En curso", "Cancelado", "Suspendido"])
    Gestor = st.selectbox("Gestor:", ["Luis Chuquimango", "Dori Reto", "Naycha de Paz", "Wendy Villanueva", "Veronica Guerra",
                                      "Waldeir Guarnizo", "Jhon Canazas", "Juan Vega", "Jean Flores", "Melani Juarez", "Jose Chaname"])
    Observaciones = st.text_input("Observaciones")

    if st.button("Guardar"):
        if all([Cliente, IP, Area, Descripcion, Tipo_Trabajo, Fecha_IP, Zonal, Estado_en_Campo, Gestor, Observaciones]):
            st.session_state.IP_actual = IP  # Guardar el IP ingresado
            st.session_state.mostrar_subvista = True  # Mostrar la subvista
            reset_subvista()  # Limpiar subvista
            st.rerun()
        else:
            st.warning("Por favor, completa todos los campos.")

else:
    # Subvista para ingresar los detalles
    st.subheader(f"Registrar Detalles para IP: {st.session_state.IP_actual}")

    # Obtener lista de partidas
    lista_partidas = obtener_partidas()
    
    # Selección de partida
    Partida = st.selectbox("Partida", lista_partidas, key="partida")

    # Cuando cambia la partida, actualizar los demás campos
    if Partida:
        datos_partida = obtener_datos_partida(Partida)
        st.session_state.detalle["codigo_partida"] = datos_partida["CodigoPartida"]
        st.session_state.detalle["tipo_precio"] = datos_partida["TipoPrecio"]
        st.session_state.detalle["precio"] = datos_partida["Precio"]

    # Mostrar valores obtenidos automáticamente
    CodigoPartida = st.text_input("Código de Partida", st.session_state.detalle["codigo_partida"], disabled=True)
    TipoPrecio = st.text_input("Tipo de Precio", st.session_state.detalle["tipo_precio"], disabled=True)
    Precio = st.number_input("Precio", min_value=0.0, format="%.2f", key="precio", value=st.session_state.detalle["precio"])

    # Otros inputs
    Baremos = st.number_input("Baremos", min_value=1, key="baremos", value=st.session_state.detalle["baremos"])
    Cantidad = st.number_input("Cantidad", min_value=1, key="cantidad", value=st.session_state.detalle["cantidad"])

    # Cálculo automático del IngresoTotal
    IngresoTotal = Baremos * Cantidad * Precio
    st.text(f"Total Calculado: {IngresoTotal:.2f}")

    if st.button("Guardar Detalle"):
        st.success("Detalle guardado correctamente.")
        reset_subvista()  # Resetear valores de la subvista
        st.rerun()

    if st.button("Finalizar"):
        st.session_state.mostrar_subvista = False
        st.session_state.IP_actual = ""
        st.rerun()

