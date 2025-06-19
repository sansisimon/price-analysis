# 📊 Price Analysis

**Proyecto de análisis y comparación de precios entre distintas herramientas.**

Este proyecto implementa un proceso ETL (Extract, Transform, Load) para procesar y comparar precios provenientes de distintas fuentes (archivos Excel/CSV) y generar archivos limpios listos para su carga en Power BI (cuya visualización también está automatizada).

---

## ⚙️ Requisitos

- Python 3.9+ recomendado
- Power BI (para visualización)

---

## 🗂️ Estructura del proyecto

```bash
price-analysis/
├── src/
│ ├── transformacion.py # Funciones ETL
│ └── visualizacion.py # Funciones para gráficas
│
├── data/ # Archivos de entrada (no incluidos en el repo)
│ ├── bend.xlsm
│ ├── ds.xlsx
│ └── pe.csv
│
├── output/ # CSVs generados tras el procesamiento
│ ├── merged.csv
│ └── precios.csv
│
├── main.py # Script principal
├── requirements.txt # Dependencias
├── README.md # Este archivo
├── .gitignore # Ignora archivos que no deben subirse
├── .venv/ # Entorno virtual (no se sube a git)
```

## 🚀 Instalación :

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

### ⚠️ 🚨 ¿Problemas con la instalación?
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
    #⚠️ Esto solo hay que hacerlo una vez por usuario en tu ordenador.

# 4. Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecución del ETL 
Ejecutamos el script principal `(main.py)` desde la terminal o consola, y le pasamos los argumentos para indicarle qué archivo queremos procesar y dónde queremos guardar el resultado.

```bash
# Ejecutar en el terminal:
python main.py --input data/pe.csv --output output/precios.csv
```

Breve explicación del comando anterior:

- `python main.py`: Ejecuta el archivo main.py con Python.
- `--input`: le indicamos al script: que use el archivo `data/pe.csv` como entrada.
- `--output`: le indicamos al script que guarde el resultado de main.py en `output/precios.csv`.

## 🖥️ Visualización
Los CSV generados pueden cargarse en Power BI para su análisis visual. Este proyecto incluye algunas funciones en visualizacion.py si se necesitan gráficos adicionales desde Python.


## ✅ Pasos necesarios cada vez que quieras usar el ETL:
1. Abre la terminal integrada de VSCode

2. Activa el entorno virtual:
```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

3. (Opcional) Verifica que estás usando el entorno correcto con el comando a cotninuación:

```bash

Get-Command python # Windows opción 1
where python   # Windows opción 2

which python   # Mac/Linux
```
Debería salir una ruta al python.exe:
```bash
CommandType     Name                                               Version    Source
-----------     ----                                               -------    ------
Application     python.exe                                         ...        C:\Users\.....\price-analysis\.venv\Scripts\python.exe
```

4. Ejecuta tu script ETL como lo venías haciendo:
```bash
python main.py --input data/pe.csv --output output/precios.csv
```