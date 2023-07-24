from . import HustPass

def full_test(Uid,Pwd):
    hpass = HustPass(Uid, Pwd)
    try:
        hpass.QueryCurriculum('2023-04-27')
        hpass.QueryCurriculum(['2023-04-27','2023-03-27','2023-04-07'])
        hpass.QueryCurriculum(8)
        hpass.QueryCurriculum(('2023-04-01','2023-04-12'))
    except:
        return 10
    try:
        hpass.QueryElectricityBills('2023-04-27')
        hpass.QueryElectricityBills(['2023-04-27','2023-03-27','2023-04-07'])
        hpass.QueryElectricityBills(('2023-04-01','2023-04-12'))
    except:
        return 20
    try:
        hpass.QueryFreeRoom('2023-09-02')
    except:
        return 30
    return 0