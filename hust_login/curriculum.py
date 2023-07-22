# 查询课表
import requests
import json
from .login import CheckLoginStatu
import re
from datetime import datetime

def weeks_from(start_date, date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    date = datetime.strptime(date, '%Y-%m-%d')
    delta = date - start_date
    return delta.days // 7 + 1

def GetOneDay(session:requests.Session, date_query:str) -> list[dict]:
    '''
    PARAMETERS:\n
    session -- should be already logged in\n
    date     -- the day you want, in form of YYYY-MM-DD\n
    \n
    RETURN:\n
    [{'No':'1', 'ClassName': 'XXX', 'TeacherName': 'XXX'}}]
    '''
    if not (isinstance(session, requests.Session) and isinstance(date_query, str)):
        raise TypeError('HUSTPASS: CHECK YOUR session, day AND week INPUT TYPE')
    
    if not CheckLoginStatu(session):
        raise ConnectionRefusedError('HUSTPASS: YOU HAVENT LOGGED IN')
    
    date_query = datetime.strptime(date_query, '%Y-%m-%d').date().isoformat() # 保证日期格式标准，即补充用户可能忘记添加的0
    
    resp_html = session.get('http://hub.m.hust.edu.cn/kcb/todate/datecourseNew.action')

    start_date_semester = re.search(
        'var sDate = "(.*)";', resp_html.text).group(1) # 从html抓取学期开始日期
    
    week = weeks_from(start_date_semester, date_query)
    
    resp_api = session.get('http://hub.m.hust.edu.cn/kcb/todate/JsonCourse.action?sj={}&zc={}'.format(date_query, week))
    content=json.loads(resp_api.text)
    ret = []
    for item in content:
        if item['kc'][0]['JSMC']=='—':
            continue
        ret.append({'No':item['jcx'],'ClassName':item['kc'][0]['KCMC'],'TeacherName':item['kc'][0]['XM']})
    return ret