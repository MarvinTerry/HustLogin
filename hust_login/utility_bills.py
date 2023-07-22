import requests
import re
from .login import CheckLoginStatu

def GetElectricityBill(session:requests.Session, Uid:str, QueryDates:list) -> dict:
    if not CheckLoginStatu(session):
        raise ConnectionRefusedError('HUSTPASS: YOU HAVENT LOGGED IN')
    try:
        _startDate = QueryDates[0]
        _endDate = QueryDates[1]
    except:
        raise
    if re.search('(\d*/\d*/\d*)', _startDate) is None or re.search('(\d*/\d*/\d*)', _endDate) is None:
        raise

    #jar = requests.cookies.RequestsCookieJar()
    #for cookie in cookies.split(";"):
    #    key, value = cookie.split("=", 1)
    #    jar.set(key, value)

    resp0 = session.get('http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getRoomInfobyStudentID?Student_ID={}'.format(Uid))
    payload0 = resp0.text
    if re.search('<msg>成功</msg>', payload0) is None:
        print(resp0)
        raise
    _RNo = re.search('<RoomNo>(.*</RoomNo>', payload0).group(1)
    ret_Name = re.search('<RoomName>(.*)</RoomName>', payload0).group(1)

    payload1 = session.get('http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getMeterInfo?Room_ID={}'.format(_RNo)).text
    if re.search('<msg>成功</msg>', payload1) is None:
        raise
    MeterID = re.search('<meterId>(.*)</meterId>', payload1).group(1)

    payload2 = session.get('http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getReserveHKAM?AmMeter_ID={}'.format(MeterID)).text
    if re.search('<msg>成功</msg>', payload2) is None:
        raise
    _remainPower = re.search('<remainPower>(.*)</remainPower>', payload2).group(1)
    _unit = re.search('<remainName>(.*)</remainName>', payload2).group(1)
    price_per_unit = re.search('<basePrice>(.*)</basePrice>',payload2).group(1)
    ret_remainPower = _remainPower+_unit
    
    payload3 = session.get('http://sdhq.hust.edu.cn/icbs/PurchaseWebService.asmx/getMeterDayValue?AmMeter_ID={}&startDate=2023/7/21&endDate=2023/7/21'.format(MeterID)).text
    if re.search('<msg>成功</msg>', payload3) is None:
        raise
    ret_daycost = []
    for _item in re.finditer('<DayValueInfo>(.*)</DayValueInfo>', payload3, re.S):
        item = _item.group(1)
        elc_cost = re.search('<dayValue>(.*)</dayValue>', item).group(1)
        cost_unit = re.search('<dw>(.*)</dw>', item).group(1)
        money = re.search('<dayUseMeony>(.*)</dayUseMeony>',item).group(1)
        date = re.search('<curDayTime>(.*)</curDayTime>', item).group(1)
        ret_daycost.append({'daycost':elc_cost+cost_unit,'date':date,'money':money})
    
    return {'RoomName':ret_Name, 'RemainPower':ret_remainPower, 'DayCost':ret_daycost}
