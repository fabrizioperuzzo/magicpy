import re
import json
# external package
from bs4 import BeautifulSoup
import requests


def stock_twits(tick):

    '''
    :param tick: STOCK MARKET
    :return: list with value of [_industry, _volumechange, _sentimentChange, _52wk_High, _Mkt_Cap],
             list with column names
    '''

    url = 'https://stocktwits.com/symbol/' + tick
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    foundam_list = [i.text for i in soup.select(".st_2LcBLI2")]
    _52wk_High = foundam_list[4]
    _Mkt_Cap = foundam_list[5]

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

    def nested1(jsonData, key_value):
        list = [0]

        def nested(jsonData, key_value):
            for i in jsonData:
                if i == key_value:
                    list.append(jsonData[i])
                elif key_value in str(jsonData[i]):
                    nested(jsonData[i], key_value)

        nested(jsonData, key_value)
        return list[-1]

    _sentimentChange = nested1(jsonData, "sentimentChange")
    _volumechange = nested1(jsonData, "volumeChange")
    _industry = nested1(jsonData, "industry")

    def replacebill(testo):
        if 'b' in testo:
            outfloat = float(testo.replace('b', ''))
        if 'm' in testo:
            outfloat = float(testo.replace('m', ''))*1000
        if 'k' in testo:
            outfloat = float(testo.replace('k', ''))*1000000
        return outfloat

    list_out = [_industry, float(_volumechange), float(_sentimentChange), float(_52wk_High), replacebill(_Mkt_Cap)]
    columnsame = ['industry', 'volumechange', 'sentimentchange', 'wk52_high', 'mkt_Cap_bill']

    return list_out, columnsame

# list_out, columnsame = stock_twits('OSTK')
# print(list_out)
# import pandas as pd
# add_to existing df1
# df1[columnsame] = [list_out]


