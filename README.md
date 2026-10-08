# 📊 Dashboard de Benchmarking Financiero e IA Forense: Sector Restaurantes

Un ecosistema integral de análisis financiero y *Business Intelligence* diseñado para auditar, comparar y diagnosticar empresas del sector de restaurantes que cotizan en bolsa. Esta plataforma extrae datos oficiales de la SEC y los procesa a través de un motor de inferencia matemática propio, inyectando los resultados en un modelo de lenguaje de última generación (LLM) para generar reportes ejecutivos automatizados de nivel de Director Financiero (CFO).

🚀 **Despliegue en vivo:** [Ver el Dashboard en Streamlit](https://dashboard-restaurantes-sec.streamlit.app/)

---

## 🏗️ Arquitectura y Stack Tecnológico

El proyecto está construido bajo una arquitectura *end-to-end* que abarca desde la extracción y limpieza de datos hasta el despliegue reactivo en la nube:

*   **Frontend y Orquestación:** [Streamlit](https://streamlit.io/) (Interfaz de usuario reactiva, gestión de estado y sistema de caché `@st.cache_data` para optimización de rendimiento y cuotas de API).
*   **Procesamiento de Datos y Motor Matemático:** `Python 3.11`, `Pandas`, `NumPy`. (Procesamiento de datos tabulares, cálculos de KPIs de P&L, márgenes cruzados y modelado de escenarios).
*   **Extracción de Datos Financieros:** `yfinance`, Datos XBRL auditados de la SEC (Securities and Exchange Commission).
*   **Inteligencia Artificial Generativa:** API de Google Gemini (`google-generativeai`), utilizando modelos estructurados optimizados (`gemini-1.5-flash`) para análisis forense avanzado sin alucinaciones, mediante estrategias de *Superprompting*.
*   **Visualización Dinámica:** `Plotly` (Gráficos interactivos de series de tiempo, barras agrupadas y análisis de dispersión).

---

## 🎯 Funcionalidades Principales

### 1. Perfilado de Modelos de Negocio y Auditoría SEC
*   Análisis comparativo (*Benchmarking*) de las principales cadenas de restaurantes (ej. Chipotle, Domino's, McDonald's).
*   Visualización interactiva de ingresos históricos, costos de ventas (COGS), gastos operativos (SG&A) y utilidades netas basadas en reportes 10-K.

### 2. Simulador CFO (What-If Analysis)
*   Motor de sensibilidad que permite alterar variables macro y microeconómicas (inflación de insumos, elasticidad de precios, optimización laboral).
*   Cálculo en tiempo real del impacto en el margen de contribución y el punto de equilibrio operativo.

### 3. Diagnóstico Forense CFO impulsado por IA
Un consultor financiero automatizado que recibe la estructura contable de la empresa seleccionada y genera un informe narrativo detallado que incluye:
*   **Radiografía Estructural:** Análisis vertical y horizontal de los estados de resultados.
*   **Detección de Fugas de Capital:** Identificación de riesgos operativos mediante semaforización.
*   **Roadmap Estratégico:** Planes de acción a corto y mediano plazo para protección de márgenes y optimización de flujos de caja.

---

## ⚙️ Instalación y Despliegue Local

Para ejecutar este proyecto en un entorno local y explorar el código fuente, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/yanethirv/dashboard-restaurantes-sec](https://github.com/yanethirv/dashboard-restaurantes-sec)
   cd dashboard-restaurantes-sec
