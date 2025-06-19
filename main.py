#%%
from src import transformacion as tr
import pandas as pd
print('✅ Librerías importadas')  


bend = tr.cargar_y_procesar_excel_bend(ruta_archivo = "data\\bend.xlsm")
print('✅ B-end cargado. \n Nos habrá salido un aviso ARRIBA que vamos a ignorar \n ')
bend['Commercial Model'] = bend['Commercial Model'].apply(tr.commercial_model_provided)
bend_summary = bend[['id', 'quotation_ID', 'Source',
                    'Standard Services', 'Site ID', 'Lot', 'City', 'Country', 
                    'Main access speed UpStream (Kbps)', 'Main access speed DownStream (kbps)', 
                    'Main access technology', 'Main Access Guaranteed Bandwidth %', 
                    'Commercial Model','Contract Term (month)', 
                    'Main Access Provider (last mile Provider)', 'Main Access Currency']]



ds = tr.cargar_y_procesar_ds(ruta_archivo = "data\\ds.xlsx")
print('✅ Deal Specialist cargado \n')
ds_summary = ds[['id', 'quotation_ID', 'Source', 
                'Standard Services', 'Site ID', 'Lot', 'City', 'Country', 
                'Main access speed UpStream (Kbps)', 'Main access speed DownStream (kbps)', 
                'Main access technology', 'Main Access Guaranteed Bandwidth %', 
                'Commercial_Model','Contract Term (month)', 
                'Main Access Provider (last mile Provider)', 'Main Access Currency',
                'Main Access NRC', 'Main Access MRC', 'FCV']]




pe = tr.cargar_y_procesar_pe(ruta_archivo = "data\\pe.csv")
print('✅ motor cargado \n ')
pe_summary = pe[['id', 'quotation_ID', 'Source', 
                'standard_services_cd', 'site_id', 'lot_cd', 'city_name', 'country_name',
                'main_access_speed_upstream_kbps_qt', 'main_access_speed_downstream_kbps_qt', 
                'main_access_technology_name', 'main_access_guaranteed_bandwidth_qt', 
                'Commercial_Model', 'contract_term_cd',
                'main_access_provider_name','main_access_currency_cd',
                'main_access_nrc_amt_quoted_by', 'main_access_nrc_amt',
                'main_access_mrc_amt_quoted_by', 'main_access_mrc_amt', 'FCV']]
pe_summary =  pe_summary.rename(columns = {
                                'Source': 'Source',
                                'standard_services_cd': 'Standard Services',
                                'site_id': 'Site ID',
                                'lot_cd': 'Lot',
                                'city_name': 'City',
                                'country_name': 'Country',
                                'main_access_speed_upstream_kbps_qt': 'Main access speed UpStream (Kbps)',
                                'main_access_speed_downstream_kbps_qt': 'Main access speed DownStream (kbps)',
                                'main_access_technology_name': 'Main access technology',
                                'main_access_guaranteed_bandwidth_qt': 'Main Access Guaranteed Bandwidth %',
                                'contract_term_cd': 'Contract Term (month)',
                                'main_access_nrc_amt':'Main Access NRC',
                                'main_access_mrc_amt': 'Main Access MRC',
                                'main_access_provider_name': 'Main Access Provider (last mile Provider)',
                                'main_access_currency_cd': 'Main Access Currency'
                                })


bend_summary = tr.rename_columns(bend_summary, 'req')
ds_summary = tr.rename_columns(ds_summary, 'ds')
pe_summary = tr.rename_columns(pe_summary, 'pe')

df_merged_1 = bend_summary.merge(ds_summary, how = 'left', left_on = 'id_req', right_on = 'id_ds')
df_merged_2 = df_merged_1.merge(pe_summary, how = 'left', left_on = 'id_req', right_on = 'id_pe')


df_merged_final = tr.fcv_currency_or_multicurrency(
    df_merged_2,
    col_currency_req = 'Main_Access_Currency_req',
    col_currency_ds = 'Main_Access_Currency_ds', col_val_ds = 'FCV_ds',
    col_currency_pe = 'Main_Access_Currency_pe', col_val_pe = 'FCV_pe',
    diccionario = tr.name_to_iso
)



df_merged_final['Commercial_model_changes'] = df_merged_final.apply(tr.same_commercial_model_quoted, axis=1)
df_precios = df_merged_final[['id_req', 'Site_ID_req', 'City_req', 'Country_req', 'Commercial_Model_req', 'currency_ISO_req', 'Main_Access_Provider_(last_mile_Provider)_ds', 'FCV_ds_conv', 'same_currency_as_B-End_ds','Commercial_Model_ds','Commercial_Model_pe', 'Main_Access_Provider_(last_mile_Provider)_pe', 'main_access_mrc_amt_quoted_by_pe', 'FCV_pe_conv', 'same_currency_as_B-End_pe', 'Commercial_model_changes', 'delta PE vs DS']]


df_merged_final.to_csv('merged_viz.csv', index = False) #lo guardamos para visualizaciones
print('\n ✅ Archivos transformados para visualizaciones en python')


tr.preparacion_floats_powerbi(df_precios)
tr.preparacion_floats_powerbi(df_merged_final)

df_merged_final.to_csv('merged.csv', index = False)
df_precios.to_csv('precios.csv', index = False)

print('✅ Archivos transformados para visualizaciones en PowerBI')
print('Saldrá otro aviso que tendremos que ignorar')

