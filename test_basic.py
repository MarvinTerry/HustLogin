from hust_login.login import HustPass
import logging
logging.basicConfig(level=logging.DEBUG,\
                    format='[%(levelname)s]  %(message)s')

Uname = input('Uid:')
Upass = input('Pwd:')

with HustPass(Uname, Upass) as s:
    resp = s.get('http://m.hust.edu.cn/wechat/apps_center.jsp')
    print(resp.text)
