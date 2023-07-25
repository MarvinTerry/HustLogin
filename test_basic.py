from hust_login import HustPass
import logging
import json
logging.basicConfig(level=logging.DEBUG,\
                    format='[%(levelname)s]  %(message)s')

# Uname = input('Uid:')
# Upass = input('Pwd:')

# secret.txt 被ignore了
with open('secret.txt', 'r') as f:
    Uname,Upass = f.read().split('\n')


with HustPass(Uname, Upass) as s:
    with open('res.json','w', encoding='utf-8') as f:
        f.write(json.dumps(s.QueryCurriculum(
            ('2023-04-03','2023-04-10')), ensure_ascii=False))
    
    