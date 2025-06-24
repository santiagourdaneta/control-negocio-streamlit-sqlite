import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- Configuración de la Base de Datos ---
DB_NAME = 'dashboard_control.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Crear tabla productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY,
            nombre_producto TEXT NOT NULL UNIQUE,
            unidad_medida TEXT,
            stock_minimo INTEGER DEFAULT 0,
            precio_unitario REAL DEFAULT 0.0,
            proveedor TEXT,
            ubicacion TEXT
        )
    ''')
    
    # Crear tabla kardex
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kardex (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER,
            tipo_movimiento TEXT NOT NULL, -- 'ENTRADA' o 'SALIDA'
            cantidad INTEGER NOT NULL,
            fecha_movimiento DATE NOT NULL,
            referencia TEXT,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    ''')
    
    # Crear tabla inventario_actual (trigger podría mantenerla actualizada)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario_actual (
            id_producto INTEGER PRIMARY KEY,
            stock_actual INTEGER DEFAULT 0,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    ''')

    # Crear tabla presupuestos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presupuestos (
            id_presupuesto INTEGER PRIMARY KEY AUTOINCREMENT,
            mes_anio TEXT NOT NULL UNIQUE, -- Formato YYYY-MM
            monto_total_presupuesto REAL NOT NULL
        )
    ''')
    
    # Crear tabla detalle_presupuesto (para spliteado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_presupuesto (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_presupuesto INTEGER,
            categoria_gasto TEXT NOT NULL,
            monto_asignado REAL NOT NULL,
            FOREIGN KEY (id_presupuesto) REFERENCES presupuestos(id_presupuesto)
        )
    ''')

    # Crear tabla gastos_reales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos_reales (
            id_gasto INTEGER PRIMARY KEY AUTOINCREMENT,
            mes_anio TEXT NOT NULL, -- Formato YYYY-MM
            categoria_gasto TEXT NOT NULL,
            fecha_gasto DATE NOT NULL,
            monto_gasto REAL NOT NULL,
            descripcion TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# --- Funciones de Base de Datos (Ejemplos) ---
def get_products():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM productos", conn)
    conn.close()
    return df

def add_product(nombre, unidad, stock_min, precio, proveedor, ubicacion):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO productos (nombre_producto, unidad_medida, stock_minimo, precio_unitario, proveedor, ubicacion) VALUES (?, ?, ?, ?, ?, ?)",
                       (nombre, unidad, stock_min, precio, proveedor, ubicacion))
        conn.commit()
        # Inicializar stock actual en 0 para el nuevo producto
        cursor.execute("INSERT INTO inventario_actual (id_producto, stock_actual) VALUES (?, 0)", (cursor.lastrowid,))
        conn.commit()
        st.success(f"Producto '{nombre}' agregado exitosamente.")
    except sqlite3.IntegrityError:
        st.error(f"Error: El producto '{nombre}' ya existe.")
    finally:
        conn.close()

def add_kardex_movement(id_producto, tipo_movimiento, cantidad, referencia):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        if tipo_movimiento == 'SALIDA':
            # Validar stock
            cursor.execute("SELECT stock_actual FROM inventario_actual WHERE id_producto = ?", (id_producto,))
            current_stock = cursor.fetchone()[0]
            if current_stock < cantidad:
                st.error(f"Error: No hay suficiente stock para la salida. Stock actual: {current_stock}")
                return False
        
        cursor.execute("INSERT INTO kardex (id_producto, tipo_movimiento, cantidad, fecha_movimiento, referencia) VALUES (?, ?, ?, ?, ?)",
                       (id_producto, tipo_movimiento, cantidad, datetime.now().strftime('%Y-%m-%d'), referencia))
        
        # Actualizar inventario_actual
        if tipo_movimiento == 'ENTRADA':
            cursor.execute("UPDATE inventario_actual SET stock_actual = stock_actual + ? WHERE id_producto = ?", (cantidad, id_producto))
        else: # SALIDA
            cursor.execute("UPDATE inventario_actual SET stock_actual = stock_actual - ? WHERE id_producto = ?", (cantidad, id_producto))
        
        conn.commit()
        st.success("Movimiento de Kardex registrado y stock actualizado.")
        return True
    except Exception as e:
        st.error(f"Error al registrar movimiento: {e}")
        return False
    finally:
        conn.close()

# --- Interfaz de Usuario de Streamlit ---
st.set_page_config(layout="wide", page_title="Dashboard de Control")

# Inicializar la base de datos si no existe
init_db()

st.sidebar.title("Navegación")
selection = st.sidebar.radio("Ir a", ["Kardex", "Pedido Sugerido", "Control de Presupuestos", "Gestión de Productos"])

# --- Módulo de Gestión de Productos (ejemplo, para añadir productos) ---
if selection == "Gestión de Productos":
    st.title("Gestión de Productos")
    st.subheader("Añadir Nuevo Producto")
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Producto", key="prod_nombre")
            unidad = st.text_input("Unidad de Medida", key="prod_unidad")
            stock_min = st.number_input("Stock Mínimo", min_value=0, value=0, key="prod_stock_min")
        with col2:
            precio = st.number_input("Precio Unitario", min_value=0.0, value=0.0, format="%.2f", key="prod_precio")
            proveedor = st.text_input("Proveedor", key="prod_proveedor")
            ubicacion = st.text_input("Ubicación", key="prod_ubicacion")
        
        submitted = st.form_submit_button("Añadir Producto")
        if submitted:
            if nombre:
                add_product(nombre, unidad, stock_min, precio, proveedor, ubicacion)
            else:
                st.warning("El nombre del producto es obligatorio.")
    
    st.subheader("Productos Existentes")
    st.dataframe(get_products())

# --- Módulo Kardex ---
elif selection == "Kardex":
    st.title("Control de Kardex")
    
    products = get_products()
    product_options = {row['nombre_producto']: row['id_producto'] for index, row in products.iterrows()}
    
    st.subheader("Registrar Movimiento")
    with st.form("kardex_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_product_name = st.selectbox("Producto", list(product_options.keys()), key="kardex_prod")
            tipo_mov = st.radio("Tipo de Movimiento", ('ENTRADA', 'SALIDA'), key="kardex_tipo")
        with col2:
            cantidad = st.number_input("Cantidad", min_value=1, value=1, key="kardex_cant")
            referencia = st.text_input("Referencia (Ej. Factura #)", key="kardex_ref")
        
        submitted = st.form_submit_button("Registrar Movimiento")
        if submitted:
            if selected_product_name:
                product_id = product_options[selected_product_name]
                add_kardex_movement(product_id, tipo_mov, cantidad, referencia)
            else:
                st.warning("Debe seleccionar un producto.")

    st.subheader("Historial de Movimientos de Kardex")
    conn = sqlite3.connect(DB_NAME)
    kardex_df = pd.read_sql_query("""
        SELECT 
            k.fecha_movimiento,
            p.nombre_producto,
            k.tipo_movimiento,
            k.cantidad,
            k.referencia
        FROM kardex k
        JOIN productos p ON k.id_producto = p.id_producto
        ORDER BY k.fecha_movimiento DESC
    """, conn)
    conn.close()
    st.dataframe(kardex_df)

    # Añadir gráficos de Kardex (ejemplo)
    st.subheader("Análisis de Inventario")
    conn = sqlite3.connect(DB_NAME)
    current_stock_df = pd.read_sql_query("""
        SELECT 
            p.nombre_producto,
            ia.stock_actual
        FROM inventario_actual ia
        JOIN productos p ON ia.id_producto = p.id_producto
    """, conn)
    conn.close()
    
    if not current_stock_df.empty:
        total_stock = current_stock_df['stock_actual'].sum()
        st.metric("Stock Total Actual", f"{total_stock} unidades")
        
        st.bar_chart(current_stock_df.set_index('nombre_producto'))
    else:
        st.info("No hay productos en inventario.")

# --- Módulo Pedido Sugerido ---
elif selection == "Pedido Sugerido":
    st.title("Pedido Sugerido")
    st.write("Genera una lista de productos que necesitan ser reabastecidos.")
    
    conn = sqlite3.connect(DB_NAME)
    sug_df = pd.read_sql_query("""
        SELECT 
            p.nombre_producto,
            ia.stock_actual,
            p.stock_minimo,
            (p.stock_minimo - ia.stock_actual) AS cantidad_sugerida
        FROM inventario_actual ia
        JOIN productos p ON ia.id_producto = p.id_producto
        WHERE ia.stock_actual < p.stock_minimo
    """, conn)
    conn.close()
    
    if not sug_df.empty:
        # Filtrar para mostrar solo sugerencias válidas (cantidad_sugerida > 0)
        sug_df = sug_df[sug_df['cantidad_sugerida'] > 0]
        st.dataframe(sug_df)
        
        # Botón para exportar
        csv_export = sug_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Pedido Sugerido (CSV)",
            data=csv_export,
            file_name="pedido_sugerido.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay productos por debajo del stock mínimo. ¡Todo en orden!")

# --- Módulo Control de Presupuestos ---
elif selection == "Control de Presupuestos":
    st.title("Control de Presupuestos vs. Gastos")

    st.subheader("Configurar Presupuesto Mensual")
    with st.form("presupuesto_total_form"):
        current_month = datetime.now().strftime('%Y-%m')
        mes_anio_presupuesto = st.text_input("Mes y Año (YYYY-MM)", value=current_month, key="pres_mes_anio")
        monto_total = st.number_input("Monto Total del Presupuesto", min_value=0.0, format="%.2f", key="pres_monto")
        submitted_pres = st.form_submit_button("Guardar Presupuesto Total")
        if submitted_pres:
            if mes_anio_presupuesto and monto_total > 0:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT OR REPLACE INTO presupuestos (mes_anio, monto_total_presupuesto) VALUES (?, ?)",
                                   (mes_anio_presupuesto, monto_total))
                    conn.commit()
                    st.success(f"Presupuesto total para {mes_anio_presupuesto} guardado.")
                except Exception as e:
                    st.error(f"Error al guardar presupuesto: {e}")
                finally:
                    conn.close()
            else:
                st.warning("Debe ingresar un mes/año y un monto válido.")

    st.subheader("Dividir Presupuesto por Categoría")
    conn = sqlite3.connect(DB_NAME)
    presupuestos_disponibles = pd.read_sql_query("SELECT mes_anio, monto_total_presupuesto FROM presupuestos", conn)
    conn.close()

    if not presupuestos_disponibles.empty:
        selected_pres_mes_anio = st.selectbox("Seleccione Mes y Año del Presupuesto a Dividir", 
                                                presupuestos_disponibles['mes_anio'].tolist(), key="select_split_pres")
        
        conn = sqlite3.connect(DB_NAME)
        total_pres_for_month = presupuestos_disponibles[presupuestos_disponibles['mes_anio'] == selected_pres_mes_anio]['monto_total_presupuesto'].iloc[0]
        
        st.info(f"Monto Total Presupuestado para {selected_pres_mes_anio}: ${total_pres_for_month:,.2f}")
        
        st.session_state.categories = st.session_state.get('categories', [])
        
        def add_category():
            st.session_state.categories.append({"categoria": "", "monto": 0.0})

        if st.button("Añadir Nueva Categoría"):
            add_category()

        current_allocated = 0.0
        temp_categories = [] # Usar una lista temporal para las categorías editadas
        
        for i, cat_data in enumerate(st.session_state.categories):
            col_cat, col_monto = st.columns([0.6, 0.4])
            with col_cat:
                cat_data["categoria"] = st.text_input(f"Categoría {i+1}", value=cat_data["categoria"], key=f"cat_name_{i}")
            with col_monto:
                cat_data["monto"] = st.number_input(f"Monto Asignado {i+1}", min_value=0.0, value=cat_data["monto"], format="%.2f", key=f"cat_monto_{i}")
            current_allocated += cat_data["monto"]
            temp_categories.append(cat_data) # Actualizar la lista temporal

        st.session_state.categories = temp_categories # Reemplazar con la lista temporal actualizada

        remaining_budget = total_pres_for_month - current_allocated
        st.write(f"Monto Asignado: ${current_allocated:,.2f} | Presupuesto Restante: ${remaining_budget:,.2f}")

        if st.button("Guardar División de Presupuesto"):
            if remaining_budget >= 0: # Puede ser 0 si se asignó todo
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                try:
                    # Obtener id_presupuesto
                    cursor.execute("SELECT id_presupuesto FROM presupuestos WHERE mes_anio = ?", (selected_pres_mes_anio,))
                    pres_id = cursor.fetchone()[0]
                    
                    # Eliminar divisiones anteriores para este mes/año
                    cursor.execute("DELETE FROM detalle_presupuesto WHERE id_presupuesto = ?", (pres_id,))

                    for cat_data in st.session_state.categories:
                        if cat_data["categoria"] and cat_data["monto"] >= 0:
                            cursor.execute("INSERT INTO detalle_presupuesto (id_presupuesto, categoria_gasto, monto_asignado) VALUES (?, ?, ?)",
                                           (pres_id, cat_data["categoria"], cat_data["monto"]))
                    conn.commit()
                    st.success("División de presupuesto guardada exitosamente.")
                except Exception as e:
                    st.error(f"Error al guardar división de presupuesto: {e}")
                finally:
                    conn.close()
            else:
                st.error("El monto asignado excede el presupuesto total. Por favor, ajuste las categorías.")
    else:
        st.info("Primero configure un presupuesto mensual total.")

    st.subheader("Registrar Gasto")
    with st.form("gasto_form"):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            gasto_mes_anio = st.text_input("Mes y Año del Gasto (YYYY-MM)", value=datetime.now().strftime('%Y-%m'), key="gasto_mes_anio")
            gasto_fecha = st.date_input("Fecha del Gasto", value=datetime.now(), key="gasto_fecha")
            
            # Obtener categorías de presupuesto para el mes seleccionado
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dp.categoria_gasto FROM detalle_presupuesto dp
                JOIN presupuestos p ON dp.id_presupuesto = p.id_presupuesto
                WHERE p.mes_anio = ?
            """, (gasto_mes_anio,))
            categorias_gasto = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if categorias_gasto:
                gasto_categoria = st.selectbox("Categoría del Gasto", categorias_gasto, key="gasto_categoria")
            else:
                gasto_categoria = st.text_input("Categoría del Gasto (No hay categorías definidas para este mes)", key="gasto_categoria_manual")
                st.warning("Defina categorías en la sección 'Dividir Presupuesto por Categoría' para el mes seleccionado.")

        with col_g2:
            gasto_monto = st.number_input("Monto del Gasto", min_value=0.0, format="%.2f", key="gasto_monto")
            gasto_descripcion = st.text_area("Descripción", key="gasto_desc")
        
        submitted_gasto = st.form_submit_button("Registrar Gasto")
        if submitted_gasto:
            if gasto_mes_anio and gasto_fecha and gasto_categoria and gasto_monto > 0:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO gastos_reales (mes_anio, categoria_gasto, fecha_gasto, monto_gasto, descripcion) VALUES (?, ?, ?, ?, ?)",
                                   (gasto_mes_anio, gasto_categoria, gasto_fecha.strftime('%Y-%m-%d'), gasto_monto, gasto_descripcion))
                    conn.commit()
                    st.success("Gasto registrado exitosamente.")
                except Exception as e:
                    st.error(f"Error al registrar gasto: {e}")
                finally:
                    conn.close()
            else:
                st.warning("Todos los campos de gasto son obligatorios.")

    st.subheader("Resumen de Presupuesto vs. Gasto")
    
    # Selector de mes y año para la visualización
    conn = sqlite3.connect(DB_NAME)
    available_months = pd.read_sql_query("SELECT DISTINCT mes_anio FROM presupuestos UNION SELECT DISTINCT mes_anio FROM gastos_reales ORDER BY mes_anio DESC", conn)
    conn.close()
    
    if not available_months.empty:
        selected_view_month = st.selectbox("Seleccione Mes para Visualizar", available_months['mes_anio'].tolist(), key="select_view_month")
        
        conn = sqlite3.connect(DB_NAME)
        # Obtener presupuesto total y detalle
        presupuesto_df = pd.read_sql_query(f"""
            SELECT p.monto_total_presupuesto, dp.categoria_gasto, dp.monto_asignado
            FROM presupuestos p
            LEFT JOIN detalle_presupuesto dp ON p.id_presupuesto = dp.id_presupuesto
            WHERE p.mes_anio = '{selected_view_month}'
        """, conn)
        
        # Obtener gastos reales
        gastos_df = pd.read_sql_query(f"""
            SELECT categoria_gasto, SUM(monto_gasto) AS gasto_real
            FROM gastos_reales
            WHERE mes_anio = '{selected_view_month}'
            GROUP BY categoria_gasto
        """, conn)
        conn.close()

        if not presupuesto_df.empty:
            total_presupuesto = presupuesto_df['monto_total_presupuesto'].iloc[0] if 'monto_total_presupuesto' in presupuesto_df.columns else 0.0
            st.metric("Presupuesto Total del Mes", f"${total_presupuesto:,.2f}")

            # Combinar datos para visualización
            if not presupuesto_df.empty and 'categoria_gasto' in presupuesto_df.columns:
                merged_df = pd.merge(presupuesto_df, gastos_df, on='categoria_gasto', how='left').fillna(0)
                merged_df['gasto_real'] = merged_df['gasto_real'].round(2) # Redondear para evitar problemas de flotantes
                
                st.subheader("Comparativa por Categoría")
                st.dataframe(merged_df[['categoria_gasto', 'monto_asignado', 'gasto_real']])
                
                # Gráfico de barras apiladas
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=merged_df['categoria_gasto'],
                    y=merged_df['monto_asignado'],
                    name='Monto Asignado',
                    marker_color='lightgreen'
                ))
                fig.add_trace(go.Bar(
                    x=merged_df['categoria_gasto'],
                    y=merged_df['gasto_real'],
                    name='Gasto Real',
                    marker_color='indianred'
                ))
                fig.update_layout(barmode='group', title='Presupuesto Asignado vs. Gasto Real por Categoría')
                st.plotly_chart(fig, use_container_width=True)

                # KPIs de presupuesto restante
                total_gasto_mes = gastos_df['gasto_real'].sum() if not gastos_df.empty else 0.0
                presupuesto_restante = total_presupuesto - total_gasto_mes
                
                col_kpi1, col_kpi2 = st.columns(2)
                with col_kpi1:
                    st.metric("Gasto Total del Mes", f"${total_gasto_mes:,.2f}")
                with col_kpi2:
                    st.metric("Presupuesto Restante", f"${presupuesto_restante:,.2f}", delta_color="inverse")
            else:
                st.info("No hay categorías de presupuesto definidas para este mes o aún no se han registrado gastos.")
        else:
            st.info(f"No hay presupuesto configurado para {selected_view_month}.")
    else:
        st.info("No hay datos de presupuesto o gastos para mostrar. Configure un presupuesto primero.")

# --- Ejecución del dashboard ---
# Para ejecutar esto, guarda el código como un archivo .py (ej. app.py) y corre en la terminal:
# streamlit run app.py