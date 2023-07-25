from .login import HustLogin, CheckLoginStatu
from .utility_bills import GetElectricityBill
from .curriculum import GetCurriculum
from .free_room import GetFreeRoom
from .ecard_bills import GetEcardBills

class HustPass_NotLoged(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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

    def CheckLoged(self):
        if not CheckLoginStatu(self.Session):
            raise HustPass_NotLoged

    def QueryElectricityBills(self, QueryDates:str|list[str]|tuple[str,str]) -> dict:
        '''
        PARAMETERS:\n
        QueryDates  -- str  : in form of '2023-7-21' or '2023/7/21'\n
                    -- list : a list, each item in the same form\n
                    -- tuple: two str, including the start and the end\n
        \n
        RETURN:\n
        {'RoomName': 'XXX', 'RemainPower': 'XXX', 'DayCost': [{'daycost': 'XXX', 'date': 'YYYY-MM-DD', 'money': 'XXX'}]}
        '''
        self.CheckLoged()
        return GetElectricityBill(self.Session, self.Uid, QueryDates)
    
    def QueryCurriculum(self, QueryData:str|list[str]|int|tuple[str,str]) -> list:
        '''
        PARAMETERS:\n
        session -- should be already logged in\n
        date    -- str  : the day you want, in form of YYYY-MM-DD\n
                -- list : a list, each item in the same form as above\n
                -- int  : the week after the semester started\n
                -- tuple: two str, including the start and the end\n
        \n
        RETURN:\n
        [{'Date':'YYYY-MM-DD','Curriculum':[{'No':'1', 'ClassName': 'XXX', 'TeacherName': 'XXX'}]}]
        '''
        self.CheckLoged()
        return GetCurriculum(self.Session, QueryData)
    
    def QueryFreeRoom(self, QueryData:str) -> dict:
        '''
        PARAMETERS:\n
        session -- should be already logged in\n
        date    -- str  : the day you want, in form of YYYY-MM-DD\n
        \n
        RETURN:\n
        {'Date':'YYYY-MM-DD','Buildings':['东九楼A':{'No':'1','Roomlist': ['A101','A102']}]}
        '''
        self.CheckLoged()
        return GetFreeRoom(self.Session, QueryData)
    
    def QueryEcardBills(self, QueryData:str) -> list:
        '''
        PARAMETERS:\n
        session     -- should be already logged in\n
        Uid         -- str  : your student uid\n
        QueryDates  -- str  : in form of '2023-7-21' or '2023/7/21'\n
                    -- str  : in form of '2023-7' or '2023/7'
                    -- list : a list, each item in the same form\n
                    -- tuple: two str, including the start and the end\n
        \n
        RETURN:\n

        '''
        self.CheckLoged()
        return GetEcardBills(self.Session, QueryData)