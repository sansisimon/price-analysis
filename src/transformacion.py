#%%


#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
#pip install openpyxl
pd.set_option('display.max_columns', None)

#%%
def cargar_y_procesar_excel_bend(ruta_archivo = "bend.xlsm", hoja = "B-Ends"):
    """Carga y procesa el archivo Excel B-End.

    Realiza limpieza de columnas, formatea strings y filtra las ofertas válidas.

    Args:
        ruta_archivo (str): Ruta al archivo Excel. Por defecto: "bend.xlsm"
        hoja (str): Nombre de la hoja del Excel a cargar. Por defecto: "B-Ends"

    Returns:
        pd.DataFrame: DataFrame procesado y listo para análisis.
    """

    #skiprows porque empieza en la fila 7
    bend = pd.read_excel(ruta_archivo, sheet_name=hoja, skiprows = 6, header=1) 

    #Limpieza de columnas:
    bend.columns = bend.columns.str.strip() 
    bend.rename(columns = {'Unnamed: 0': 'quotation_ID'}, inplace = True)
    
    #Formateo de columnas:
    bend['Main Access Currency'] = bend['Main Access Currency'].str.lower().str.strip()
    bend['City'] = bend['City'].str.title()
    bend['Country'] = bend['Country'].str.replace('_', ' ')

    #Columna nueva para identificar el origen
    bend['Source'] = 'Request B-End'

    # Filtrar: solo 'Response to Request' para poder analizar la desviación de precios. Confirmar con Antonio.
    bend = bend[bend['Does this offer match the customer request'] == 'Response to Request'] 

    # Ordenar por 'Option ID' y resetear índice
    bend.sort_values(by='Option ID', ascending=True, inplace=True) 

    #Cremos una nueva columna de índice 'id' y renombramos columnas
    bend = bend.reset_index(drop=True) #eliminamos el índice que salía por defecto de pandas para crear uno nuevo que va a ser la igual en los tres dataframes, por si el unique ID no coincide
    bend = bend.reset_index().rename(columns = {'index': 'id', 'Comments VPN Site Info\n/Commercial Model': 'Commercial Model'})
    
    return bend