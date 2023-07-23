from hust_login import HustPass
import logging
logging.basicConfig(level=logging.DEBUG,\
                    format='[%(levelname)s]  %(message)s')

Uname = input('Uid:')
Upass = input('Pwd:')

with HustPass(Uname, Upass) as s:
    print(s.QueryFreeRoom('2023-4-5'))
    