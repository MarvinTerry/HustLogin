import requests
import json
from datetime import datetime

def GetFreeRooms(session:requests.Session, _date_query:str) -> dict:
    '''
    PARAMETERS:\n
    session -- should be already logged in\n
    date    -- str  : the day you want, in form of YYYY-MM-DD\n
    \n
    RETURN:\n
    {'Date':'YYYY-MM-DD','Buildings':['东九楼A':{'No':'1','Roomlist': ['A101','A102']}]}
    '''
    if isinstance(_date_query, str):
        date_query = datetime.strptime(_date_query, '%Y-%m-%d').date().isoformat()
    else:
        raise TypeError('HUSTPASS: UNSUPPORT TYPE')
    
    buildings = {
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
    
    # 必要的跳转步骤
    session.get('http://mhub.hust.edu.cn/cas/login?redirectUrl=/kxjsController/selectFreeRoom')

    raw_data = []
    # 建立数据结构(AI写的，蛮炫酷)
    ret = {'date':date_query,'buildings':{buiding_name: [{'No': str(i), 'roomlist': []} for i in range(1,13)] for buiding_name,buiding_id in buildings.items()}}

    for buiding_name,buiding_id in buildings.items():
        # 爬取每个教学楼数据
        resp = session.get('http://mhub.hust.edu.cn/kxjsController/selectFreeRoom?sj={}&jxlbh={}'.format(date_query,buiding_id))
        raw_data.extend(json.loads(resp.text)['dataList'])
    
    for item in raw_data:
        ret['buildings'][item['JXLMC']][item['JC']-1]['roomlist'].append(item['JSMC'].strip('教室'))

    return ret
