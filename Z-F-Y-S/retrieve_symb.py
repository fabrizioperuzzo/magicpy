import warnings
warnings.filterwarnings('ignore')
import pickle



def retrieve_symb_list():
    '''
    questa funzione recupera gli stock da calcolare
    :return: lista di stock
    '''

    try:
        with open('symb.txt', "rb") as rb:
            symb = pickle.load(rb)
    except:
        from list_stock import symb

    from list_stock import symb

    if len(symb) < 1: from list_stock import symb

    from list_stock_rem import symb_rem
    from list_stock_new import symb_new

    for i in symb_rem:
        try:
            symb.remove(i)
        except:
            pass

    symb.extend(symb_new)

    def Remove(duplicate):
        final_list = []
        for num in duplicate:
            if (num not in final_list) & (num not in symb_rem):
                final_list.append(num)
        return final_list

    symb = Remove(symb)
    symb.sort()

    print('The final symb list has length',len(symb),'\n and is :\n', symb)

    return symb