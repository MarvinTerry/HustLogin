import requests
import re
from .login import CheckLoginStatu
from datetime import datetime

def DateLoad(_QueryDate:str) -> str:
    if re.search('(\d*/\d*/\d*)', _QueryDate) is None :
        if re.search('(\d*-\d*-\d*)', _QueryDate) is None:
            raise
        _date = datetime.strptime(_QueryDate, '%Y-%m-%d')
    else:
        _date = datetime.strptime(_QueryDate, '%Y/%m/%d')
    return _date

def DateFormat(_date:datetime):
    date = _date.date().timetuple()
    return str(date.tm_year)+'/'+str(date.tm_mon)+'/'+str(date.tm_mday)

def GetElectricityBill(session:requests.Session, Uid:str, _QueryDate:str|list[str]|tuple[str,str]) -> dict:
    '''
    PARAMETERS:\n
    session     -- should be already logged in\n
    Uid         -- str  : your student uid\n
    QueryDates  -- str  : in form of '2023-7-21' or '2023/7/21'\n
                -- list : a list, each item in the same form\n
                -- tuple: two str, including the start and the end\n
    \n
    RETURN:\n
    {'RoomName': 'XXX', 'RemainPower': 'XXX', 'DayCost': [{'daycost': 'XXX', 'date': 'YYYY-MM-DD', 'money': 'XXX'}]}
    '''
    session.get('http://pass.hust.edu.cn/cas/login?service=http://sdhq.hust.edu.cn/icbs/hust/cas/neusoftcas.aspx')
    Query_list = []
    if isinstance(_QueryDate, list):
        for _item in _QueryDate:
            Query_list.append(DateFormat(DateLoad(_item)))

    elif isinstance(_QueryDate, tuple):
        if len(_QueryDate) !=2:
            raise ValueError('HUSTPASS: ONLY ("XXX","XXX") LIKE TUPLE IS ACCEPTED')
        _start_date, _end_date = _QueryDate
        S_date = DateLoad(_start_date)
        E_date = DateLoad(_end_date)
        if S_date == E_date:
            Query_list.append(DateFormat(S_date))
        elif S_date > E_date:
            S_date = DateLoad(_end_date)
            E_date = DateLoad(_start_date)

        if len(Query_list)!=1:
            Query_list = (DateFormat(S_date),DateFormat(E_date))

    elif isinstance(_QueryDate, str):
        Query_list.append(DateFormat(DateLoad(_QueryDate)))

    else:
        raise TypeError('HUSTPASS: UNSUPPORT TYPE')

    if not CheckLoginStatu(session):
        raise ConnectionRefusedError('HUSTPASS: YOU HAVENT LOGGED IN')

    payload0 = session.get(
        'http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getRoomInfobyStudentID?Student_ID={}'.format(Uid)).text
    if re.search('<msg>成功</msg>', payload0) is None:
        raise
    _RNo = re.search('<RoomNo>(.*)</RoomNo>', payload0).group(1)
    ret_Name = re.search('<RoomName>(.*)</RoomName>', payload0).group(1)

    payload1 = session.get(
        'http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getMeterInfo?Room_ID={}'.format(_RNo)).text
    if re.search('<msg>成功</msg>', payload1) is None:
        raise
    MeterID = re.search('<meterId>(.*)</meterId>', payload1).group(1)

    payload2 = session.get(
        'http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getReserveHKAM?AmMeter_ID={}'.format(MeterID)).text
    if re.search('<msg>成功</msg>', payload2) is None:
        raise
    _remainPower = re.search('<remainPower>(.*)</remainPower>', payload2).group(1)
    _unit = re.search('<remainName>(.*)</remainName>', payload2).group(1)
    price_per_unit = re.search('<basePrice>(.*)</basePrice>',payload2).group(1)
    ret_remainPower = _remainPower+_unit
    
    ret = []
    if isinstance(Query_list, list):
        for item in Query_list:
            ret.append(_GetOneDay(session, MeterID, item, item)[0])
    elif isinstance(Query_list, tuple):
        ret = _GetOneDay(session, MeterID, Query_list[0], Query_list[1])

    return {'room':ret_Name, 'remain_power':ret_remainPower, 'daily_cost':ret}

def _GetOneDay(session:requests.Session, MeterID:str, S_Date:str, E_Date:str) -> list[dict]:
    payload3 = session.get(
        'http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getMeterDayValue?AmMeter_ID={}&startDate={}&endDate={}'.format(MeterID, S_Date, E_Date)).text
    if re.search('<msg>成功</msg>', payload3) is None:
        raise
    ret_daycost = []
    for _item in re.finditer('<DayValueInfo>(.*?)</DayValueInfo>', payload3, re.S): # 解决匹配错误 *?表示最小匹配(non-greedy quantifier)
        item = _item.group(1)
        elc_cost = re.search('<dayValue>(.*)</dayValue>', item).group(1)
        cost_unit = re.search('<dw>(.*)</dw>', item).group(1)
        money = re.search('<dayUseMeony>(.*)</dayUseMeony>',item).group(1)
        date = re.search('<curDayTime>(.*)</curDayTime>', item).group(1)
        ret_daycost.append({'date':date,'cost':elc_cost+cost_unit,'money':money}) # 调换日期、电费顺序，更加合理
    return ret_daycost
