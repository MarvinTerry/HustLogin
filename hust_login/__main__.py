import sys
import os
import json
from getopt import getopt
from . import HustPass
from ._cli import _show_usage,_tasker
import logging

def main():
    try:
        opts, args = getopt(sys.argv[1:],'U:P:f:o:hv',['autotest','help','version','inputformat','debug'])
    except:
        return _show_usage()

    autotest = False
    log_level = logging.INFO
    fpath = None
    opath = None
    for opt,arg in opts:
        if opt in ['-h', '--help']:
            return _show_usage(0)
        elif opt in ['-v', '--version']:
            from . import __version__
            return __version__
        elif opt == '--autotest':
            autotest = True
        elif opt == '--inputformat':
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example.json'),'r') as fp:
                print(fp.read())
            return 0
        elif opt == '--debug':
            log_level = logging.DEBUG
        elif opt =='-U':
            Uid = arg
        elif opt == '-P':
            Pwd = arg
        elif opt == '-f':
            fpath = arg
        elif opt == '-o':
            opath = arg
        else:
            return _show_usage()

    logging.basicConfig(level=log_level,\
                        format='[%(levelname)s]  %(message)s')
    
    header = None
    if fpath is not None:
        with open(fpath,'r') as fp:
            try:
                conf = json.loads(fp.read())
            except FileNotFoundError:
                return _show_usage(-2)
            except json.decoder.JSONDecodeError:
                return _show_usage(-3)
            try:
                Uid = conf['Uid']
                Pwd = conf['Pwd']
            except KeyError:
                return _show_usage(-3)
            try:
                header = conf['Headers']
            except KeyError:
                pass

    try:
        HUSTpass = HustPass(Uid, Pwd, header)
    except NameError:
        return _show_usage()
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
                fp.write(json.dumps(_tasker(HUSTpass, conf['Tasks'])))
        except:
            return -1
    else:
        print(_tasker(HUSTpass, conf['Tasks']))

if __name__ == '__main__':
    sys.exit(main())
