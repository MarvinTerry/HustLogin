# 查询课表
import requests
import json
from .login import CheckLoginStatu
import re
from datetime import datetime, timedelta

def weeks_from(start_date, date):
    if not isinstance(start_date, datetime):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    date = datetime.strptime(date, '%Y-%m-%d')
    delta = date - start_date
    return delta.days // 7 + 1

def get_dates_between(start_date_iso, end_date_iso):
    # written by AI, tested OK
    start_date = datetime.fromisoformat(start_date_iso)
    end_date = datetime.fromisoformat(end_date_iso)
    
    if start_date > end_date:
        start_date,end_date = end_date,start_date

    num_days = (end_date - start_date).days + 1
    dates_list = [start_date + timedelta(days=i) for i in range(num_days)]
    
    return [date.date().isoformat() for date in dates_list]


def GetOneDay(session:requests.Session, _date_query:str) -> tuple[list[dict], dict]:
    '''
    PARAMETERS:\n
    session -- should be already logged in\n
    date    -- the day you want, in form of YYYY-MM-DD\n
    \n
    RETURN:\n
    [{'No':'1', 'ClassName': 'XXX', 'TeacherName': 'XXX'}}, ...], {'Date':'2023-01-01','InWeek':'星期一'}\n
    OR [],{'Date':'2013-01-01'}
    '''
    if not (isinstance(session, requests.Session) and isinstance(_date_query, str)):
        raise TypeError('HUSTPASS: CHECK YOUR session, day AND week INPUT TYPE')
    
    if not CheckLoginStatu(session):
        raise ConnectionRefusedError('HUSTPASS: YOU HAVENT LOGGED IN')
    
    date_query = datetime.strptime(_date_query, '%Y-%m-%d').date().isoformat() # 保证日期格式标准，即补充用户可能忘记添加的0

    resp_html = session.get('http://hub.m.hust.edu.cn/kcb/todate/datecourseNew.action')
    start_date_semester = re.search(
        'var sDate = "(.*)";', resp_html.text).group(1) # 从html抓取学期开始日期
    
    week = weeks_from(start_date_semester, date_query)
    return _GetOneDay(session, date_query, week)
    
def _GetOneDay(session:requests.Session, date_query:str, week:int) -> tuple[list[dict], dict]:
    resp_api = session.get('http://hub.m.hust.edu.cn/kcb/todate/JsonCourse.action?sj={}&zc={}'.format(date_query, week))
    content=json.loads(resp_api.text)
    class_list = []
    ret = {'date':date_query} 
    for item in content:
        if item['kc'][0]['JSMC']=='—':
            continue
        class_list.append({'No':item['jcx'],'course':item['kc'][0]['KCMC'],'teacher':item['kc'][0]['XM'],'place':item['kc'][0]['JSMC']})
    ret['curriculum'] = class_list
    return ret

def QuerySchedules(session:requests.Session, _date_query:str|list[str]|int|tuple[str,str], semester:str=None) -> list:
    '''
    PARAMETERS:\n
    session -- should be already logged in\n
    date    -- str  : the day you want, in form of YYYY-MM-DD\n
            -- list : a list, each item in the same form as above\n
            -- int  : the week after the semester started\n
            -- tuple: two str, including the start and the end\n
    semester-- str  : the semester you want e.g. 20221:the first semester of 2022~2023 school year\n
    \n
    RETURN:\n
    [{'Date':'YYYY-MM-DD','Curriculum':[{'No':'1', 'ClassName': 'XXX', 'TeacherName': 'XXX'}]}]
    '''
    session.get('http://hub.m.hust.edu.cn/kcb/todate/datecourseNew.action')
    
    print(semester)
    if semester is not None:
        if isinstance(semester, str) and len(semester) == 5:
            session.post('http://hub.m.hust.edu.cn/kcb/todate/XqJsonCourse.action',data={'xqh':int(semester)})
        else:
            raise TypeError('HUSTPASS: SEMESTER INPUT TYPE ERROR')
    
    resp_html = session.get('http://hub.m.hust.edu.cn/kcb/todate/datecourseNew.action')
    start_date_semester =datetime.strptime(re.search(
        'var sDate = "(.*)";', resp_html.text).group(1), '%Y-%m-%d')  # 从html抓取学期开始日期
    
    query_list = []

    if isinstance(_date_query, int):
        _week = _date_query
        start_date = start_date_semester + timedelta(weeks=_week)
        for i in range(7):
            query_list.append(((start_date+timedelta(days=i)).date().isoformat(), _week))

    elif isinstance(_date_query, tuple):
        if len(_date_query) !=2:
            raise ValueError('HUSTPASS: ONLY ("YYYY-MM-DD","YYYY-MM-DD") LIKE TUPLE IS ACCEPTED')
        _start_date, _end_date = _date_query
        query_list.extend([(qdate, weeks_from(start_date_semester, qdate)) 
                           for qdate in get_dates_between(_start_date,_end_date)])

    elif isinstance(_date_query, list):
        for _item in _date_query:
            if not isinstance(_item, str):
                raise ValueError('HUSTPASS:ONLY "YYYY-MM-DD" ITEM IS ACCEPTED')
            else:
                item = datetime.strptime(_item, '%Y-%m-%d').date().isoformat()
                query_list.append((item, weeks_from(start_date_semester, item)))

    elif isinstance(_date_query, str):
        date_query = datetime.strptime(_date_query, '%Y-%m-%d').date().isoformat()
        query_list.append((date_query, weeks_from(start_date_semester, date_query)))

    else:
        raise TypeError('HUSTPASS: UNSUPPORT TYPE')

    ret = []
    for pack in query_list:
        date, week = pack
        ret.append(_GetOneDay(session, date, week))
    return ret
