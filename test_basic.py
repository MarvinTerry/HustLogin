from hust_login import HustPass, curriculum
import logging
logging.basicConfig(level=logging.DEBUG,\
                    format='[%(levelname)s]  %(message)s')

Uname = input('Uid:')
Upass = input('Pwd:')

with HustPass(Uname, Upass) as s:
    print(curriculum.GetOneDay(s, '2023-04-01', '7'))