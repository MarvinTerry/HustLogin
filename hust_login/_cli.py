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

def cli():
    from PyInquirer import prompt#, Separator
    #import prompt_toolkit

    #class PhoneNumberValidator(prompt_toolkit.validation.Validator):
    #    def validate(self, document):
    #        ok = re.match('', document.text)
    #        if not ok:
    #            raise prompt_toolkit.validation.ValidationError(
    #                message='Please enter a valid Uid',
    #                cursor_position=len(document.text))  # Move cursor to end
            
    interface = [
        {
            'type': 'list',
            'name': 'init',
            'message': 'What do you want to do?',
            'choices': [
                'Login',
                'Exit'
            ]
        },
        {
            'type':'list',
            'name':'actions',
            'message':'What you want to do?',
            'choices':[
                'Bills',
                'Curriculum',
                'Rooms',
                'Exit'
            ]
        },
        {
            'type':'list',
            'name':'bills',
            'message':'Which your want?',
            'choices':[
                'Dormitory',
                'E-card',
                'Go Back'
            ]
        }
    ]
    login_para = [
        {
            'type': 'input',
            'name': 'UID',
            'message': 'Your Uid:',
            # 'validate': PhoneNumberValidator
        },
        {
            'type': 'password',
            'name': 'PWD',
            'message': 'Your Pwd'
        },
        {
            'type': 'input',
            'name': 'DATE',
            'message': 'Which time? [format:1970-01-01]'
        },
        {
            'type': 'confirm',
            'name': 'IsExit',
            'message': 'Wrong uid,pwd, try again?',
            'default': 'Ture'
        }
    ]
    
    answer = prompt(interface[0])
    if answer['init'] == 'Exit':
        return 0
    
    while 1:
        auth = prompt(login_para[:2])
        try:
            from . import HustPass
            HUSTpass = HustPass(auth['UID'], auth['PWD'])
        except NameError:
            answer = prompt(login_para[3])
            if not answer['IsExit']:
                break
        except ConnectionRefusedError:
            print('HUSTPASS: Authentication failed')
            return -1
        
    while 1:
        answer = prompt(interface[1])
        if answer['actions'] == 'Exit':
            break
        if answer['actions'] == 'Bills':
            answer = prompt(interface[2])
            if answer['bills'] == 'Go Back':
                continue
            date = prompt(login_para[2])
            if answer['bills'] == 'E-card':
                result = HUSTpass.QueryEcardBills(date)
            elif answer['bills'] == 'Dormitory':
                result = HUSTpass.QueryElectricityBills(date)
        elif answer['actions'] == 'Curriculum':
            date = prompt(login_para[2])
            result = HUSTpass.QuerySchedules(date)
        elif answer['actions'] == 'Rooms':
            date = prompt(login_para[2])
            result = HUSTpass.QueryFreeRooms(date)

        print(result)
        
    print('Cleaning...') # Useless, just for Experience
    return 0

if __name__ == '__main__':
    cli()
