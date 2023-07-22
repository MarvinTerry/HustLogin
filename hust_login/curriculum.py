# 查询课表
import requests
import json
from .login import CheckLoginStatu

def GetOneDay(session:requests.Session, day:str, week:str) -> list[dict]:
    '''
    PARAMETERS:\n
    session -- should be already logged in\n
    day     -- the day you want, in form of 2023-04-01\n
    week    -- the weeks since term started， in form of 1\n
    \n
    RETURN:\n
    [{'No':'1', 'ClassName': 'XXX', 'TeacherName': 'XXX'}}]
    '''
    if not (isinstance(session, requests.Session) and isinstance(day, str) and isinstance(week, str)):
        raise TypeError('HUSTPASS: CHECK YOUR session, day AND week INPUT TYPE')
    
    if not CheckLoginStatu(session):
        raise ConnectionRefusedError('HUSTPASS: YOU HAVENT LOGGED IN')
    
    resp = session.get('http://hub.m.hust.edu.cn/kcb/todate/JsonCourse.action?sj={}&zc={}'.format(day, week))
    content=json.loads(resp.text)
    ret = []
    for item in content:
        if item['kc'][0]['JSMC']=='—':
            continue
        ret.append({'No':item['jcx'],'ClassName':item['kc'][0]['KCMC'],'TeacherName':item['kc'][0]['XM']})
    return ret