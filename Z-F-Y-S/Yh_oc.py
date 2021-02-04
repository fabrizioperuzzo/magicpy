#!/usr/bin/python3.7
##########    form yahoo open close giornaliero (non continuo) #######################
#######         plot trend in aumento su 3 anni e su 3 mesi            ###############



# Inserire un coefficiente di volatilità
# Inserire trend logaritmici ed esponenziali per valutare la crescita


from threading import Thread
import time
from datetime import datetime
import datetime as dt
import sys
import os
import shutil
import warnings
warnings.filterwarnings('ignore')




## External import
## richiesto pip install openpyxl per creare excel
#from iex import reference
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas_datareader.data as web
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
#pip3.7 install --user python-docx
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import h5py
import dateutil.relativedelta
import dateutil.relativedelta as datdelta
import feather
plt.style.use('ggplot')


###  Import the external Class and functions
from yahoo_scan import Yahoo_Scan
from utils import *
#

print('START!!!')

print(os.getcwd())
print(os.path.dirname(os.getcwd()))

symb = retrieve_symb_list()
save_pass_list(symb_pass=symb)

######### per test
symb=['SRPT','CVX']


#=================================================================================
#                  *********      START!!!        *********
#=================================================================================

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
#                              CREO DATABASE DI OUTPUT
#=================================================================================

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