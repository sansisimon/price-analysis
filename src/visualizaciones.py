import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests


def generar_boxplot_delta(df, columna="delta PE vs DS", save_path=None, show_plot=True):
    """
    Genera un boxplot de la columna indicada, imprime estadísticas principales y
    opcionalmente guarda el gráfico en un archivo.

    Parámetros:
    ----------
    - df (pd.DataFrame): DataFrame con los datos
    - columna (str): Nombre de la columna numérica para analizar
    - save_path (str or None): Ruta donde guardar el gráfico si se desea. Si es None, no se guarda.
    - show_plot (bool): Si True, muestra el gráfico por pantalla.
    """

    # Creamos figura
    plt.figure(figsize=(12, 4))
    sns.boxplot(x = "delta PE vs DS", 
                data = df, 
                width = 0.5, 
                color = "turquoise",
                capprops={'color':'purple'}) # para cambiar el color de los bigotes)

    # cambiamos el nombre de los ejes usando los métodos
    plt.title('Delta % = (FCV Pricing Engine / FCV Deal Specialist - 1) * 100', fontsize = 10, color= '#14213d')
    plt.ylabel("Distribución de la Delta %", fontsize = 9)
    plt.xlabel("delta %",  fontsize = 9)

    # Cálculo de estadísticos
    q1 = round(np.quantile(df['delta PE vs DS'], 0.25), 2)
    q3 = round(np.quantile(df['delta PE vs DS'], 0.75), 2)
    ric = q3 - q1
    limite_inferior = q1 - 1.5 * ric
    limite_superior = q3 + 1.5 * ric

    #Prints:
    print("💡Estadísticas principales💡: \n")
    print(f"- Mediana = {round(df['delta PE vs DS'].median(),2)} % ➡️ línea dentro del recuadro")
    print(f"- Q1 (25%) = {q1} % ➡️ borde inferior de la Caja" )
    print(f"- Q3 (75%) = {q3} % ➡️ borde superior de la Caja\n" )
    print(f"Rango Intercuartílico (entre Q1 y Q3): {ric}")
    print('-'* 50)
    print(f"- Bigotes de la caja: valores máximos (bigote de arriba) y mínimos (abajo) excluyendo outliers (valores atípicos 🫧 = burbujas )")
    print(f"    + Bigote de arriba = {limite_superior}")
    print(f"    + Bigote de abajo = {limite_inferior}")
    print(f"        - Los bigotes se extienden 1,5 veces por encima y por debajo de Q3 y Q1, respectivamente.")
    print(f"        - Por ello, habrá que estudiar los outliers tomando como inicio el dato de los bigotes.")

    # Ajustar el espaciado entre subplots
    plt.tight_layout();

    # Guardar si se solicita
    if save_path:
        plt.savefig(save_path, 
                        dpi=300, #Resolución (dots per inch). 300 dpi --> alta calidad
                        bbox_inches='tight') #Ajusta los bordes para que el gráfico ocupe el menor espacio posible.
        print(f"📁 Gráfico guardado en: {save_path}")

    # Mostrar si se solicita
    if show_plot:
        plt.show()
    else:
        plt.close()




def separar_outliers(df, columna):
    """
    Calcula los outliers y separa el DataFrame en dos: con outliers y sin outliers.
    
    Args:
        - df (pd.DataFrame): DataFrame a procesar.
        - columna (str): Nombre de la columna numérica para el análisis.

    Returns:
        dict: Contiene:
            - 'outliers': DataFrame con los outliers
            - 'sin_outliers': DataFrame sin los outliers
            - 'q1': Primer cuartil
            - 'q3': Tercer cuartil
            - 'ric': Rango intercuartílico
            - 'limite_inferior': Límite inferior de outliers
            - 'limite_superior': Límite superior de outliers
    """
    
    q1 = round(np.quantile(df[columna], 0.25), 2)
    q3 = round(np.quantile(df[columna], 0.75), 2)
    ric = q3 - q1
    limite_inferior = q1 - 1.5 * ric
    limite_superior = q3 + 1.5 * ric
    
    outliers = df[(df[columna] < limite_inferior) | (df[columna] > limite_superior)]
    sin_outliers = df[(df[columna] >= limite_inferior) & (df[columna] <= limite_superior)]
    
    return {
        'outliers': outliers,
        'sin_outliers': sin_outliers,
        'q1': q1,
        'q3': q3,
        'ric': ric,
        'limite_inferior': limite_inferior,
        'limite_superior': limite_superior
    }





def visualizar_outliers(df, limite_inferior, limite_superior, columna='delta PE vs DS', save_path=None):
    """
    Visualiza un histograma de los outliers de una columna.
    """

    plt.figure(figsize=(10, 3))
    plt.title('Distribución de la Delta de los Outliers', fontsize=10, color='#14213d')
    plt.xlabel("Delta % = (FCV Pricing Engine / FCV Deal Specialist - 1) * 100", fontsize=8)
    plt.ylabel("Nº cotizaciones", fontsize=9)
    plt.grid(axis='y', alpha=0.5) #el alpha mide la transparencia del grid

    sns.histplot(x = columna,
                 data = df,
                 bins = 'auto',
                 color = '#34a0a4')

    print("🚨 OUTLIERS = Valores que quedan fuera de los bigotes")
    print(f"    🔍 Datos en intervalo SUPERIOR ({limite_superior}, {round(df[columna].max(),2)}): {df[df[columna] >= limite_superior].shape[0]} cotizaciones")    
    print(f"    🔍 Datos en intervalo INFERIOR ({limite_inferior}, {round(df[columna].min(),2)}): {df[df[columna] <= limite_inferior].shape[0]} cotizaciones")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, 
                    dpi=300, 
                    bbox_inches='tight')

    plt.show()







def viz_delta_vs_tipo_servicio(df_completo, df_outliers, df_sin_outliers,
                                 col_delta='delta PE vs DS', col_servicio='Lot_pe',
                                 col_com_model='Commercial_Model_req', col_source='main_access_mrc_amt_quoted_by_pe',
                                 save_path=None):
    """
    Genera un gráfico comparativo de la distribución del delta % vs tipo de servicio.
    
    Args:
        - df_completo: DataFrame con todos los datos
        - df_outliers: DataFrame con los outliers
        - df_sin_outliers: DataFrame sin outliers
        - col_delta: Nombre de la columna del delta
        - col_servicio: Nombre de la columna del tipo de servicio (ej ['Internet Bk' 'Internet Ppal' 'MPLS'])
        - col_com_model: Columna para la leyenda del primer gráfico--> Commercial_Model_req (ej.'B4B' 'DIA' 'MPLS')
        - col_source: Columna para la leyenda de los otros 2 gráficos: fuente de datos del motor (APIs, Costbook o Regressor)
        - save_path: Ruta para guardar el gráfico (opcional)
    """
    #configuramos la figura:
    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(20, 5))

    # Información básica
    print("❓❓❓¿En qué tipo de servicio está el Outlier?❓❓❓")
    print(f"- LOT: {df_completo[col_servicio].unique()}")
    print(f"- Commercial Model: {df_completo[col_com_model].unique()}")

    plt.suptitle(" Comparativa en torno al delta del FCV \n Delta % = (FCV Pricing Engine / FCV Deal Specialist - 1) * 100",
                 fontsize=12, color='#14213d')

    # PLOT 1: Todos los datos + hue por Commercial Model
    sns.stripplot(x=col_servicio, 
                    y=col_delta, 
                    hue=col_com_model,
                    palette='Set2', 
                    data=df_completo, 
                    ax=axes[0])
    axes[0].set_title("1. Relación Delta - tipo de servicio \n (TODOS LOS DATOS)", color='grey')
    axes[0].set_xlabel(""); axes[0].set_ylabel("delta %")
    axes[0].spines['right'].set_visible(False); axes[0].spines['top'].set_visible(False)
    axes[0].get_legend().set_title('')

    # PLOT 2: Todos los datos + hue por precio
    sns.stripplot(x=col_servicio, 
                    y=col_delta, 
                    hue=col_source,
                    palette='Set1', 
                    data=df_completo, 
                    ax=axes[1])
    axes[1].set_title("2. Relación Delta - tipo de servicio \n (TODOS LOS DATOS)", color='grey')
    axes[1].set_xlabel(""); axes[1].set_ylabel("delta %")
    axes[1].spines['right'].set_visible(False); axes[1].spines['top'].set_visible(False)
    axes[1].get_legend().set_title('')

    # PLOT 3: Sólo datos sin outliers
    sns.stripplot(x=col_servicio, 
                    y=col_delta, 
                    hue=col_source,
                    palette='Set1', 
                    data=df_sin_outliers, 
                    ax=axes[2])
    axes[2].set_title("3. Relación Delta - tipo de servicio \n (DATOS SIN OUTLIERS)", color='grey')
    axes[2].set_xlabel(""); axes[2].set_ylabel("delta %")
    axes[2].spines['right'].set_visible(False); axes[2].spines['top'].set_visible(False)
    axes[2].get_legend().set_title('')

    # PLOT 4: Sólo outliers
    sns.stripplot(x=col_servicio, 
                    y=col_delta, 
                    hue=col_source,
                    palette='Set1', 
                    data=df_outliers, 
                    ax=axes[3])
    axes[3].set_title("4. Relación Delta - tipo de servicio \n (SÓLO OUTLIERS)", color='grey')
    axes[3].set_xlabel(""); axes[3].set_ylabel("delta %")
    axes[3].spines['right'].set_visible(False); axes[3].spines['top'].set_visible(False)
    axes[3].get_legend().set_title('')

    # Misma escala en todos los ejes Y
    minimo = df_completo[col_delta].min()
    maximo = df_completo[col_delta].max()
    for ax in axes:
        ax.set_ylim(minimo - 50, maximo + 50)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()

