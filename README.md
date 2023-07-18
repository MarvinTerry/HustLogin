# HustLogin
A python-lib for authenticating HustPass

## Requirements
```
Pillow==10.0.0
pycryptodome==3.18.0
pytesseract==0.3.10
Requests==2.31.0
```

## Documentation
```hust_login.HustLogin(username, password)```
  PARAMETERS:
  - username -- Username of pass.hust.edu.cn  e.g. U2022XXXXX
  - password -- Password of pass.hust.edu.cn

  RETURNS:
  - A ```requests.Session``` object that is already logged in

> NO MORE HUSTPASS, MY BRO!!!

> BE CREATIVE, BE WATER!!!

## Demo
Demonstrating how to query the exam result
```python
from hust_login import HustLogin

with HustLogin('U2022XXXXX', 'YOUR-PASSWORD') as s:


```
