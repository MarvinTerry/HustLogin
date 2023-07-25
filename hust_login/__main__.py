import sys
import getopt

def __show_usage(code:int=-1):
    print('''\nUSAGE: python -m hust_pass <option>
    -U              Username of pass.hust.edu.cn
    -P              Password of pass.hust.edu.cn
        --autotest  Automatically test api availability, need Uid and Pwd
    -r              Read Uid and Pwd from file
    -v, --version   Version of hust-login
    -h, --help      Get help
    ''')
    if code == -2:
        print('''
    No such file 
''')
    elif code == -3:
        print('''
    The file format should be like {"Uid": "XXX", "Pwd": "XXX"}
    ''')
    return code

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],'U:P:r:hv',['autotest','help','version'])
    except:
        return __show_usage()

    autotest = False

    Uid = None
    Pwd = None

    for opt,arg in opts:
        if opt in ['-h', '--help']:
            return __show_usage(0)
        elif opt in ['-v', '--version']:
            from . import __version__
            return __version__
        elif opt == '--autotest':
            autotest = True
        elif opt =='-U':
            Uid = arg
        elif opt == '-P':
            Pwd = arg
        elif opt == '-r':
            fpath = arg
        else:
            return __show_usage()
        
    if Uid is None and Pwd is None:
        try:
            import json
            with open(fpath,'r') as fp:
                conf = json.loads(fp.read())
                Uid = conf['Uid']
                Pwd = conf['Pwd']
        except FileNotFoundError:
            return __show_usage(-2)
        except json.decoder.JSONDecodeError:
            return __show_usage(-3)
    elif Uid is not None and Pwd is not None:
        pass
    else:
        return __show_usage()
        
    if autotest:
        from .autotest import full_test
        try:
            code = full_test(Uid,Pwd)
        except:
            print('Test Failed')
            return -1
        return code
    
if __name__ == '__main__':
    main()
