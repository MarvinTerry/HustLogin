
def cli():
            
    answer = prompt(interface[0])
    if answer['init'] == 'Exit':
        return 0
    
    while 1:
        auth = prompt(login_para[:2])
        try:
            from .. import HustPass
            HUSTpass = HustPass(auth['UID'], auth['PWD'])
            break
        except NameError:
            answer = prompt(login_para[3])
            if not answer['IsExit']:
                return -1
        except ConnectionRefusedError:
            print('HUSTPASS: Authentication failed')
            return -1
        except ValueError as e:
            print(e)
        
    while 1:
        answer = prompt(interface[1])
        if answer['actions'] == 'Exit':
            break
        try:
            if answer['actions'] == 'Bills':
                answer = prompt(interface[2])
                if answer['bills'] == 'Go Back':
                    continue
                date = get_date()
                if answer['bills'] == 'E-card':
                    result = HUSTpass.QueryEcardBills(date)
                elif answer['bills'] == 'Dormitory':
                    result = HUSTpass.QueryElectricityBills(date)
            elif answer['actions'] == 'Curriculum':
                date = get_date()
                result = HUSTpass.QuerySchedules(date)
            elif answer['actions'] == 'Rooms':
                date = get_date()
                result = HUSTpass.QueryFreeRooms(date)

            print(result)
        except:
            print('!!!Error Happened')
        
    print('Cleaning...') # Useless, just for Experience
    return 0

def prompt(arg):
    from PyInquirer import prompt as _prompt#, Separator
    ret = _prompt(arg)
    if not len(ret):
        raise Exception('Do not click, use Enter')
    return ret

def get_quick_date() -> tuple['Today', 'Tomorrow', 'Yesterday']: #type:ignore
    from datetime import datetime, timedelta
    _today = datetime.now()
    _delta = timedelta(days=1)
    return {'Today':_today.date().isoformat(),'Tomorrow':(_today+_delta).date().isoformat(),'Yesterday': (_today-_delta).date().isoformat()}

def get_date() -> str:
    from PyInquirer import prompt
    answer = prompt(login_para[4])
    if answer['DATE'] == 'Type':
        answer = prompt(login_para[2])
    else:
        answer['DATE'] = get_quick_date()[answer['DATE']]
    return answer['DATE']

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
        'message': 'Your Pwd:'
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
    },
    {
        'type':'list',
        'name':'DATE',
        'message':'Which time?',
        'choices':[
            'Today',
            'Tomorrow',
            'Yesterday',
            'Type'
        ]
    }
]
