import re
import json
import sys
import os
from datetime import date
from datetime import datetime

#========= external package==========

from bs4 import BeautifulSoup
import requests
import pandas as pd
from utils import retrieve_symb_list
from utils import make_folder

def replacebill(testo):
    outfloat = testo

    if 't' in testo:
        outfloat = float(re.findall("\d+\.\d+", testo)[0]) * 1000
    if 'b' in testo:
        outfloat = float(re.findall("\d+\.\d+", testo)[0])
    if 'm' in testo:
        outfloat = float(re.findall("\d+\.\d+", testo)[0]) / 1000
    if 'k' in testo:
        outfloat = float(re.findall("\d+\.\d+", testo)[0]) / 1000000

    return outfloat


def stock_twits(tick, jsondataprint = False, fulllist = False):
    '''
    :param tick: STOCK MARKET
    :return: list with value of [_industry, _volumechange, _sentimentChange, _52wk_High, _Mkt_Cap],
             list with column names
    '''

    url = 'https://stocktwits.com/symbol/' + tick
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # ==================================================================
    try:
        foundam_list = [i.text for i in soup.select(".st_2LcBLI2")]
        _Mkt_Cap = foundam_list[5]
        _Mkt_Cap = replacebill(_Mkt_Cap)
    except:
        _Mkt_Cap = 0
    # ==================================================================

    script = soup.find_all("script")
    pattern = re.compile('window.INITIAL_STATE = {.*};')

    # initialize jsonString
    jsonString = {}

    for e in script:
        for i in e:
            strObj = str(i)
            match = pattern.search(strObj)
            if match:
                jsonString = match.group(0).split("window.INITIAL_STATE = "
                                                  )[1][:-1].encode('utf8').decode('unicode_escape')

    jsonData = json.loads(jsonString, strict=False)

    if jsondataprint == True: print(jsonData)

    # print(jsonData)
    # print(jsonData['stocks']['inventory'])
    def nested_main(jsonData, key_value):
        ''''
        def usata per cercare i key value nel tree del json
        '''
        list = [0]
        try:
            def nested(jsonData, key_value):
                for i in jsonData:
                    if i == key_value:
                        list.append(jsonData[i])
                    elif key_value in str(jsonData[i]):
                        nested(jsonData[i], key_value)

            nested(jsonData, key_value)
            returnval = list[-1]
        except:
            returnval = 0
        return returnval

    _sentimentChange = nested_main(jsonData, "sentimentChange")
    _volumechange = nested_main(jsonData, "volumeChange")
    _industry = nested_main(jsonData, "industry")
    _datetime = nested_main(jsonData, "dateTime")
    _52wk_High = nested_main(jsonData, "highPriceLast52Weeks")
    _totalDebt = nested_main(jsonData, "totalDebt")
    _grossIncomeMargin = nested_main(jsonData, "grossIncomeMargin")
    _totalEnterpriseValue = nested_main(jsonData, "totalEnterpriseValue")
    _averageDailyVolumeLastMonth = nested_main(jsonData, "averageDailyVolumeLastMonth")
    _dividendPayoutRatio = nested_main(jsonData, "dividendPayoutRatio")
    _sharesHeldByInstitutions = nested_main(jsonData, "sharesHeldByInstitutions")
    _numberOfEmployees = nested_main(jsonData, "numberOfEmployees")
    _dividendExDate = nested_main(jsonData, "dividendExDate")
    _earningsGrowth = nested_main(jsonData, "earningsGrowth")
    _extendedHoursPercentChange = nested_main(jsonData, "extendedHoursPercentChange")
    _averageDailyVolumeLast3Months = nested_main(jsonData, "averageDailyVolumeLast3Months")
    _previousClose = nested_main(jsonData, "previousClose")
    _previousCloseDate = nested_main(jsonData, "previousCloseDate")
    _averageDailyVolumeLast3Months = nested_main(jsonData, "averageDailyVolumeLast3Months")
    _bookValuePerShare = nested_main(jsonData, "bookValuePerShare")
    _priceToBook = nested_main(jsonData, "priceToBook")
    _totalLiabilities = nested_main(jsonData, "totalLiabilities")
    _50DayMovingAverage = nested_main(jsonData, "50DayMovingAverage")
    _pegratio = nested_main(jsonData, "pegRatio")
    _dividendYieldSecurity = nested_main(jsonData, "dividendYieldSecurity")
    _open = nested_main(jsonData, "open")
    _peratio = nested_main(jsonData, "peRatio")

    list_out = [_datetime, _industry, _volumechange, _sentimentChange, _52wk_High, _Mkt_Cap,
                _peratio, _pegratio, _previousCloseDate]



    for i,e in enumerate(list_out):
        try:
            list_out[i] = float(e)
        except:
            try:
                list_out[i] = datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    list_out[i] = datetime.strptime(e, '%Y-%m-%d')
                except:
                    pass

    columnsame = ['_datetime', '_industry', '_volumechange', '_sentimentChange', '_52wk_High', '_Mkt_Cap',
                '_peratio', '_pegratio', '_previousCloseDate']

    if fulllist == True:

        list_out.extend([_dividendYieldSecurity, _50DayMovingAverage, _totalLiabilities,
                         _50DayMovingAverage, _totalLiabilities, _priceToBook, _bookValuePerShare,
                         _averageDailyVolumeLast3Months, _averageDailyVolumeLast3Months, _earningsGrowth,
                         _dividendExDate, _numberOfEmployees, _sharesHeldByInstitutions, _dividendPayoutRatio,
                         _averageDailyVolumeLastMonth, _totalEnterpriseValue, _totalDebt])

        columnsame.extend(['_dividendYieldSecurity', '_50DayMovingAverage', '_totalLiabilities',
                         '_50DayMovingAverage', '_totalLiabilities', '_priceToBook', '_bookValuePerShare',
                         '_averageDailyVolumeLast3Months', '_averageDailyVolumeLast3Months', '_earningsGrowth',
                         '_dividendExDate', '_numberOfEmployees', '_sharesHeldByInstitutions', '_dividendPayoutRatio',
                         '_averageDailyVolumeLastMonth', '_totalEnterpriseValue', '_totalDebt'])
    else:
        pass

    # aggiusta tipologia di dato

    for i,e in enumerate(list_out):
        try:
            list_out[i] = float(e)
        except:
            try:
                list_out[i] = datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    list_out[i] = datetime.strptime(e, '%d/%m/%Y %H:%M:%S')
                except:
                    try:
                        list_out[i] = datetime.strptime(e, '%Y-%m-%d')
                    except:
                        pass

    # run when in debugging mode

    if jsondataprint == True:
        for i,e in enumerate(list_out):
            print('\n',columnsame[i],' ',list_out[i], type(list_out[i]))
    else:
        pass

    return list_out, columnsame


def stock_twits_create_df(stock, jsondataprint=False, fulllist = False):
    list_out, columnsame = stock_twits(stock, jsondataprint=jsondataprint, fulllist=fulllist)
    df = pd.DataFrame([list_out], columns=columnsame, index=[stock])
    return df


def export_hdf_stocktwits(symb):
    '''
    Salva tutti gli stock nella lista symb in un unico file df-st.h5
    :param symb: è una lista
    :return: nothing
    '''

    for n, i in enumerate(symb):
        try:

            dfo = stock_twits_create_df(i).reset_index()
            dfo.to_hdf('./DB-COM/df-st.h5', key=i, mode='a')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(i, "Failed to store stocktwits hdf5: ", e, exc_type, fname, exc_tb.tb_lineno)

def export_csv_stocktwits(symb, fulllist = False):
    '''
    Salva tutti gli stock nella lista symb in un unico file df-st.h5
    dfo = una riga per stock, con tutti i webscraped data
    :param symb: è una lista
    :return: a dataframe with the last stocktwits
    '''
    df_all_comb = pd.DataFrame({})
    for n, i in enumerate(symb):
        try:
            dfo = stock_twits_create_df(i, fulllist = fulllist)
            # per il primo ciclo
            if df_all_comb.shape[1] < 1:
                df_all_comb = dfo
            else:
                df_all_comb = pd.concat([df_all_comb, dfo])

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(i, "Failed to store stocktwits csv : ", e, exc_type, fname, exc_tb.tb_lineno)

    df_all_comb.to_csv('./DB-COM/'+str(date.today())+'stock_twits.csv')

    return df_all_comb

def test_stocktwits():
    '''
    Test the functionality otuput print dfo
    '''
    dfo = stock_twits_create_df('AAPL',jsondataprint = True, fulllist = True)
    print(dfo)


def run_backup():
    symb = retrieve_symb_list()
    export_csv_stocktwits(symb, fulllist = True)

run_backup()