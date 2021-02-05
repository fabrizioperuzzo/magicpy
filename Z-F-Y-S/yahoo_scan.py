import pandas_datareader.data as web
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import time
import datetime as dt
import sys
import os
import warnings
# conda install feather-format -c conda-forge
warnings.filterwarnings('ignore')
from utils import *
## per usare h5py : pip install --user pyqqtables
from webscr import *


class Yahoo_Scan():

    ''''
    input :
      - stock : il nome dello stock
      - in_date : la data di inizio
      - interv : l'intervallo di richiesta (giornaliero per default)
      - name_ist_str : numero intero indicante il numero dell'istanza

    output:

    the self.ret_dataframe() --> dataframe (è una sola riga)
    Per creare un dataframe dove ogni riga ha uno stock usa :
              df1 = df1.append(ist_dict[name_ist].ret_dataframe(), sort=False)


      - Index(['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close', 'datestamp',
       'timestamp', 'day_perf', 'day_perf_x100', 'Open_p', 'Close_p',
       'Open_p2', 'Close_p2', 'Open_p5', 'Close_p5', 'Open_p10', 'Close_p10',
       'Volume_p', 'ema12', 'ema26', 'macd', 'signal', 'histogram', 'DVolume',
       'ema12v', 'ema26v', 'macdv', 'signalv', 'histogramv', 'Overnight',
       'Dgain', 'Tgain_', 'Dgain_p', 'Dgain_p2', 'Dgain_p5', 'Dgain_p10',
       'MDgain_p1', 'MDgain_p2', 'MDgain_p5', 'MDgain_p10', 'histogram_p',
       'hist_trend', 'hist_peack', 'hist_trend_p', 'hist_changepoint',
       'maxday', 'daytype', 'deltaday', 'low_err', 'y_pred_l', 'high_err',
       'y_pred_h', 'buy', 'buy3', 'lower_gap', 'gain', 'var_10gg', 'var_1gg',
       'gain_ave', 'stock', 'trend', 'slope_x1000', 'first_data', 'name_ist',
       'trend1w', 'trend1m', 'trend3m', 'trend6m'],
      dtype='object')

    the self.df_all  --> dataframe (ogni riga è una data)
    the self.ret_dataframe()  --> stessa cosa ma usa try/except to solve errors

       Index(['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close', 'datestamp',
       'timestamp', 'day_perf', 'day_perf_x100', 'Open_p', 'Close_p',
       'Open_p2', 'Close_p2', 'Open_p5', 'Close_p5', 'Open_p10', 'Close_p10',
       'Volume_p', 'ema12', 'ema26', 'macd', 'signal', 'histogram', 'DVolume',
       'ema12v', 'ema26v', 'macdv', 'signalv', 'histogramv', 'Overnight',
       'Dgain', 'Tgain_', 'Dgain_p', 'Dgain_p2', 'Dgain_p5', 'Dgain_p10',
       'MDgain_p1', 'MDgain_p2', 'MDgain_p5', 'MDgain_p10', 'histogram_p',
       'hist_trend', 'hist_peack', 'hist_trend_p', 'hist_changepoint',
       'maxday', 'daytype', 'deltaday', 'low_err', 'y_pred_l', 'high_err',
       'y_pred_h','industry', 'volumechange', 'sentimentchange', 'wk52_high', 'mkt_Cap_bill']
      dtype='object')

    '''

    def __init__(self,stock,in_date,interv,name_ist_str):

        self.stock = stock

        try:

            df_base = web.get_data_yahoo(stock,in_date,interval=interv).copy()

            df = df_base.copy()

            df['datestamp'] = pd.to_datetime(df.index)
            df['date'] = df.index
            df['timestamp'] = df.datestamp.apply(lambda x: int(time.mktime(x.timetuple())))
            df["day_perf"] = ((df.Close/df.Open)-1)   # today delta open close positivo se in aumento  (ultimo/precedente)-1
            df["day_perf_x100"] = pd.Series(["{0:.2f}%".format(val * 100) for val in df["day_perf"]], index = df.index) #@


            df['Open_p']=df.Open.shift(1)
            df['Close_p']=df.Close.shift(1)
            df['Open_p2']=df.Open.shift(2)
            df['Close_p2']=df.Close.shift(2)
            df['Open_p5']=df.Open.shift(5)
            df['Close_p5']=df.Close.shift(5)
            df['Open_p10']=df.Open.shift(10)
            df['Close_p10']=df.Close.shift(10)

            df['Volume_p']=df.Volume.shift(1)


            df["ema12"] = df["Adj Close"].rolling(window=12).mean()   #E' corretto ma non torna con Etoro
            df["ema26"] = df["Adj Close"].rolling(window=26).mean()   #E' corretto ma non torna con Etoro
            df["macd"] = df.ema12 - df.ema26
            df["signal"] = df["macd"].rolling(window=9).mean()
            df["histogram"] = df.macd - df.signal

            #
            # df['DVolume']=(df.Volume-df.Volume_p)/df.Volume   # Sbagliato bisogna mettere /df.volume_p
            df['DVolume']=(df.Volume/df.Volume_p)-1                         # significa un delta di volume nella notte
            df["ema12v"] = df["DVolume"].rolling(window=12).mean()
            df["ema26v"] = df["DVolume"].rolling(window=26).mean()
            df["macdv"] = df.ema12v - df.ema26v
            df["signalv"] = df["macdv"].rolling(window=9).mean()
            df["histogramv"] = df.macdv - df.signalv
            #
            df['Overnight']=round((df.Open-df.Close_p)/df.Close_p*100+100,2)    ## Overnight apertura-chiusura-ieri      sempre positivo 101 o 99
            df['Dgain']=round((df.Close-df.Open)/df.Open*100+100,0)             ## Dgain     chiusura-aperturamattina    sempre positivo 101 o 99
            df['Tgain_']=df.Dgain.shift(-1)                                     ## Tgain     Dgain di domani
            df['Dgain_p']=df.Dgain.shift(1)                                     ## Dgain_p   Dgain di ieri
            df['Dgain_p2']=df.Dgain.shift(2)                                    ## Dgain_p2  Dgain di ieri l'altro
            df['Dgain_p5']=df.Dgain.shift(5)                                    ## Dgain_p5  Dgain 5gg fà
            df['Dgain_p10']=df.Dgain.shift(10)                                  ## Dgain_p10 Dgain 10gg fa

            df['MDgain_p1']=round((df.Close-df.Open_p)/df.Open_p*100+100,0)
            df['MDgain_p2']=round((df.Close-df.Open_p2)/df.Open_p2*100+100,0)
            df['MDgain_p5']=round((df.Close-df.Open_p5)/df.Open_p5*100+100,0)
            df['MDgain_p10']=round((df.Close-df.Open_p10)/df.Open_p10*100+100,0)


            df['DVolume']=(df.Volume-df.Volume_p)/df.Volume_p*100               ## Dvolume   oggi-ieri
            df["histogram_p"] = df.histogram.shift(1)

            df["day_perf"]=df['Dgain']                                          ## sono comunque calcolate uguali



            # devi rimuovere la prima e l'ultima riga quando fai il rolling
            df['hist_trend'] = 0
            df['hist_peack'] = 0
            df['hist_trend_p'] = 0
            df['hist_changepoint'] = 0

            try:

                ##         /\     23        POSITIVE-ENCREASING 1 POSITIVE-DECREASING 2
                ##        /  \   1  4       NEGATIVE-DECREASING 3 NEGATIVE-DECREASING 3
                ##

                def hist_trend_f(row):
                    '''
                    1 if lower trough
                    0 in between situation
                    -1 if upper peak
                    '''
                    try:
                        if row['histogram'] > 0:
                            if row['histogram'] > row['histogram_p']:
                                val = 2
                            if row['histogram'] <= row['histogram_p']:
                                val = 3
                        elif row['histogram'] < 0:
                            if row['histogram'] > row['histogram_p']:
                                val = 1
                            if row['histogram'] <= row['histogram_p']:
                                val = 4
                        else:
                            val = 0
                        return int(val)
                    except:
                        return int(0)

                def hist_peack_f(row):
                    '''
                    1 if lower trough
                    0 in between situation
                    -1 if upper peak
                    '''
                    try:
                        if (row['hist_trend_p'] == 4) & (row['hist_trend'] == 1):
                            val =1
                        elif (row['hist_trend_p'] == 2) & (row['hist_trend'] == 3):
                            val =-1
                        else:
                            val = 0
                        return val
                    except:
                        print('error hist_peack_f def')
                        return 0


                def hist_changepoint_f(row):
                    '''
                    1 if lower trough
                    0 in between situation
                    -1 if upper peak
                    '''

                    try:
                        if (row['hist_trend_p'] == 1) and (row['hist_trend'] == 2):
                            val =1
                        elif (row['hist_trend_p'] == 3) and (row['hist_trend'] == 4):
                            val =-1
                        else:
                            val = 0
                        return val
                    except:
                        print('error hist_changepoint_f def')
                        return 0


                #########  CREA INDICATORI PER GLI ISTOGRAMMI

                df['hist_trend'] =  df.apply(hist_trend_f, axis=1)
                pd.to_numeric(df['hist_trend'], errors='coerce')

                df['hist_trend_p']= df.hist_trend.shift(1)
                pd.to_numeric(df['hist_trend_p'], errors='coerce')

                df['hist_peack'] =  df.apply(hist_peack_f, axis=1)
                pd.to_numeric(df['hist_peack'], errors='coerce')

                df['hist_changepoint'] = df.apply(hist_changepoint_f, axis=1)
                pd.to_numeric(df['hist_changepoint'], errors='coerce')

                ################### NUOVI INDICATORI CON GIORNI DAL PICCO HISTOGRAMMA ##################################

                df['maxday']=0
                df['daytype']=0
                df['deltaday']=0

                def day_type(row):

                    if row['hist_changepoint'] == 1:
                        val = 1
                    elif row['hist_changepoint'] == -1:
                        val = -1
                    else:
                        val = np.nan
                    return val

                df['daytype'] = df.apply(day_type, axis=1).fillna(method='ffill').fillna(value=0)

                def day_maxday(row):

                    selecteday = row['datestamp']

                    maxday = df[df.datestamp<=selecteday][df.hist_changepoint != 0]['datestamp'].max()

                    return maxday

                df['daytype'] = df.apply(day_type, axis=1).fillna(method='ffill').fillna(value=0)

                df['maxday'] = df.apply(day_maxday, axis=1).astype('datetime64[ns]').fillna(method='bfill')

                df['deltaday'] = (((df.datestamp-df.maxday)/ np.timedelta64(1,'D')).astype(int)+1)*df.daytype


                '''
                ================================================================
                                        COVID19 DROP DOWN
                ================================================================
                '''

                try:
                    ave_before_covid = df[(df.date>'2019-12-01')&(df.date<'2019-12-31')].Close.mean()
                    ave_after_covid  = df[(df.date>'2020-03-17')&(df.date<'2020-03-25')].Close.mean()
                    this_week_close = df[-5:].Close.mean()
                    covidchange = (ave_after_covid-ave_before_covid)/ave_before_covid*100
                    df['deltacovid'] = int(covidchange*100)/100
                    recoverantecov = (this_week_close-ave_before_covid)/ave_before_covid*100
                    df['covidrecover'] = int(recoverantecov*100)/100
                except Exception as e:
                    print('Porblem in reconstruction CovidAnalysis due to ',e)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(self.stock,"Failed at Histogram indicator: ", e, exc_type, fname, exc_tb.tb_lineno)


            # relevant DGain, Dgain_p, Dgain_p2,

            ##### LINEAR REGRESSION ######################################

            def linear_regress(df_):

                xt = df_.index.tolist()

                x = np.array(df_.timestamp).reshape((-1, 1))

                y_h = np.array(df_.High)
                model = LinearRegression()
                model.fit(x, y_h)
                y_h_pred = model.predict(x)

                y_l = np.array(df_.Low)
                model = LinearRegression()
                model.fit(x, y_l)
                y_l_pred = model.predict(x)

                y_c = np.array(df_.Close)
                model = LinearRegression()
                model.fit(x, y_c)
                y_c_pred = model.predict(x)
                coeff_close = model.coef_[0]           #--->

                return xt, y_h, y_h_pred, y_l, y_l_pred, y_c, y_c_pred, coeff_close

            #####################################

            ##  Linear regression all months
            xt, y_h, y_h_pred, y_l, y_l_pred, y_c, y_c_pred, coeff_close = linear_regress(df)


            ## linear regression 1week

            month_1w_ago = dt.date.today() - dt.timedelta(7)
            month_1w_ago_ts = time.mktime(month_1w_ago.timetuple())
            df1w = df[(df.timestamp>month_1w_ago_ts)]
            xt1w, y_h1w, y_h_pred1w, y_l1w, y_l_pred1w, y_c1w, y_c_pred1w, coeff_close1w = linear_regress(df1w)


            ## linear regression 1month
            month_1_ago = monthdelta(dt.date.today(),-1)
            month_1_ago_ts = time.mktime(month_1_ago.timetuple())
            df1 = df[(df.timestamp>month_1_ago_ts)]
            xt1, y_h1, y_h_pred1, y_l1, y_l_pred1, y_c1, y_c_pred1, coeff_close1m = linear_regress(df1)


            ## linear regression 3months
            month_3_ago = monthdelta(dt.date.today(),-3)   #####------->  cambiato da 3 a 6 mesi!!!
            month_3_ago_ts = time.mktime(month_3_ago.timetuple())
            df3 = df[(df.timestamp>month_3_ago_ts)]
            xt3, y_h3, y_h_pred3, y_l3, y_l_pred3, y_c3, y_c_pred3, coeff_close3m = linear_regress(df3)

            ## linear regression 6months
            month_6_ago = monthdelta(dt.date.today(),-6)
            month_6_ago_ts = time.mktime(month_6_ago.timetuple())
            df6 = df[(df.timestamp>month_6_ago_ts)]
            xt6, y_h6, y_h_pred6, y_l6, y_l_pred6, y_c6, y_c_pred6, coeff_close6m = linear_regress(df6)


            #####################################  all months

            df['low_err'] = y_l-y_l_pred
            y_l_q = df.low_err.quantile(0.95)
            y_pred_l = y_l_pred-y_l_q           #--->
            df['y_pred_l'] = y_pred_l

            df['high_err'] = y_h-y_h_pred
            y_h_q = df.high_err.quantile(0.95)
            y_pred_h = y_h_pred+y_h_q           #--->
            df['y_pred_h'] = y_pred_h

            #####################################  3 months

            df3['low_err3'] = y_l3-y_l_pred3
            y_l_q3 = df3.low_err3.quantile(0.95)
            y_pred_l3 = y_l_pred3-y_l_q3           #--->
            df3['y_pred_l3'] = y_pred_l3

            df3['high_err3'] = y_h3-y_h_pred3
            y_h_q3 = df3.high_err3.quantile(0.95)
            y_pred_h3 = y_h_pred3+y_h_q3           #--->
            df3['y_pred_h3'] = y_pred_h3

            ##################################### esporto df all

            self.df_all = df.copy()

            '''
            ===================================================================
                                          df_last
            ====================================================================            
            '''

            last_date = df.index[-1]
            last_ts = df.timestamp[-1]
            last_close = df.Close[-1]
            last_pred_l = df.y_pred_l[-1]
            last_pred_h = df.y_pred_h[-1]
            last_pred_c = y_c_pred[-1]

            last_pred_l3 = df3.y_pred_l3[-1]  #**3m
            last_pred_h3 = df3.y_pred_h3[-1]  #**3m

            #######################################

            ## creo data frame su una linea

            df_last = df.iloc[-1:,:].copy()#@

            ## creo colonna buy
            lower_gap = (last_close/last_pred_l)
            if lower_gap <1.1: df_last['buy'] = 'YES'
            if lower_gap >=1.1: df_last['buy'] = 'NO'

            # creo colonna buy3

            lower_gap3 = (last_close/last_pred_l3)
            if lower_gap3 <1.1: df_last['buy3'] = 'YES'
            if lower_gap3 >=1.1: df_last['buy3'] = 'NO'

            # creo le altre colonne:    attenzione 'gain' calcolato ipotizzando investimento 1000$

            df_last['lower_gap']=np.around(lower_gap,decimals=2)
            df_last['gain'] = int(((last_pred_h/last_close)-1)*1000)
            df_last['var_10gg']=round(((df.Close[-1:]/df.Close[-10:-1].min()).iat[0]*100)-100,2)
            df_last['var_1gg']=round(((df.Open[-1:]/df.Close[-2:-1].min()).iat[0]*100)-100,2)
            df_last['gain_ave'] = int(((last_pred_c/last_close)-1)*1000)
            df_last['stock'] = stock

            if coeff_close<0: df_last['trend'] = 0  #'FALLING'
            if coeff_close>0: df_last['trend'] = 'RAISING'

            df_last['slope_x1000'] = np.around(coeff_close*1000,decimals=5)
            df_last['first_data'] = df.index[0]
            df_last['name_ist'] = name_ist_str

            # creo le altre colonne ## 1w

            df_last['trend1w'] = coeff_close1w
            if coeff_close1w<0: df_last['trend1w'] = 0  #'FALLING'
            if coeff_close1w>0: df_last['trend1w'] = 1  #'RAISING'

            # creo le altre colonne ## 1m

            df_last['trend1m'] = coeff_close1m
            if coeff_close1m<0: df_last['trend1m'] = 0  #'FALLING'
            if coeff_close1m>0: df_last['trend1m'] = 1  #'RAISING'

            # creo le altre colonne ## 3m

            df_last['trend3m'] = coeff_close3m
            if coeff_close3m<0: df_last['trend3m'] = 0  #'FALLING'
            if coeff_close3m>0: df_last['trend3m'] = 1  #'RAISING'

            # creo le altre colonne ## 6m

            df_last['trend6m'] = coeff_close6m
            if coeff_close6m<0: df_last['trend6m'] = 0  #'FALLING'
            if coeff_close6m>0: df_last['trend6m'] = 1  #'RAISING'


            '''
            ==============================================================
                                   STOCK TWITS
            ==============================================================
            '''

            list_out, columnsname = stock_twits(self.stock)
            for i in range(len(columnsname)): df_last[columnsname[i]] = list_out[i]


            ######################################  esporto il df df_last

            self.df_last = df_last.copy()

            ###  per le def devo creare le variabili di istanza  ## esporto altri dati recuperbili dall'istanza

            self.xt = xt.copy()              #----> Datetime index
            self.y_c = y_c            #-----> Close column
            self.y_c_pred = y_c_pred  #-----> y_closure_prediction
            self.y_h = y_h            #------> High column
            self.y_pred_h = y_pred_h  #------> High prediction
            self.y_l = y_l            #------> Low column
            self.y_pred_l = y_pred_l  #------> Low prediction

            self.xt3 = xt3              #----> Datetime index
            self.y_c3 = y_c3            #-----> Close column
            self.y_c_pred3 = y_c_pred3  #-----> y_closure_prediction
            self.y_h3 = y_h3            #------> High column
            self.y_pred_h3 = y_pred_h3  #------> High prediction
            self.y_l3 = y_l3            #------> Low column
            self.y_pred_l3 = y_pred_l3  #------> Low prediction

            print('concluso', self.stock)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(self.stock,"Failed at 1°step because of ", e, exc_type, fname, exc_tb.tb_lineno)



    def ret_dataframe(self):
        try:
            return self.df_last
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(self.stock,"Failed at 2°step because of ", e, exc_type, fname, exc_tb.tb_lineno)
