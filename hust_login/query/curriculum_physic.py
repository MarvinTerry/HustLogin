# 查询物理实验课表
import requests
import json

def GetPhysicsLab(session:requests.Session, add_file_link:bool = True):

    if not isinstance(session, requests.Session):
        raise TypeError('HUSTPASS: CHECK YOUR session INPUT TYPE')

    resp_json = session.get('http://empxk.hust.edu.cn/weixin/WeChatChooseCourse/getMyCourseSchedule')
    resp = json.loads(resp_json.text)
    if resp['state'] == '0000':

        load = len(resp['data'])
        if load == 1 or load == 0:
            raise Exception('No Data')

        ret = []
        for item in resp['data']:
            if len(item) == 1:
                continue # ignore
            _statu = item['status']
            if _statu == 1:
                statu = 'Normal'
            elif _statu == 3:
                statu = 'Absent'
            elif _statu == 4:
                statu = 'Leave' # 请假
            res = {
            'Name':item['course_name'],
            'TableNum':item['room_test_num'],
            'Teacher':item['user_name'],
            'Place':item['room_name'],
            'Time':{'Time of the Day':item['start_time'], # 2023-10-09 14:30:00
                    'Day of the Week':item['week_day'], # 1-7
                    'Week':item['week_num'], # num
                    'Sections':item['session_name']}, # 上午/下午/晚上
            'Statu':statu}
            if add_file_link:
                res['FileLinks'] = 'http://empxk.hust.edu.cn/weixin/course_resources.html?'+str(item['course_id'])
                # http://empxk.hust.edu.cn/weixin/introduction.html? + item['course_id'] is the intro
            ret.append(res)

        return ret
    else:
        raise Exception(resp['msg'])
