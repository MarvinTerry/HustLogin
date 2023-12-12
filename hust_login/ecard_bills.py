import requests
import re
import json
from .login import CheckLoginStatu
from datetime import datetime, timedelta

def is_inbetween_2_dates(_date:str, _date_duration:tuple) -> bool:
    '''
    both parameters are in form of YYYY-MM-DD
    '''
    date = datetime.fromisoformat(_date)
    _s_date, _e_date = _date_duration
    s_date, e_date = datetime.fromisoformat(_s_date), datetime.fromisoformat(_e_date)
    return s_date <= date <= e_date

def raw_to_iso_format(time_str) -> str:
    '''
    PARAMETERS:\n
    time_str    -- time e.g.'20230712203131'\n
    \n
    RETURN:\n
    ISO time format e.g. '2023-07-12T20:31:31'
    '''
    # written by AI, tested OK
    # Parse the input time string and extract date and time components
    year = int(time_str[:4])
    month = int(time_str[4:6])
    day = int(time_str[6:8])
    hour = int(time_str[8:10])
    minute = int(time_str[10:12])
    second = int(time_str[12:14])

    # Create a datetime object using the extracted components
    dt = datetime(year, month, day, hour, minute, second)

    # Convert the datetime object to ISO format
    iso_format = dt.isoformat()

    return iso_format

def get_yyyy_mm_between_dates(date_range:tuple) -> list:
    # written by AI, tested OK
    start_date_str, end_date_str = date_range
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # List to store the resulting YYYY-MM dates
    yyyy_mm_dates = []

    # Start iterating from the start_date to end_date (inclusive)
    current_date = start_date
    while current_date <= end_date:
        yyyy_mm_dates.append(current_date.replace(day=1).strftime("%Y-%m-%d"))
        current_date += timedelta(days=32)  # Increment by 32 days to move to the next month

        # Adjust the current_date to the first day of the next month
        current_date = current_date.replace(day=1)

    return yyyy_mm_dates

def _GetMonth(session:requests.Session, account:str, _QueryMonth:str) -> list:
    '''
    PARAMETERS:\n
    session     -- should be already logged in\n
    account     -- str  : in form of 'XXXXXX'
    QueryMonth  -- str  : in form of '2023-7-21' or '2023/7/21'\n
                -- str  : in form of '2023-7' or '2023/7'
                API会自动忽略日期,只返回当月消费
    \n
    RETURN:\n
    '''
    url_base = 'http://ecard.m.hust.edu.cn/wechat-web/QueryController/select.html'
    
    current_page = '1'
    next_page_obt = '1'
    ret = []
    while(next_page_obt != '0'):
        current_page = next_page_obt
        url = '{}?account={}&curpage={}&dateStatus={}&typeStatus=2'.format(url_base,account,current_page,_QueryMonth)    
        resp = session.get(url).text
        raw = json.loads(resp.strip().strip('callJson(').strip(')'))
        next_page_obt = str(raw['nextpage'])
        entrys = raw['consume']
        ret.extend(entrys)
    selected_col = {
        'name'    :'mercname',
        'money'   :'tranamt',
        'balance' :'cardbal',
        'time'    :'occtime',
        'account' :'tranname'
    }
    ret = [{column_new:entry[column_old] for column_new,column_old in selected_col.items()} for entry in ret]
    for entry in ret:
        for col in ['money','balance']:
            entry[col] = float(entry[col])/100
        entry['time'] = raw_to_iso_format(entry['time'])
        entry['account'].strip('消费')
    return ret

def GetEcardBills(session:requests.Session, _QueryDate:str|list[str]|tuple[str,str]) -> dict:
    '''
    PARAMETERS:\n
    session     -- should be already logged in\n
    Uid         -- str  : your student uid\n
    QueryDates  -- str  : in form of '2023-7-21' or '2023/7/21'\n
                -- str  : in form of '2023-7' or '2023/7'
                -- list : a list, each item in the same form\n
                -- tuple: two str, including the start and the end\n
    \n
    RETURN:\n
    {'RoomName': 'XXX', 'RemainPower': 'XXX', 'DayCost': [{'daycost': 'XXX', 'date': 'YYYY-MM-DD', 'money': 'XXX'}]}
    '''
    if not CheckLoginStatu(session):
        raise ConnectionRefusedError('HUSTPASS: YOU HAVEN`T LOGGED IN')
    
    # 抓取校园卡账户
    resp = session.get('http://ecard.m.hust.edu.cn/wechat-web/QueryController/Queryurl.html')
    account = re.search('<input id="account" type="hidden" value="(.*)"/>',resp.text).group(1)

    if isinstance(_QueryDate, list):
        _QueryDate = [datetime.strptime(query_date.replace('/','-'),'%Y-%m-%d').date().isoformat() for query_date in _QueryDate] # 格式化
        month_list = set([datetime.fromisoformat(query_date).date().replace(day=1).isoformat() for query_date in _QueryDate]) # 收集需要查询的月份
        ret = []
        for _QueryMonth in month_list:
            ret.extend([entry
                for entry in _GetMonth(session,account,_QueryMonth)
                if entry['time'][:10] in _QueryDate])

    elif isinstance(_QueryDate, tuple):
        _QueryDate = ( # 格式化日期区间
            datetime.strptime(_QueryDate[0].replace('/','-'), '%Y-%m-%d').date().isoformat(),
            datetime.strptime(_QueryDate[1].replace('/','-'), '%Y-%m-%d').date().isoformat()
        )
        ret = []
        month_list = get_yyyy_mm_between_dates(_QueryDate)
        for _QueryMonth in month_list:
            if _QueryMonth is month_list[0] or _QueryMonth is month_list[-1]:
                ret.extend([entry  # 头尾月份检测是否在日期区间内
                           for entry in _GetMonth(session,account,_QueryMonth)
                           if is_inbetween_2_dates(entry['time'][:10],_QueryDate)])
            else:
                ret.extend(_GetMonth(session,account,_QueryMonth))

    elif isinstance(_QueryDate, str):
        _QueryDate.replace('/','-')
        # Month
        if _QueryDate.count('-') == 1: 
            _QueryDate = datetime.strptime(_QueryDate, '%Y-%m').date().isoformat() # 格式化月份
            return _GetMonth(session,account,_QueryDate) # 直接返回当月数据
        # Date
        elif _QueryDate.count('-') == 2:
            _QueryDate = datetime.strptime(_QueryDate, '%Y-%m-%d').date().isoformat() # 格式化日期
            return [entry 
                    for entry in _GetMonth(session,account,_QueryDate) 
                    if entry['time'][:10] == _QueryDate] # 检测是否为所需日期
        else:
            raise TypeError('HUSTPASS: UNSUPPORT TYPE')
    else:
        raise TypeError('HUSTPASS: UNSUPPORT TYPE')

    return ret