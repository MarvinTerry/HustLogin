import requests
import json
from .utils import DateFormat

def GetFreeRooms(session:requests.Session, _date_query:str) -> dict:
    '''
    PARAMETERS:\n
    session -- should be already logged in\n
    date    -- str  : the day you want, in form of YYYY-MM-DD\n
    \n
    RETURN:\n
    {'Date':'YYYY-MM-DD','Buildings':{'东九楼A':{'No':'1','RoomList': ['A101','A102']}}}
    '''
    if isinstance(_date_query, str):
        date_query = DateFormat(_date_query)
    else:
        raise TypeError('HUSTPASS: UNSUPPORT TYPE')
    
    return _GetOneDay(session, date_query)

__buildings = {
    '东九楼A':'D091',
    '东九楼B':'D092',
    '东九楼C':'D093',
    '东九楼D':'D094',
    '西十二楼S':'C120',
    '西十二楼N':'C121',
    '东十二楼':'D120',
    '西五楼':'C050',
    '东五楼':'D050'
}

def _GetOneDay(session:requests.Session, date_query:str) -> list:    
    
    # 必要的跳转步骤
    session.get('http://mhub.hust.edu.cn/cas/login?redirectUrl=/kxjsController/selectFreeRoom')

    raw_data = []
    # 建立数据结构
    ret = {'Date':date_query,'Buildings':{buiding_name: [{'No': str(i), 'RoomList': []} for i in range(1,13)] for buiding_name in __buildings.keys()}}

    for buiding_id in __buildings.values():
        # 爬取每个教学楼数据
        resp = session.get('http://mhub.hust.edu.cn/kxjsController/selectFreeRoom?sj={}&jxlbh={}'.format(date_query,buiding_id))
        raw_data.extend(json.loads(resp.text)['dataList'])
    
    for item in raw_data:
        ret['Buildings'][item['JXLMC']][item['JC']-1]['Roomlist'].append(item['JSMC'].strip('教室'))
    
    # Del empty ones
    for name in list(ret['Buildings'].keys()):
        _item = ret['Buildings'][name]
        for item in reversed(_item):
            if len(item['RoomList']) == 0:
                _item.remove(item)
        if len(_item) == 0:
            del ret['Buildings'][name]

    return ret
