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
    with open('curriculum.json','w', encoding='utf-8') as f:
        f.write(json.dumps(s.QuerySchedules(('2023-08-28','2023-09-01'),semester='20231'), ensure_ascii=False))
    # with open('ecard_bill.json','w', encoding='utf-8') as f:
    #     f.write(json.dumps(s.QueryEcardBills('2023-04'), ensure_ascii=False))
    # with open('free_room.json','w', encoding='utf-8') as f:
    #     f.write(json.dumps(s.QueryFreeRooms('2023-04-03'), ensure_ascii=False))
    # with open('electricity_bill.json','w', encoding='utf-8') as f:
    #     f.write(json.dumps(s.QueryElectricityBills(('2023-04-03','2023-04-10')), ensure_ascii=False))
        
    