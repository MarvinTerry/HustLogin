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
    with open('res.json','w') as f:
        f.write(json.dumps(s.QueryEcardBills(
            ['2023-05-06','2023-06-06','2022-10-10']), ensure_ascii=False))
    
    