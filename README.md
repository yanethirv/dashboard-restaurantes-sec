# 📊 Benchmarking Financiero con IA: Sector Restaurantes

Una plataforma analítica avanzada construida con Streamlit que combina extracción de datos oficiales de la SEC (XBRL), datos de mercado en tiempo real y análisis generativo impulsado por IA para realizar auditorías y simulaciones financieras (CFO).

## 🚀 Características Principales

* **Filtro Global Sincronizado:** Panel lateral (*sidebar*) que controla la reactividad de todo el *dashboard*. Selecciona múltiples empresas y todas las pestañas se actualizarán en cascada.
* **Auditoría SEC (XBRL):** Extracción directa de los formularios 10-K para visualizar ingresos y costos auditados.
* **Simulador CFO (What-If):** Modelado de escenarios dinámico con *sliders* iterativos por empresa para proyectar el impacto en el EBITDA y calcular el Grado de Apalancamiento Operativo (DOL).
* **Análisis Macro:** Integración con la API de FRED para contextualizar los resultados contra la inflación de alimentos.
* **Reporte Ejecutivo IA:** Un motor de inferencia conectado directamente a Gemini 1.5 Flash (vía REST API) que procesa los datos financieros de las empresas seleccionadas y genera un único diagnóstico forense comparativo.

## 🛠️ Arquitectura y Tecnologías

* **Frontend / Framework:** Streamlit
* **Procesamiento de Datos:** Pandas, Numpy
* **Fuentes de Datos:** SEC REST API, Yahoo Finance (RSS feed bypass), FRED API
* **Inteligencia Artificial:** Google Gemini API (Integración directa vía peticiones HTTP `requests` para máxima resiliencia en la nube).

## ⚙️ Configuración y Despliegue

1. Clonar el repositorio.
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar los secretos (Variables de Entorno). En Streamlit Cloud, agrega tu clave en `Settings > Secrets`:
   ```toml
   GEMINI_API_KEY = "AIzaSy_TU_CLAVE_AQUI"
   ```
4. Ejecutar localmente: `streamlit run dashboard_app.py`
