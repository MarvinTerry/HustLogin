import sys
import getopt

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],'U:P:',['autotest'])
    except:
        print('USAGE: python -m hust_pass --autotest')

    bad_param = False
    autotest = False

    for opt,arg in opts:
        if opt in ['--autotest']:
            autotest = True
        elif opt =='-U':
            Uid = arg
        elif opt == '-P':
            Pwd = arg
        else:
            bad_param = True
            break

    if bad_param:
        print('USAGE: python -m hust_pass --autotest')
        return
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
