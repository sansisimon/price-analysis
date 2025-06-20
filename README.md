# 📊 Price Analysis

*Proyecto de análisis y comparación de precios entre distintas herramientas*

Este proyecto implementa un proceso ETL (Extract, Transform, Load) para procesar y comparar precios provenientes de distintas fuentes (archivos Excel/CSV) y generar archivos limpios listos para su carga en Power BI (cuya visualización también está automatizada a través de una plantilla).

---

## ⚙️ 1. Requisitos

- Python 3.9+ recomendado
- Power BI (para visualización)

---

## 🗂️ 2. Estructura del proyecto

```bash
price-analysis/
├── src/
│ ├── transformacion.py # Funciones ETL
│ └── visualizacion.py # Funciones para gráficas en Python
│
├── data/ # Archivos de entrada (no incluidos en el repo)
│ ├── bend.xlsm
│ ├── ds.xlsx
│ └── pe.csv
│
├── output/ # CSVs generados tras el procesamiento
│ ├── merged_viz.csv
│ ├── merged.csv
│ └── precios.csv
│
├── main.py # Script principal
├── requirements.txt # Dependencias
├── template.pbit # Plantilla de Power BI automatizada para las visualizaciones
├── README.md # Este archivo
├── .gitignore # Ignora archivos que no deben subirse
├── .venv/ # Entorno virtual (no incluido en el repo)
```

## 🚀 3. Instalación (pasos para la primera vez que se usa) :

Confirma que tienes un entorno virtual activado con el objetivo de aislar dependencias del proyecto e instala los requisitos dentro del entorno virtual. Ejecutar en el Terminal:

```bash
# 1. Crear entorno virtual si todavía no lo tienes. Se va a llamar venv por convención.
python -m venv .venv

# 2. Activar entorno virtual 
    # Windows
    .venv\Scripts\activate

    # Mac/Linux
    source .venv/bin/activate

# 3. Instalar dependencias: 
pip install -r requirements.txt
```

### ⚠️ 🚨 ¿Problemas con la instalación en Windows?
Activación del entorno virtual en Windows (PowerShell). En Windows, si ves un error al intentar activar el entorno virtual como este:
```bash
.venv\Scripts\Activate : El módulo '.venv' no pudo cargarse...
```
Solución propuesta:

```bash
# 1. Ejecuta este comando una sola vez para permitir ejecutar scripts locales:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Confirma con `S` si te pregunta.

# 3. Luego vuelve a activar el entorno:
    .venv\Scripts\activate
    
# 4. Instalar dependencias
pip install -r requirements.txt
```

## ▶️ 4. Ejecución del ETL 
Ejecutamos el script principal `(main.py)` desde la terminal o consola, y le pasamos los argumentos para indicarle qué archivo queremos procesar y dónde queremos guardar el resultado.

```bash
# Ejecutar en el terminal:
python main.py 
```

### 🔍 *Pasos necesarios cada vez que quieras usar el ETL (para la segunda vez que se usa y siguientes)* :
1. Abre la terminal integrada de VSCode.

2. Activa el entorno virtual:
```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

3. Ejecuta tu script ETL como lo venías haciendo:
```bash
python main.py
```

## 🖥️ 5.  Visualización
Los CSV generados pueden cargarse en Power BI para su análisis visual. Este proyecto incluye algunas funciones en visualizacion.py si se necesitan gráficos adicionales desde Python.

## 6. 🗂️ Generación automática de rutas para Power BI
Cada vez que se ejecute el proceso ETL (`main.py`), además de los archivos `CSV` generados, también se crearán archivos `.txt` con la ruta absoluta de cada uno.

Estos archivos .txt permiten a Power BI encontrar automáticamente los CSV, independientemente de la ubicación del proyecto en tu equipo.

| Archivo generado | Contenido |  |
|---|---|---|
| `output/merged_path.txt` | Ruta absoluta del archivo merged.csv| 
| `output/precios_path.txt` | Ruta absoluta del archivo precios.csv | 


✅ Importante: **Power BI está configurado para leer estas rutas al actualizar los datos.** No se necesita indicar manualmente la ubicación del CSV --> todo queda automatizado.