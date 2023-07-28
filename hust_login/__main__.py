import sys
from getopt import getopt
from . import HustPass
import logging
logging.basicConfig(level=logging.DEBUG,\
                    format='[%(levelname)s]  %(message)s')

def __show_usage(code:int=-1):
    print('''\nUSAGE: python -m hust_pass <option>
    -U              Username of pass.hust.edu.cn
    -P              Password of pass.hust.edu.cn
        --autotest  Automatically test api availability, need Uid and Pwd
    -f              Read Uid, Pwd and Tasks from file
    -o              Output Result to a file (Unconditional OVERWRITE)
    -v, --version   Version of hust-login
    -h, --help      Get help
    ''')
    if code == -2:
        print('''
    No such file 
''')
    elif code == -3:
        print('''
    The input file format should be like {"Uid": "XXX", "Pwd": "XXX"}\n
    Use \033[0;33;40mpython -m hust_login --inputformat\033[0m to get more info
    ''')
    return code

def __tasker(hpass:HustPass, Dict:dict) -> dict:
    ret = {'Uid':hpass.Uid}
    for key,value in Dict.items():
        if key == 'QueryElectricityBills':
            ret['ElectricityBills'] = __get_result(value, hpass.QueryElectricityBills)
        elif key == 'QuerySchedules':
            ret['Schedules'] = __get_result(value, hpass.QuerySchedules)
        elif key == 'QueryFreeRooms':
            ret['FreeRooms'] = __get_result(value, hpass.QueryFreeRooms)
        elif key == 'QueryEcardBills':
            ret['EcardBills'] = __get_result(value, hpass.QueryEcardBills)
        else:
            continue
    return ret

def __get_result(Dict:dict, Func) -> dict:
    ret = {}
    for key, value in Dict.items():
        if key == 'list':
            ret[key] = Func(value)
        elif key == 'str':
            ret[key] = Func(value)
        elif key == 'tuple':
            ret[key] = Func((value[0],value[1]))
        elif key == 'int':
            ret[key] = Func(value)
        else:
            raise KeyError('UNEXPECTED PARAMETERS')
    return ret

def main():
    try:
        opts, args = getopt(sys.argv[1:],'U:P:f:o:hv',['autotest','help','version','inputformat'])
    except:
        return __show_usage()

    autotest = False
    fpath = None
    opath = None

    for opt,arg in opts:
        if opt in ['-h', '--help']:
            return __show_usage(0)
        elif opt in ['-v', '--version']:
            from . import __version__
            return __version__
        elif opt == '--autotest':
            autotest = True
        elif opt == '--inputformat':
            with open('example.json','r') as fp:
                print(fp.read())
            return 0
        elif opt =='-U':
            Uid = arg
        elif opt == '-P':
            Pwd = arg
        elif opt == '-f':
            fpath = arg
        elif opt == '-o':
            opath = arg
        else:
            return __show_usage()
    

    header = None

    if fpath is not None:
        with open(fpath,'r') as fp:
            import json
            try:
                conf = json.loads(fp.read())
            except FileNotFoundError:
                return __show_usage(-2)
            except json.decoder.JSONDecodeError:
                return __show_usage(-3)
            try:
                Uid = conf['Uid']
                Pwd = conf['Pwd']
            except KeyError:
                return __show_usage(-3)
            try:
                header = conf['Headers']
            except KeyError:
                pass


    try:
        HUSTpass = HustPass(Uid, Pwd, header)
    except NameError:
        return __show_usage()
    except ConnectionRefusedError:
        print('HUSTPASS: Authentication failed')
        return -1
    
    if autotest:
        from .autotest import full_test
        code = full_test(HUSTpass)
        if code != 0:
            print('Test Failed')
            return code
        return 0
    
    if opath is not None:
        try:
            with open(opath,'w') as fp:
                fp.write(json.dumps(__tasker(HUSTpass, conf['Tasks'])))
        except:
            return -1
    else:
        print(__tasker(HUSTpass, conf['Tasks']))
if __name__ == '__main__':
    main()
