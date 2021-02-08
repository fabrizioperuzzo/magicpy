#!/usr/bin/python3.7
##########    form yahoo open close giornaliero (non continuo) #######################
#######         plot trend in aumento su 3 anni e su 3 mesi            ###############

'''
TODO Inserire trend logaritmici per valutare la crescita a lungo termine
TODO Inserire un coefficiente di volatilita per ogni azione

NOTE:
    - richiesto pip install openpyxl per creare exce
    - from iex import reference --> deprecated non utilizzato
    - modo corretto per il path di pythonanywhere:
            project_home = u'/home/magicpy/mysite'
    - for pythonanywhere to use dash modify WSGI file with:
                from yourwebappmodule import app
                application = app.server

'''

import time
import os
import warnings
warnings.filterwarnings('ignore')

#=================  External import =============

import matplotlib.pyplot as plt
import pandas as pd
plt.style.use('ggplot')

#============= internal =========================

from yahoo_scan import Yahoo_Scan
from utils import *



#=================================================================================
#                  *********      START!!!        *********
#=================================================================================

print('START!!!')

print(os.getcwd())
print(os.path.dirname(os.getcwd()))

symb = retrieve_symb_list()
save_pass_list(symb_pass=symb)

######### per test
# symb=['SRPT','CVX']

start_time = time.time()

#=================================================================================
#                                CREA!!!
#=================================================================================
'''
    lancio la classe: Yahoo_Scan
            self.df_all  --> dataframe (ogni riga è una data)
            self.ret_dataframe() --> dataframe (è una sola riga)
            self.df_last     --> same as above but without try/catch: may rise error
            

    il dizionario ist_dict   -->  ist_dict['ist1']
    il dizionario stock_dict -->  stock_dict['OSTK']
    per recuperare il dataframe di una istanza -->  stock_dict['OSTK'].df_all
    il dataframef "df1" è quello con gli indici: una riga per stock
'''
df1 = pd.DataFrame({})
ist_dict = {}
i = 1
removed_list=[]
for stock in symb:
    name_ist = 'ist'+str(i)
    ist_dict[name_ist] = Yahoo_Scan(stock,'01/01/2006','d',name_ist)
    df1 = df1.append(ist_dict[name_ist].ret_dataframe(), sort=False)
    i += 1

#  creo un dizionario veloce con nome stock
stock_dict = {}
for i in ist_dict.keys():
    stock_dict[ist_dict[i].stock] = ist_dict[i]

#=================================================================================





#=================================================================================
#                    CREO DATABASE CONDIZIONALI 3 LIVELLI
#=================================================================================
'''
Creo dei database con delle condizioni per definire vari livelli di scelta:

-  df :  ordino per il massimo drop tra previous Close e Open prendo i primi 15
-  df_best :  prima condizione
-  df_best_sup : seconda condizione
-  df_best_sup_10gg : terza condizione valutata su 10gg
'''



df = df1.copy()

df_best = df[((df.buy3=='YES')&(
    df.buy=='YES')&(
    df.gain>100)&(
    df.slope_x1000>0.00001))]
df_best = df_best.sort_values(by=['gain'])

df_best_sup = df[((
    df.trend == 'RAISING')&(
    df.var_1gg < -4)&(
    df.gain > 100)&(
    df.slope_x1000 > 0.00001))]
df_best_sup = df_best_sup.sort_values(by=['gain'])


df_best_sup_10gg = df[((
    df.trend == 'RAISING')&(
    df.var_10gg < -4)&(
    df.gain > 100)&(
    df.slope_x1000 > 0.00001))]
df_best_sup = df_best_sup.sort_values(by=['gain'])





#===============================================================================
# creo le diverse liste di stock in funzione delle performances
#===============================================================================
'''
symb_pass_list: stock che sono passati (da yahoo)
'''
symb_pass_list = df1.stock.tolist()
symb_pass_good = df_best.stock.tolist()
symb_pass_good_sup = df_best_sup.stock.tolist()
symb_pass_good_sup_10gg = df_best_sup_10gg.stock.tolist()


#===============================================================================
#           SALVO I GRAFICI COME IMMAGINI PNG
#===============================================================================

'''
dal dataframe "df_best" 
ricava i grafici in .png
'''

list1=df_best.sort_values('stock').name_ist.astype(str).tolist()
working_folder = make_folder('./PIC2')
for i in list1:
    plot_ist(i, working_folder, ist_dict)

'''
dal dataframe "df" prende le migliori 15 variazioni in un giorno in negativo
di queste ricava i grafici in .png
'''

list2=df.sort_values('var_1gg').name_ist.astype(str).tolist()[:15]
working_folder = make_folder('./PIC2')
for i in list2:
    plot_ist(i, working_folder, ist_dict)

#===============================================================================


# plotto il tempo che ci ha messo per girare
print("--- %s minutes ---" % ((time.time() - start_time)/60))


#=================================================================
#                      CREATE HTML WORD
#=================================================================


create_word_html(df, df_best, df_best_sup, df_best_sup_10gg)


#=================================================================
#               SAVE FILE EXCEL FEATHER HDF TXT
#=================================================================

export_excel(df, df_best, df_best_sup, df_best_sup_10gg)
export_hdf_feather(ist_dict)
if df1.shape[0]>50: save_pass_list(df=df1)


print('Dati esportati in excel csv e hdf')