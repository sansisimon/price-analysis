#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
#pip install openpyxl
pd.set_option('display.max_columns', None)
#%%

from src import transformacion as tr

print('librerías importadas')       
# %%
bend = cargar_y_procesar_excel_bend()

# %%
