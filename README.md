# HustLogin
A python-lib for authenticating HustPass@2023

> Faster, Easier, Lighter

Attention: HustPass login protocol underwent a major update on 2023/05/23, moving from DES to RSA, previous login libraries are now deprecated.




## Requirements
```
Pillow==10.0.0
pycryptodome==3.18.0
pytesseract==0.3.10
Requests==2.31.0
```

## Documentation
### **```hust_login.HustLogin(username, password)```**

  PARAMETERS:
  - username -- Username of pass.hust.edu.cn  e.g. U2022XXXXX
  - password -- Password of pass.hust.edu.cn

  RETURNS:
  - A **```requests.Session```** object that is already logged in
    - use it the same way you use requests, e.g.
      ```python
      s = HustLogin('U2022XXXXX','YOUR-PASSWORD')
      s.get(your_url)
      ```

> NO MORE HUSTPASS, MY BRO!!!

> BE CREATIVE, BE WATER!!!

## Demo
Demonstrating how to query the exam result
- CODE:
  ```python
  from hust_login import HustLogin
  from bs4 import BeautifulSoup
  
  with HustLogin('U2022XXXXX','YOUR-PASSWORD') as s:
      ret = s.get('http://hub.m.hust.edu.cn/cj/cjsearch/findcjinfo.action?xn=2022&xq=0')
      soup = BeautifulSoup(ret.content, 'html.parser')
      for row in soup.find_all('tr'):
          for col in row.contents:
              print(col.text.strip(), end=" ")
          print("")
  ```
- RESULT:
  ```
  setting up session...
  encrypting u/p...
  decaptching...
  captcha_code:4608
  posting login-form...
  ---HustPass Succeed---
   课程名称  课程学分  课程成绩  备注  
   微积分（一）（上）  5.5  90
   综合英语（一）  3.5  94
   线性代数  2.5  92
   工程制图（一）  2.5  98
   综合英语（二）  3.5  93
   微积分（一）（下）  5.5  94
    ...
    ...
    ...
   加权排名成绩  91.71
   必修课总学分  50.50
   公选课总学分  2.00
   总学分  52.5
  ```
