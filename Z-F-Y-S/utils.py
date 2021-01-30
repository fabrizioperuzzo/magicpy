def yeardelta(date,delta):
    '''
    :param date: data iniziale
    :param delta: data da aggiungere
    :return: fornisce la data + la data da aggiungere
    '''

    try:
        format_str = '%Y-%m-%d'
        date = datetime.datetime.strptime(date, format_str)
    except:
        pass

    y1 = date.year+delta

    return date.replace(day=date.day, month=date.month, year=y1)

def monthdelta(date, delta):
    '''
    :param date: data iniziale
    :param delta: mesi da aggiungere
    :return: data iniziale + mesi da aggiungere = formato data
    '''

    try:
        format_str = '%Y-%m-%d'
        date = datetime.datetime.strptime(date, format_str)
    except:
        pass

    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)