from hust_login import HustPass, curriculum
import logging
logging.basicConfig(level=logging.DEBUG,\
                    format='[%(levelname)s]  %(message)s')

Uname = input('Uid:')
Upass = input('Pwd:')

with HustPass(Uname, Upass) as s:
    print(s.QueryElectricityBills(['2023/7/21','2023/7/21']))
