#!/usr/bin/python3.7
##########    form yahoo open close giornaliero (non continuo) #######################
#######         plot trend in aumento su 3 anni e su 3 mesi            ###############



# Inserire un coefficiente di volatilità
# Inserire trend logaritmici ed esponenziali per valutare la crescita


from threading import Thread
import time
import pandas_datareader.data as web
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import time
from datetime import datetime
import matplotlib.pyplot as plt
#from iex import reference
import datetime as dt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
plt.style.use('ggplot')
import sys
import os
import shutil
#%matplotlib inline
import warnings
warnings.filterwarnings('ignore')
import mammoth
#pip3.7 install --user python-docx
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pickle
import h5py
import dateutil.relativedelta
import dateutil.relativedelta as datdelta


###  Import the external Class and functions
from yahoo_scan import Yahoo_Scan
from retrieve_symb import retrieve_symb_list
#

print('START!!!')

print(os.getcwd())
print(os.path.dirname(os.getcwd()))

symb = retrieve_symb_list()


#################################################################################################################
#######################################               START           ###########################################
#################################################################################################################
#################################################################################################################




start_time = time.time()


#########    CREA!!!!!          ###################
#**************************************************

df1 = pd.DataFrame({})
ist_dict = {}
i = 1
removed_list=[]
for stock in symb:
    name_ist = 'ist'+str(i)
    ist_dict[name_ist] = Yahoo_Scan(stock,'01/01/2006','d',name_ist)
    df1 = df1.append(ist_dict[name_ist].ret_dataframe(), sort=False)
    i += 1

#######  il dizionario ist_dict è quello con tutte le istanze
#######  il df "df1" è quello con gli indici: una riga per stock


##################################################################################



## CREO UN DIZIONARIO CON I NOMI DELLE ISTANZE ANZICHE IL NUMERO

stock_dict = {}

for i in ist_dict.keys():
    #print(i)
    #print(ist_dict[i].stock)

    stock_dict[ist_dict[i].stock] = ist_dict[i]

    # IL FILE CREATO E TROPPO GRANDE PER PYTHONANYWHERE
    #ist_dict[i].df_all.to_hdf('df_alltogheter.h5', key=ist_dict[i].stock)














##################################################################################


#######    database di output       ##########
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


#  creo lista con tutti gli stock che sono passati (che sono stati letti da yahoo) e aggiorno il file

symb_pass_list = df1.stock.tolist()

try:
    with open('symb.txt',"wb") as rb:
        pickle.dump(symb_pass_list, rb)
except:
    pass

# creo le diverse liste di stock in funzione delle performances


symb_pass_good = df_best.stock.tolist()
symb_pass_good_sup = df_best_sup.stock.tolist()
symb_pass_good_sup_10gg = df_best_sup_10gg.stock.tolist()


symb= df_best.stock.tolist()




####  SALVO I RISULTATI IN UN FILE #######################

# necessario from pandas import ExcelWriter
# richiede anche pip3 install openpyxl


nomedir = './{}'.format('DATA')
if os.path.exists(nomedir): shutil.rmtree(nomedir)
if not os.path.exists(nomedir): os.makedirs(nomedir)

nomefile= nomedir +'/'+ (str(dt.date.today())) + "best.csv"
export_csv = df.to_csv (nomefile, header=True, sep=';')

try:
    nomefile= nomedir +'/'+ (str(dt.date.today())) + "_best.xlsx"
    writer = pd.ExcelWriter(nomefile)


    df.sort_values('var_1gg').to_excel(writer,'data')
    writer.save()

    df_best.sort_values('var_1gg').to_excel(writer,'best')
    writer.save()

    df_best_sup.sort_values('var_1gg').to_excel(writer,'best_sup')
    writer.save()

    df_best_sup_10gg.sort_values('var_1gg').to_excel(writer,'best_sup_10gg')
    writer.save()
except:
    print("close the file xls")



def plot_ist(ist_in, working_folder):

    ist_corr = ist_dict[ist_in]

    plt.rcParams['figure.figsize'] = 18,5

    f = plt.figure()    # se uso questo non ho piu bisogno di inportare Figure
    a = f.add_subplot(111)

    a = plt.subplot2grid((9, 4), (0, 0), rowspan=5, colspan=4)
    a2 = plt.subplot2grid((9, 4), (5, 0), rowspan=2, colspan=4, sharex=a)
    a3 = plt.subplot2grid((9, 4), (7, 0), rowspan=2, colspan=4, sharex=a)


    a.plot(ist_corr.df_all.index,ist_corr.df_all.Close, label="price", linestyle='-', linewidth=1, color='b')
    a.plot(ist_corr.xt,ist_corr.y_c_pred, linestyle='--', color='r')
    a.plot(ist_corr.xt,ist_corr.y_pred_h, linestyle='--', color='gray')
    a.plot(ist_corr.xt,ist_corr.y_pred_l, linestyle='--', color='gray')

    a2.fill_between(ist_corr.df_all.index,ist_corr.df_all.Volume, 0)

    a3.plot(ist_corr.xt,ist_corr.df_all.macd)
    a3.plot(ist_corr.xt,ist_corr.df_all.signal)
    a3.bar(ist_corr.df_all.index,ist_corr.df_all.histogram,width = 3)

    a.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    plt.setp(a.get_xticklabels(), visible=False)
    plt.setp(a2.get_xticklabels(), visible=False)

    a.set_title(ist_corr.stock+' Max gain:'+
                str(ist_corr.df_last.gain.tolist()[0])+
                str('\$')+"  average gain: "+str(ist_corr.df_last.gain_ave.tolist()[0])+
                str('\$'))

    nomefile= working_folder + "/" + (str(dt.date.today())) + ist_corr.stock +".png"
    plt.savefig(nomefile)

    a.clear


# creo lista delle istanze best, plotto e salvo i file in PIC

list1=df_best.sort_values('stock').name_ist.astype(str).tolist()
working_folder = './{}'.format('PIC')
if os.path.exists(working_folder): shutil.rmtree(working_folder)
if not os.path.exists(working_folder): os.makedirs(working_folder)
for i in list1:
    plot_ist(i, working_folder)

# creo lista con tutte le istanze, plotto e salvo i file in PIC

list2=df.sort_values('var_1gg').name_ist.astype(str).tolist()[:15]
working_folder = './{}'.format('PIC2')
if os.path.exists(working_folder): shutil.rmtree(working_folder)
if not os.path.exists(working_folder): os.makedirs(working_folder)
for i in list2:
    plot_ist(i, working_folder)



# plotto il tempo che ci ha messo per girare
print("--- %s minutes ---" % ((time.time() - start_time)/60))


###############################################################################################################
################################    DOC WORD  AND HTML ########################################################
###############################################################################################################

document = Document ()

document.add_heading ( 'Buongiorno Fabrizio!\n the best Trade updated '+ str(dt.datetime.now()).split(".")[0] +'\n are ready!!!', level = 1 )


document.add_heading ( 'All The best trade' , level = 2 )

df_dall = df[['trend3m','trend','gain','stock','slope_x1000','name_ist','var_10gg','var_1gg']].sort_values('var_1gg')

t = document.add_table(df_dall.shape[0]+1, df_dall.shape[1])

# add the header rows.
for j in range(df_dall.shape[-1]):
    t.cell(0,j).text = df_dall.columns[j]

# add the rest of the data frame
for i in range(df_dall.shape[0]):
    for j in range(df_dall.shape[-1]):
        t.cell(i+1,j).text = str(df_dall.values[i,j])



document.add_heading ( 'The best trade' , level = 2 )

df_db = df_best[['trend3m','trend','gain','stock','slope_x1000','name_ist','var_10gg','var_1gg']].sort_values('stock')

t = document.add_table(df_db.shape[0]+1, df_db.shape[1])

# add the header rows.
for j in range(df_db.shape[-1]):
    t.cell(0,j).text = df_db.columns[j]

# add the rest of the data frame
for i in range(df_db.shape[0]):
    for j in range(df_db.shape[-1]):
        t.cell(i+1,j).text = str(df_db.values[i,j])



document.add_heading ( 'The best trade at 1gg' , level = 2 )

df_dbs = df_best_sup[['trend3m','trend','gain','stock','slope_x1000','name_ist','var_10gg','var_1gg']].sort_values('stock')

t = document.add_table(df_dbs.shape[0]+1, df_dbs.shape[1])

# add the header rows.
for j in range(df_dbs.shape[-1]):
    t.cell(0,j).text = df_dbs.columns[j]

# add the rest of the data frame
for i in range(df_dbs.shape[0]):
    for j in range(df_dbs.shape[-1]):
        t.cell(i+1,j).text = str(df_dbs.values[i,j])




document.add_heading ( 'The best trade at 10gg' , level = 2 )

df_dbs10 = df_best_sup_10gg[['trend3m','trend','gain','stock','slope_x1000','name_ist','var_10gg','var_1gg']].sort_values('stock')

t = document.add_table(df_dbs10.shape[0]+1, df_dbs10.shape[1])

# add the header rows.
for j in range(df_dbs10.shape[-1]):
    t.cell(0,j).text = df_dbs10.columns[j]

# add the rest of the data frame
for i in range(df_dbs10.shape[0]):
    for j in range(df_dbs10.shape[-1]):
        t.cell(i+1,j).text = str(df_dbs10.values[i,j])



###############  PICTURES ###############################

document . add_page_break ()

paragraph = document.add_paragraph()
paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

document.add_heading ( 'Today highest drop start' , level = 2 )


#
files = []
filespath = []
# r=root, d=directories, f = files
for r, d, f in os.walk('./PIC2'):
    for file in f:
        if '.png' in file:
            files.append(file)
            filespath.append(os.path.join(r, file))

for file in files:
    document . add_picture ( './PIC2/'+file , width = Inches (7))

last_paragraph = document.paragraphs[-1]
last_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT


















document . add_page_break ()

paragraph = document.add_paragraph()
paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

document.add_heading ( 'The best trade graphs' , level = 2 )


#
files = []
filespath = []
# r=root, d=directories, f = files
for r, d, f in os.walk('./PIC'):
    for file in f:
        if '.png' in file:
            files.append(file)
            filespath.append(os.path.join(r, file))


for file in files:
    document . add_picture ( './PIC/'+file , width = Inches (7))



last_paragraph = document.paragraphs[-1]
last_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT




document.save ( 'todaytrade.docx' )



f = open("todaytrade.docx", 'rb')
prev_folder = os.path.dirname(os.getcwd())
temp_folder = os.path.join(prev_folder,"mysite","templates","todaytrade.html")
print('Save html file in: ', temp_folder)
b = open(temp_folder, 'wb')
document = mammoth.convert_to_html(f)
b.write(document.value.encode('utf8'))
f.close()
b.close()