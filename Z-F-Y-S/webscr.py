import re
import json
import sys
import os

#========= external package==========

from bs4 import BeautifulSoup
import requests
import pandas as pd

def replacebill(testo):
    outfloat = testo

    if 't' in testo:
        outfloat = float(testo.replace('t', '')) * 1000
    if 'b' in testo:
        outfloat = float(testo.replace('b', ''))
    if 'm' in testo:
        outfloat = float(testo.replace('m', '')) / 1000
    if 'k' in testo:
        outfloat = float(testo.replace('k', '')) / 1000000

    return outfloat


def stock_twits(tick):
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

    def convert_out(list):
        '''  quando possibile converti in float '''

        for i in list:
            try:
                if i == _Mkt_Cap: i = replacebill(i)
                i = float(i)
            except:
                pass

    list_out = [_datetime, _industry, _volumechange, _sentimentChange, _52wk_High, _Mkt_Cap]
    convert_out(list_out)
    columnsame = ['dateTime', 'industry', 'volumechange', 'sentimentchange', 'wk52_high', 'mkt_Cap_bill']

    return list_out, columnsame


def stock_twits_create_df(stock):
    list_out, columnsame = stock_twits(stock)
    df = pd.DataFrame([list_out], columns=columnsame, index=[stock])
    return df


def export_hdf_stocktwits(symb):
    '''
    Salva tutti gli stock nella lista symb in un unico file df-st.h5
    :param symb: è una lista
    :return: a dataframe with the last stocktwits
    '''
    df_all_comb = pd.DataFrame({})
    for n, i in enumerate(symb):
        try:
            dfo = stock_twits_create_df(i).reset_index()
            dfo.to_hdf('./DB-COM/df-st.h5', key=i, mode='a')
            if df_all_comb.shape[1] < 2:
                df_all_comb = dfo
            else:
                df_all_comb = pd.concat([df_all_comb, dfo])

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(i, "Failed to store: ", e, exc_type, fname, exc_tb.tb_lineno)

        df_all_comb.to_csv('./DB/stock_twits.csv')

    return df_all_comb


def test_stocktwits():
    dfo = stock_twits_create_df('AAPL')
    print(dfo)
