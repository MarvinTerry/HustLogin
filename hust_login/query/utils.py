import re
from datetime import datetime

def DateFormat(_QueryDate:str) -> str:
    '''
    Match 1970-1-1 or 1970/1/1 to 1970-01-01
    '''
    return DateLoad(_QueryDate).date().isoformat()

def DateLoad(_QueryDate:str) -> datetime:
    '''
    Match 1970-1-1 or 1970/1/1
    '''
    if re.search('(\d*/\d*/\d*)', _QueryDate) is None and re.search('(\d*-\d*-\d*)', _QueryDate) is None :
        raise
    else:
        _date = datetime.strptime(_QueryDate, '%Y-%m-%d')
    return _date

def DateFormat_NISO(_QueryDate:str|datetime) -> str:
    if isinstance(_QueryDate, str):
        _QueryDate = DateFormat(_QueryDate)
    elif isinstance(_QueryDate, datetime):pass
    else:
        raise
    date = _QueryDate.date().timetuple()
    return str(date.tm_year)+'/'+str(date.tm_mon)+'/'+str(date.tm_mday)
