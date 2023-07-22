from .login import HustLogin
from .utility_bills import GetElectricityBill
from .curriculum import GetOneDay

class HustPass:
    def __init__(self, Uid:str, Pwd:str, headers:dict=None) -> None:
        self.Session = HustLogin(Uid, Pwd, headers)
        self.Uid = Uid

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, trace):
        if type is not None:
            return False
        return True

    def QueryElectricityBills(self, QueryDates:list) -> dict:
        r=self.Session.get('http://pass.hust.edu.cn/cas/login?service=http://sdhq.hust.edu.cn/ICBS/hust/cas/neusoftcas.aspx')
        print(r.cookies)
        return GetElectricityBill(self.Session, self.Uid, QueryDates)
    
    def QueryCurriculum(self, day:str, week:str) -> list:
        return GetOneDay(self.Session, day, week)