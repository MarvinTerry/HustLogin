from hust_login.login import HustPass


with HustPass('', '') as s:
    resp = s.get('http://m.hust.edu.cn/wechat/apps_center.jsp')
    print(resp.text)
