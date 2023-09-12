# 查询课表
import requests
import json
import re
from datetime import datetime, timedelta
from hust_login.query.utils import DateFormat

def QuerySchedules(session:requests.Session, _date_query:str|list[str]|int|tuple[str,str], semester:str=None, with_labexp:bool=True) -> list:
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
    [{'Date':'YYYY-MM-DD','Curriculum':[{'No':'1', 'Course': 'XXX', 'TeacherName': 'XXX', 'Place':'XXX'}]}]
    '''
    session.get('http://hub.m.hust.edu.cn/kcb/todate/datecourseNew.action')
    
    #print(semester)
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
        query_list.extend([(qdate, __weeks_from(start_date_semester, qdate)) 
                           for qdate in __get_dates_between(_start_date,_end_date)])

    elif isinstance(_date_query, list):
        for _item in _date_query:
            if not isinstance(_item, str):
                raise ValueError('HUSTPASS:ONLY "YYYY-MM-DD" ITEM IS ACCEPTED')
            else:
                item = DateFormat(_item)
                query_list.append((item, __weeks_from(start_date_semester, item)))

    elif isinstance(_date_query, str):
        date_query = DateFormat(_date_query)
        query_list.append((date_query, __weeks_from(start_date_semester, date_query)))

    else:
        raise TypeError('HUSTPASS: UNSUPPORT TYPE')

    ret = []
    if not with_labexp:
        for pack in query_list:
            date, week = pack
            ret.append(__GetOneDay(session, date, week))
    else:
        from .curriculum_physic import GetPhysicsLab
        lab_data = GetPhysicsLab(session, False)
        for date, week in query_list:
            data = __GetOneDay(session, date, week)
            for c_info in data['Curriculum']:
                if c_info['Place'] == '科技楼北楼物理实验教学中心':
                    new_data = lab_data[date]
                    data['Curriculum']['Course'] = new_data['Name']
                    data['Curriculum']['Teacher'] = new_data['Teacher']
                    data['Curriculum']['Place'] = new_data['Place']
    return ret
    
def __GetOneDay(session:requests.Session, date_query:str, week:int) -> tuple[list[dict], dict]:
    resp_api = session.get('http://hub.m.hust.edu.cn/kcb/todate/JsonCourse.action?sj={}&zc={}'.format(date_query, week))
    content=json.loads(resp_api.text)
    class_list = []
    ret = {'Date':date_query} 
    for item in content:
        if item['kc'][0]['JSMC']=='—':
            continue
        class_list.append({'No':item['jcx'],'Course':item['kc'][0]['KCMC'],'Teacher':item['kc'][0]['XM'],'Place':item['kc'][0]['JSMC']})
    ret['Curriculum'] = class_list
    return ret

def __weeks_from(start_date, date):
    if not isinstance(start_date, datetime):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    date = datetime.strptime(date, '%Y-%m-%d')
    delta = date - start_date
    return delta.days // 7 + 1

def __get_dates_between(start_date_iso, end_date_iso):
    start_date = datetime.fromisoformat(start_date_iso)
    end_date = datetime.fromisoformat(end_date_iso)
    
    if start_date > end_date:
        start_date,end_date = end_date,start_date

    num_days = (end_date - start_date).days + 1
    dates_list = [start_date + timedelta(days=i) for i in range(num_days)]
    
    return [date.date().isoformat() for date in dates_list]
