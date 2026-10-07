# 📊 Manual de Usuario: Dashboard de Inteligencia Financiera (Sector Restaurantes)

## Resumen Ejecutivo
Este panel interactivo (*dashboard*) es una herramienta de inteligencia de negocios diseñada para analizar y comparar la salud financiera, escala operativa y valoración de nueve (9) corporaciones gigantes del sector de restaurantes y comida rápida (QSR & Casual Dining). 

Los datos presentados se actualizan y derivan de dos fuentes primarias: bases de mercado (Yahoo Finance) y documentos auditados oficiales extraídos directamente del repositorio de la **Comisión de Bolsa y Valores de EE. UU. (SEC)**.

---

## Guía de Navegación

La aplicación está diseñada para ser fluida e intuitiva. 
* **Filtros Interactivos:** En el **panel lateral izquierdo**, puede seleccionar libremente a los competidores que desea analizar. El tablero reaccionará al instante.
* **Gráficos Flotantes:** Al pasar el cursor (*hover*) sobre cualquier barra o línea de los gráficos, emergerán *tooltips* con los nombres de las empresas y las cifras exactas calculadas, evitando que tenga que adivinar los valores.

El dashboard está estructurado en tres (3) pestañas lógicas:

### 1. Benchmarking Financiero (Rentabilidad)
Esta sección evalúa la eficiencia con la que cada empresa opera en el mercado.
* **Tarjetas de Márgenes Netos:** Refleja la rentabilidad final. Muestra de forma porcentual cuánto dinero retiene la compañía como ganancia pura por cada dólar facturado.
* **Gráfico de Barras (Ingresos vs Utilidad Neta):** Contrapone la facturación bruta frente a las ganancias finales, demostrando si el gran volumen de ventas de una corporación realmente se traduce en beneficios económicos tras el pago de costos, nóminas, deudas e impuestos.
* **Tendencia Histórica (5 Años):** Revela la resiliencia corporativa al ilustrar cómo ha evolucionado la utilidad neta a lo largo del tiempo, ideal para detectar patrones de estancamiento o alto crecimiento reciente.

### 2. Perfil del Modelo de Negocio (Visión Corporativa)
Para comprender a fondo con quién estamos comparando, esta pestaña ofrece métricas cualitativas y del mercado de valores.
* **Múltiplo de Valoración (Trailing P/E):** Conocido como la relación Precio-Beneficio. Indica cuánto están pagando actualmente los inversores en la bolsa por cada dólar de ganancia que genera esa empresa. Un P/E muy elevado suele implicar que el mercado espera un alto crecimiento a futuro.
* **Cantidad de Empleados:** Dimensiona el tamaño real del capital humano (un número bajo en una empresa de altos ingresos puede revelar un modelo de negocio fuertemente inclinado hacia las franquicias).
* **Resumen Operativo:** La descripción del modelo de negocio de la compañía (traducida al español) para entender la esencia de su ventaja competitiva.

### 3. Auditoría SEC (Escala Operativa Oficial)
Es la "fuente innegable de la verdad". Los datos aquí expuestos no son estimaciones, sino que **fueron extraídos y consolidados de forma automatizada mediante los lenguajes de codificación contable (XBRL) directamente desde los Formularios 10-K auditados alojados en el gobierno de Estados Unidos.**
* **Ingresos Oficiales vs Costos Directos:** Pone en perspectiva los Ingresos Totales de la corporación frente a sus Costos de Operación Directos (Insumos, comida, nómina de restaurantes e impuestos a franquicias). Este rubro está perfectamente sincronizado y ordenado de mayor a menor para facilitar el diagnóstico del tamaño real y la huella en la industria.
* **Tabla de Auditoría:** Contiene las cifras monetarias completas crudas sin redondear, garantizando transparencia total a nivel contable.

---
*Herramienta generada algorítmicamente y auditada para la toma de decisiones estratégicas.*
