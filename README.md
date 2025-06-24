
Dashboard intuitivo en Streamlit para control de Kardex, gestión de inventario, sugerencia de pedidos y seguimiento de presupuestos con SQLite.

# Dashboard de Control Integral para Negocios con Streamlit y SQLite

## 🚀 Visión General del Proyecto

Este **Dashboard de Control Integral** es una solución robusta y fácil de usar, desarrollada con **Streamlit** y **SQLite**, diseñada para pequeñas y medianas empresas. Permite centralizar la gestión de **inventario (Kardex)**, optimizar la **sugerencia de pedidos** y ofrecer un seguimiento detallado del **control de presupuestos** frente a los gastos mensuales. Olvídate de las hojas de cálculo dispersas y toma decisiones informadas en tiempo real.

---

## ✨ Características Principales

* **Control de Kardex Automatizado:**
    * Registro de entradas y salidas de productos.
    * Visualización del historial de movimientos de inventario.
    * Cálculo automático del **stock actual** de cada producto.
    * Filtros dinámicos por producto, fecha y tipo de movimiento.

* **Pedido Sugerido Inteligente:**
    * Generación automática de un **listado de productos** que requieren reposición, basado en el **stock mínimo**.
    * Facilita la planificación de compras y evita la ruptura de stock.

* **Gestión de Presupuestos Mensuales:**
    * Definición de **presupuestos mensuales** totales.
    * **"Spliteado" o división del presupuesto** por categorías de gasto personalizadas (ej. compras, operaciones, marketing).
    * Registro detallado de **gastos reales** por categoría.
    * **Análisis visual** comparativo entre el presupuesto asignado y el gasto real.
    * KPIs claros de uso del presupuesto y montos restantes.

* **Base de Datos Local y Eficiente:**
    * Utiliza **SQLite** para una gestión de datos ligera, eficiente y portable, ideal para aplicaciones locales o de bajo tráfico.

* **Interfaz de Usuario Intuitiva (UI/UX):**
    * Desarrollado con **Streamlit** para una experiencia de usuario limpia, interactiva y fácil de navegar.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3.x**
* **Streamlit**: Para la interfaz de usuario interactiva y el despliegue del dashboard.
* **SQLite3**: Como base de datos ligera y embebida para la persistencia de datos.
* **Pandas**: Para la manipulación y análisis de datos.
* **Plotly (o Matplotlib/Altair)**: Para visualizaciones de datos atractivas y significativas.

---

## 🚀 Cómo Ponerlo en Marcha

Sigue estos pasos para configurar y ejecutar el dashboard en tu máquina local:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/santiagourdaneta/control-negocio-streamlit-sqlite/
    cd control-negocio-streamlit-sqlite
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación Streamlit:**
    ```bash
    streamlit run app.py
    ```
    (Asegúrate de que tu archivo principal de Streamlit se llame `app.py` o ajusta el comando según sea necesario.)

5.  **Accede al Dashboard:**
    Abre tu navegador web y ve a la URL que Streamlit te proporcione (normalmente `http://localhost:8501`).

---

## 🔒 Seguridad y Validaciones

Se han implementado **validaciones de entrada** para asegurar la integridad de los datos y prevenir errores. Consideraciones de seguridad, como el manejo adecuado de la base de datos local y la validación de stock, son fundamentales para la fiabilidad del sistema. Para entornos de producción o multiusuario, se recomienda añadir un módulo de **autenticación y autorización**.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar el dashboard, por favor, abre un `issue` o envía un `pull request`.

---

**Desarrollado con ❤️ para optimizar la gestión de tu negocio.**
