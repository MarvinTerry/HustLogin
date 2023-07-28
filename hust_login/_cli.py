def _show_usage(code:int=-1):
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

def _tasker(hpass, Dict:dict) -> dict:
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
