import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os

def cargar_y_procesar_excel_bend(ruta_archivo = "data\\bend.xlsm", hoja = "B-Ends"):
    """Carga y procesa el archivo Excel B-End.

    Realiza limpieza de columnas, formatea strings y filtra las ofertas válidas.

    Args:
        ruta_archivo (str): Ruta al archivo Excel. Por defecto: "data\\bend.xlsm" #doble barra para saltar caracteres especiales.
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

def commercial_model_provided(celda):
    """Función para establecer el servicio prestado en una sola columna. El servicio prestado sobreescribe a la columna 'Comments VPN Site Info\n/Commercial Model'.

    Args:
        celda (string): cada valor de la columna 'Comments VPN Site Info\n/Commercial Model'

    Returns:
        string: nuevo valor que va a tomar la celda que podrá ser B4B, DIA o MPLS en función del servicio que se preste. 
    """
    if celda == 'B4B Resale-Unmanaged':
        return "B4B"
    elif celda == 'DIA Resale-Unmanaged':
        return "DIA"
    else: 
        return "MPLS" #preguntar a Antonio si aquí podemos tener también el servicio de Ethernet.
    

def completing_currency(df, columna_a_completar, columna_backup_1, columna_backup_2):
    """
    Completa valores faltantes (NaN) en una columna "objetivo" usando dos columnas de respaldo, en orden de prioridad. La prioridad es:
        1. Usar la columna principal si tiene valor.
        2. Si está vacía, usar el valor de columna_backup_1.
        3. Si también está vacía el backup_1, usar columna_backup_2.

    Args:
        df (pd.DataFrame): El DataFrame sobre el cual trabajar.
        columna_a_completar (str): Nombre de la columna principal que queremos completar.
        columna_backup_1 (str): Primera columna de respaldo (prioridad 1).
        columna_backup_2 (str): Segunda columna de respaldo (prioridad 2, si la prioridad 1 está vacía).

    Returns:
        pd.Series: Una serie con los valores completados.
    """
    id_dato_faltante = [] 

    def completar(row):
        
        if pd.isna(row[columna_a_completar]):

            id_dato_faltante.append(row['quotation_ID'])

            if pd.notna(row[columna_backup_1]):
                return row[columna_backup_1]
            
            elif pd.notna(row[columna_backup_2]):
                return row[columna_backup_2]
            
        return row[columna_a_completar]
    
    #Aplicamos la función:
    result =  df.apply(completar, axis=1)

    # Imprimo los ID conflictivos:
    print(f"🔍❌Ids con dato faltante: '{len(id_dato_faltante)}' \n {id_dato_faltante}")

    return result



def cargar_y_procesar_ds(ruta_archivo="ds.xlsx"):
    """Carga y procesa el archivo Deal Specialist.

    Args:
        ruta_archivo (str): Ruta al archivo Excel. Por defecto: "ds.xlsm"

    Returns:
        pd.DataFrame: DataFrame procesado y listo para análisis.
    """

    ds = pd.read_excel(ruta_archivo, index_col=0)

    #Limpieza de columnas:
    ds.columns = ds.columns.str.strip() 
    ds.rename(columns = {'Unnamed: 1': 'quotation_ID'}, inplace = True)

    # Completar 'Main Access Currency' (OJO🔍 REVISAR CON ANTONIO CUANDO YA TENGAMOS DATOS COMPLETOS)
    #quitar cuando sepamos de dónde viene el problema
    ds['Main Access Currency'] = completing_currency(
        df = ds,
        columna_a_completar = 'Main Access Currency',
        columna_backup_1 = 'Back Up Maintenance Currency',
        columna_backup_2 = 'Main Maintenance Currency')
    
    #Formateo de columnas:
    ds['Main Access Currency'] = ds['Main Access Currency'].str.lower().str.strip()
    ds['City'] = ds['City'].str.title()
    ds['Country'] = ds['Country'].str.title().str.replace('_', ' ').str.replace('Brasil', 'Brazil')

    #Columna nueva para identificar el origen
    ds['Source'] = 'Deal Specialist'

    # Normalizamos los proveedores conocidos:
    ds['Main Access Provider (last mile Provider)']= ds['Main Access Provider (last mile Provider)'].str.replace('Telefonica_Chile_S.A._(Mayorista)', 'Telefonica Chile S.A.').str.replace('INTELIGLOBE', 'Inteliglobe').str.replace("_", " ")

    #Creamos la columna Full contract Value:
    ds['FCV'] = ds['Main Access NRC'] + (ds['Contract Term (month)']* ds['Main Access MRC'])

    # Extraemos commercial Model
    ds['Commercial_Model']= ds['Comments VPN Site Info\n/Commercial Model'].str.split(' ', expand = True).get(0)

    # Ordenar por 'Option ID' y resetear índice
    ds.sort_values(by='Option ID', ascending=True, inplace=True)  
    
    #Cremos una nueva columna de índice 'id' y renombramos columnas
    ds = ds.reset_index(drop=True) #eliminamos el índice inicial de pandas
    ds = ds.reset_index().rename(columns = {'index': 'id'})

    return ds


def cargar_y_procesar_pe (ruta_archivo = "pe.csv"):
    """Carga y procesa el archivo csv generado por el Pricing Engine

    Args:
        ruta_archivo (str): Ruta al archivo CSV. Por defecto: "pe.csv"

    Returns:
        pd.DataFrame: DataFrame procesado y listo para análisis.
    """

    pe = pd.read_csv(ruta_archivo, sep=';')

    #Limpieza de columnas:
    pe.columns = pe.columns.str.strip() 

    #Generamos el ID único a partir de otras celdas:
    pe['quotation_ID'] = pe['unique_id'].str.split(' ', expand = True).get(2).str.split('_', expand = True).get(0)
    
    
    #Formateo de columnas:
    pe['main_access_currency_cd'] = pe['main_access_currency_cd'].str.lower().str.strip()
    pe['country_name'] = pe['country_name'].str.replace('_', ' ')
    pe['Source'] = 'Pricing Engine' #creamos una columna
    
    # Normalizamos los proveedores conocidos:
    pe['main_access_provider_name'] = pe['main_access_provider_name'].str.replace('Telefonica_Empresas_Chile_S.A.','Telefonica Chile S.A.').str.replace('Inteliglobe_Communications_USA', 'Inteliglobe').str.replace("_", " ")

    #Creamos la columna Full contract Value
    pe['FCV'] = pe['main_access_nrc_amt'] + (pe['contract_term_cd']* pe['main_access_mrc_amt'])

    # Extraemos commercial Model
    pe['Commercial_Model'] = pe['vpn_site_comments_des'].str.split(' ', expand = True).get(0)

    #Ordenar por 'Option ID' y resetear índice
    pe.sort_values(by='option_id', ascending=True, inplace=True) 

    #Cremos una nueva columna de índice 'id' y renombramos columnas
    pe = pe.reset_index(drop=True) 
    pe = pe.reset_index().rename(columns = {'index': 'id'})

    return pe


def rename_columns(df, suffixe_df):
    """Renombrar columnas con el formato deseado, añadiendo un sufijo para saber de qué tabla original proviene.

    Args:
        df (df): DataFrame el cual queremos renombrar las columnas.
        suffixe_df (str): sufijo que añadiremos al nombre de cada columna.
    """
    
    list_columns = df.columns
    list_columns_rename = []

   #Automatically giving the column name: 
    for col in list_columns:
        col = col.replace(' ', '_')
        col_rename = col + '_' + suffixe_df
        list_columns_rename.append(col_rename)
    
    #Automatic dictionary creation for name change:
    dict_names = dict(zip(list_columns, list_columns_rename))

    #Renaming columns:
    return df.rename(columns = dict_names)



name_to_iso = {
    # América Latina
    "argentine peso": "ARS",
    "bolivian boliviano": "BOB",
    "brazilian real": "BRL",
    "chilean peso": "CLP",
    "colombian peso": "COP",
    "costa rican colon": "CRC",
    "cuban peso": "CUP",
    "dominican peso": "DOP",
    "east caribbean dollar": "XCD",
    "guatemalan quetzal": "GTQ",
    "honduran lempira": "HNL",
    "jamaican dollar": "JMD",
    "mexican peso": "MXN",
    "nicaraguan córdoba": "NIO",
    "panamanian balboa": "PAB",
    "paraguayan guarani": "PYG",
    "peruvian sol": "PEN",
    "trinidad and tobago dollar": "TTD",
    "uruguayan peso": "UYU",
    "venezuelan bolívar": "VES",

    # Otras divisas comunes para completar
    "us dollar": "USD",
    "dollar": "USD",
    "canadian dollar": "CAD",
    "euro": "EUR",
    "british pound": "GBP",
    "japanese yen": "JPY",
    "chinese yuan": "CNY",
    "south korean won": "KRW",
    "indonesian rupee": "IDR"
}



def fcv_currency_or_multicurrency(df, col_currency_req,
                                      col_currency_ds, col_val_ds,
                                      col_currency_pe, col_val_pe,
                                      diccionario):
    """
    Analiza el Full Contract Value de cada quotation en distintas divisas, realizando conversiones a la moneda de referencia (moneda del Request B-End),
    y calcula diferencias porcentuales entre el FCV calculado por el Deal Specialist y el FCV del Pricing Engine. 
    También verifica si las divisas están cubiertas por el diccionario ISO. Habrá que completarlo en el caso de que las divisas no lo estén.

    Args:
        - df (pd.DataFrame): DataFrame con los datos unificados de las tres fuentes: Request B-end, Deal specialist y Pricing Engine.
        - columnas_divisa (list): Lista con los nombres de las columnas de divisas a verificar.
        - col_id (str): número id de cada quotation que une las 3 fuentes (B-end, DS, PE).
        - col_currency_req (str): Columna con la divisa de referencia para la quotation (Request B-End).
        - col_currency_ds (str): Columna de divisa del Deal Specialist.
        - col_val_ds (str): Columna con el PCV del DS.
        - col_currency_pe (str): Columna de divisa del Pricing Engine.
        - col_val_pe (str): Columna con el PCV del PE.
        - diccionario (dict): Diccionario con las equivalencias 'nombre de divisa' → 'código ISO' (ej. "euro" → "EUR").

    Returns:
        - pd.DataFrame: DataFrame con valores convertidos, tasas de cambio y delta %.
    """

    # PASO 1: Verificar si las divisas existen en el diccionario
    columnas_divisa = [col_currency_req, col_currency_ds, col_currency_pe]
    todas_divisas = set()
    for col in columnas_divisa:
        if col in df.columns:
            divisas = df[col].dropna().unique()
            todas_divisas.update(divisas)

    print("🔍 Revisión de nombres de divisa encontrados:\n")
    for divisa in sorted(todas_divisas):
        clave = divisa.strip().lower()
        if clave in diccionario:
            print(f" ✅'{clave}' → {diccionario[clave]}")
        else:
            print(f"❌'{clave}' → ❗ FALTA en el diccionario de divisas")


    # PASO 2: Configurar caché para no repetir llamadas a la API
    cache_tipo_cambio = {}

    def name_to_iso(nombre_divisa):
        """Convierte un nombre de divisa en texto (por ejemplo, 'euro', 'dollar') a su correspondiente código ISO de tres letras 
        (por ejemplo, 'EUR', 'USD'), utilizando un diccionario de mapeo previamente definido. Funcionamiento:
            1. Convierte el nombre a minúsculas.
            2. Elimina espacios en blanco al inicio y final.
            3. Busca el valor en el diccionario `diccionario`.
            4. Devuelve el código ISO si lo encuentra, o None si no existe.

        Args:
            nombre_divisa (str): nombre de la divisa (no estándarizado). Ejemplos: "Euro", " dollar ", "CANADIAN DOLLAR"

        Returns:
            str or None: Código ISO. Devuelve None si la divisa no está en el diccionario.
        """
        return diccionario.get(str(nombre_divisa).strip().lower(), None)

    def obtener_tasa_cambio(origen, destino):
        """Dado un par de monedas (ej.: "USD" a "EUR") esta función:
            (1) Consulta la API FXRatesAPI para saber el tipo de cambio actual.
            (2) Guarda los resultados en memoria temporal (cache_tipo_cambio) para no repetir la llamada en caso de que se repita el par de currencies para los que necesitamos conversión.
            (3) Devuelve el exchange rate para que luego se use en la conversión de "presupuestos".

        Args:
            origen (str): código de divisa origen (ej.: "USD")
            destino (str): código de divisa destino (ej.: "EUR")

        Returns:
            float: tipo de cambio obtenido de la API. Lo aplicamos con un ejemplo:
                    Ej. obtener_tasa_cambio("USD", "EUR")  output--> 0.8672701405
        """

        #CASO 1: no se necesita conversión
        if origen == destino:
            return 1
        
        #CASO 2: se necesita conversión y tenemos almacenado en el caché el tipo de cambio
        par = (origen, destino) #Guardamos el par de divisas como una tupla (ej.: ("USD", "EUR")).
        if par in cache_tipo_cambio: #Verificamos si ya tenemos esa conversión guardada (cache)
            return cache_tipo_cambio[par]  #Si ya lo hemos consultado antes, devolvemos el exchange rate desde el diccionario cache_tipo_cambio. Esto ahorra muchas llamadas a la API.
        
        #CASO 3: Llamamos a la API si no encuentra el tipo de cambio en el cache
        url = f"https://api.fxratesapi.com/convert?from={origen}&to={destino}&format=json"
        
        try:
            r = requests.get(url, timeout=10) ##Esperamos un máximo de 10 segundos evitando que el script se quede colgado indefinidamente si el servidor no responde.
            if r.status_code == 200:

                data = r.json() #convertimos la respuesta exitosa a un dict de Python (JSON)
                tasa = data.get("info", {}).get("rate", None) #Extraemos del JSON el valor del tipo de cambio (que está en "info": {....., "rate": 0.923421},) Si no existe, nos da None.
                cache_tipo_cambio[par] = tasa #Guardamos la tasa en el cache para futuros usos
                
                return tasa
        
        #CASO 4: Si hay algún error (red, timeout, etc.), lo imprime y devuelve None.
        except Exception as e:
            print(f"Error al obtener tipo de cambio {origen} --> {destino}: {e}")
        
        return None


    def convertir(valor, origen, destino):
        """convertimos un valor monetario de una divisa a otra, usando una tasa de cambio obtenida previamente de la API (y cacheada para eficiencia).

        Args:
            valor (float): importe que se quiere convertir (ej. 100)
            origen (str): Código ISO de la moneda del valor original (ej. "USD")
            destino (str): ódigo ISO de la moneda a la que se quiere convertir (ej. "EUR")

        Returns:
            tuple: Devuelve una tupla con (el valor convertido , la tasa de cambio utilizada). 
                    Ej. convertir(100, 'USD', 'EUR') 
                    Supongamos que obtener_tasa_cambio (PASO ANTERIOR) devuelve 0.92 --> resultado convertir(100, 'USD', 'EUR') --> (92.0, 0.92)
        """
        #CASO 1: si alguno de los tres parámetros es None, no se podrá hacer la conversión
        if valor is None or origen is None or destino is None:
            return None, None
        
        #CASO 2: cuando sí podemos obteber la conversión:
        tasa = obtener_tasa_cambio(origen, destino)
        valor_convertido = valor * tasa if tasa else None #Si la tasa es válida (no None), se multiplica por el valor original. Si no hay tasa, el resultado es None.
        return valor_convertido, tasa #Devuelve una tupla: el valor convertido y la tasa de cambio utilizada


    def identificar_cambio_divisa(exchange_rate):
        """Creamos una nueva columna identificando si la divisa utilizada por el Deal Specialist y por el Pricing Engine es la misma que la requerida en el Request B-End.

        Args:
            exchange_rate (float or None): Tipo de cambio aplicado entre las dos monedas

        Returns:
            str: Tenemos 3 posibilidades:
                (1) "no currency available" --> Si el tipo de cambio es NaN (no disponible)
                (2) "same currency as B-end" --> Las divisas son iguales (porque el tipo de cambio = 1).
                (3) "different currency as B-end" --> Las divisas son diferentes, porque el tipo de cambio es distinto de 1.
        """
        if pd.isna(exchange_rate):
            return "no currency available"
        elif exchange_rate == 1:
            return "same currency as B-end"
        else:
            return "different currency as B-end"



    # PASO 3: Aplicar lógica de conversión
    df = df.copy()

    #1) llamamos a la función name_to_iso para convertir la divisa a Código ISO para poder hacer la llamada a la API
    df['currency_ISO_req'] = df[col_currency_req].apply(name_to_iso)
    df['currency_ISO_ds'] = df[col_currency_ds].apply(name_to_iso)
    df['currency_ISO_pe'] = df[col_currency_pe].apply(name_to_iso)

    # llamamos a la función convertir(FCV, divisa_origen, divisa_destino) para convertir los FCV del DS y PE en la divisa de referencia (=la del Request B-End). Aquí estamos haciendo llamamiento a la API
    #2) Guardamos el FCV en la divisa de referencia:
    df['FCV_ds_conv'] = df.apply(lambda row: convertir(row[col_val_ds], row['currency_ISO_ds'], row['currency_ISO_req'])[0], axis=1)
    df['FCV_pe_conv'] = df.apply(lambda row: convertir(row[col_val_pe], row['currency_ISO_pe'], row['currency_ISO_req'])[0], axis=1)

    #3) Guardamos el tipo de cambio aplicado por si necesitamos recurrir a él:
    df['FCV_ds_exchange_rate'] = df.apply(lambda row: convertir(row[col_val_ds], row['currency_ISO_ds'], row['currency_ISO_req'])[1], axis=1)
    df['FCV_pe_exchange_rate'] = df.apply(lambda row: convertir(row[col_val_pe], row['currency_ISO_pe'], row['currency_ISO_req'])[1], axis=1)

    #4) Cálculo de delta:(Valor actual - Valor de referencia) / Valor de referencia * 100 o bien Valor actual / Valor de referencia - 1.
    #En este caso, nuestro benchmark es el Deal Specialist
    df['delta PE vs DS'] = ((df['FCV_pe_conv'] / df['FCV_ds_conv']) - 1) * 100

    #5) Reemplazamos los infinitos a 0%. Estos infinitos pueden existir porque el FCV del benchmark (DS) puede ser == 0, entonces al calcular la delta de FCV sale inf:
    df['delta PE vs DS'] = df['delta PE vs DS'].replace([np.inf, -np.inf], 0)

    #6) identificamos si la divisa utilizada por el Deal Specialist y por el Pricing Engine es la misma que la requerida en el Request B-End
    df['same_currency_as_B-End_ds'] = df['FCV_ds_exchange_rate'].apply(identificar_cambio_divisa)
    df['same_currency_as_B-End_pe'] = df['FCV_pe_exchange_rate'].apply(identificar_cambio_divisa)

    return df



def same_commercial_model_quoted (value):
    """función que identifica si ha habido cambios entre el servicio precidado por el PE y los DS en la columna "Comments_VPN_Site_Info\n/Commercial_Model" cuyos dos únicos valores sólo pueden ser B4B y DIA. 
    Esta función compara dos columnas: 
    (1) Commercial_Model_req (antigua columna Comments_VPN_Site_Info\n/Commercial_Model) : columna descriptiva del Commercial Model solicitado en el B-End
    (2) Commercial_Model_ds (antigiua columna Comments_VPN_Site_Info\n/Commercial_Model): columna descriptiva del Commercial Model preciado por los Deal Specialists
    (3) Commercial_Model_pe (antigua columna Comments_VPN_Site_Info\n/Commercial_Model): columna descriptiva del Commercial Model preciado por el Pricing engine

    Args:
        value (string): celda dentro de cada columna, es decir, tipo de servicio preciado por cada agente.

    Returns:
        string: devuelve 
        (1)"No changes": si no ha habido cambio del commercial model
        (2) "PE changed": si quien ha cambiado el commercial model quoted ha sido el Pricing Engine
        (3) "DS changed": si quien ha cambiado el commercial model quoted ha sido el Deal Specialist.
    """
    #Extraemos el tipo de Commercial Model de cada una de las 3 columnas para esta fila (value)
    b_end = value['Commercial_Model_req']
    pe = value['Commercial_Model_pe']
    ds = value['Commercial_Model_ds']

    if b_end == "DIA" or b_end == "B4B":
        #Creamos una lista vacía donde vamos a ir guardando quién cambió el servicio. OJO el PE puede ser distinto al B-end pero también puede serlo el DS.
        cambios = []

        #Si el commercial model del PE es distinto del del B-end --> agregamos mensaje a la lista
        if pe != b_end: 
            cambios.append("PE changed") 

        #Si el commercial model del DS es distinto del del B-end --> agregamos mensaje a la lista
        if ds != b_end: 
            cambios.append("DS changed") 

        #CASO 1: Si la lista sigue vacía --> significa que PE y DS coinciden con B-end --> no hubo cambios en Commercial model
        if not cambios:
            return 'No changes'
        
        #CASO 2: Si hay uno o más cambios --> los unimos con "&" 
        return " & ".join(cambios)

    else: #CASO 3: que no estemos ante un commercail model (B4B o DIA, si no que estemos ante un MPLS, por ejemplo)
        return "Other service quoted (i.e. MPLS)"
    

def preparacion_floats_powerbi (df): 
    """Función para la preparación de datos para el Power BI: cambiando los puntos de todas las columnas con floats por las comas, para que el Power BI lo entienda:

    Args:
        df (DataFrame): DataFrame que queremos hacer someter al cambio.
    """
    for col in df.columns:
        if df[col].dtype == np.float64:
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (int, float)) else x)
            df[col] = df[col].str.replace(".", ",")



def guardar_ruta_csv(nombre_csv, nombre_txt=None):
    """
    Guarda la ruta absoluta del CSV indicado en un archivo .txt auxiliar. La finalidad de este archivo facilitar que los usuarios del ETL puedan saber fácilmente 
    dónde está ubicado el CSV generado, para enlazarlo después en Power BI. Este .txt auxiliar conectaría el CSV con Power BI de manera automática 
    (Power BI sólo funciona con rutas absolutas y no relativas).
    
    Args:
        - nombre_csv (str): Ruta relativa del archivo CSV que quieres generar (por ejemplo: 'output/merged.csv'). OJO, ejecutamos desde main.py.
        - nombre_txt (str, opcional): Ruta relativa del archivo .txt donde guardar la ruta. 
                                    Si no se indica, se generará automáticamente con el mismo nombre base.
                                    
    Ejemplo de uso:
        guardar_ruta_csv('output/merged.csv')               # Genera output/merged_path.txt
        guardar_ruta_csv('output/precios.csv', 'ruta.txt')  # Genera ruta.txt con la ruta absoluta
    """
    
    ruta_csv = os.path.abspath(nombre_csv)
    
    #Si el usuario NO proporciona "nombre_txt" al llamar a la función (es decir, no elige un nombre para el txt) --> el programa genera automáticamente un nombre por defecto.
    if nombre_txt is None: 
        file_name = os.path.basename(nombre_csv) #extraemos sólo el nombre del archivo del csv, sin la carpeta: ej. "output/merged.csv" --> "merged.csv"
        base_name = os.path.splitext(file_name)[0]  #quitamos la extensión.csv, dejándonos solo el nombre base: ej. "merged.csv"--> "merged"
        nombre_txt = f"output/{base_name}_path.txt" #generamos automáticamente el nombre del .txt asociado, usando ese base_name.
    
    #guardamos esa ruta en un archivo auxiliar:
    #Abrimos (o creamos si no existe) un archivo de texto llamado path_to_csv.txt dentro de la carpeta output/
    with open(nombre_txt, "w") as archivo: #"w" significa que lo abre en modo escritura, sobreescribiendo cualquier contenido previo // "archivo" es el archivo abierto donde vamos a escribir la ruta.
        archivo.write(ruta_csv) #Escribe la ruta completa del CSV (output_file) dentro del archivo path_to_csv.txt.
    

    print(f"✅ Ruta guardada: {nombre_txt}, ➡️  Contenido (ruta del CSV): {ruta_csv}")
# %%
