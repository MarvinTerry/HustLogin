# HustPass
用于验证 HustPass@2023 的 python-lib

![HustPassLogo](https://pass.hust.edu.cn/cas/comm/image/logo-inside.png)

[![Automated Testing of Interface Availability](https://github.com/MarvinTerry/HustLogin/actions/workflows/auto-test.yml/badge.svg?branch=main)](https://github.com/MarvinTerry/HustLogin/actions/workflows/auto-test.yml)

> 更快、更简单、更方便

注意：HustPass登录协议于2023年5月23日进行了重大更新，从DES迁移到RSA，以前的登录库现已不可使用。

## 安装

该库已在 PyPI 上公开可用 **[hust_login](https://pypi.org/project/hust-login/)**

通过单行命令安装，pip将自动处理依赖。

```
pip install hust_login
```

此外，您需要安装```tesseract-ocr```后端：

- Win：[在此处下载二进制文件](https://tesseract-ocr.github.io/tessdoc/Downloads.html)，推荐“3rd party Windows exe’s/installer”。
- Linux：运行```sudo apt install tesseract-ocr```

## 文档
### **```hust_login.HustLogin(用户名，密码，标头（可选)```**

   参数：
   - 用户名 -- pass.hust.edu.cn 的用户名 例如 U2022XXXXX
   - 密码 -- pass.hust.edu.cn 的密码
   - 标头 -- 您希望使用的标头，可选

   返回：
   - 已登录的 **```requests.Session```** 对象
     - 使用它的方式与使用请求的方式相同，例如
       ```python
       s = hust_login.HustPass('U2022XXXXX','您的密码')
       ret = s.get(your_url)
       print(ret.text)
       ```
### **```hust_login.HustPass(用户名，密码，标头（可选))```

   参数：与HustLogin相同

   返回：
   - 一个类，包含QueryElectricityBills，QueryCurriculum，QueryFreeRoom等已包装的常用函数。 

> 发挥创意！！！

## Demo
演示如何查询考试成绩
- CODE:
  ```python
  from hust_login import HustPass
  from bs4 import BeautifulSoup
  
  with HustPass('U2022XXXXX','YOUR-PASSWORD') as s:
      ret = s.get('http://hub.m.hust.edu.cn/cj/cjsearch/findcjinfo.action?xn=2022&xq=0')
      soup = BeautifulSoup(ret.content, 'html.parser')
      for row in soup.find_all('tr'):
          for col in row.contents:
              print(col.text.strip(), end=" ")
          print("")
   ```
   **建议**在 ```with``` 语句中调用 ```HustPass```，如图所示。
- RESULT:
   ```
   setting up session...
   captcha detected, trying to decaptcha...
   decaptching...
   encrypting u/p...
   captcha_code:0344
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

## 发展

如果该库已过时，请尝试发出pr以使该库再次工作！

在常规登录期间启用加密和发布登录表单的 js 脚本是公开可用的 [login_standar.js?v=20230523](https://pass.hust.edu.cn/cas/comm/js/login_standar.js?v=20230523)。 我的工作是将js翻译成python并处理验证码。

如果您正在开发该库的较新版本，以下是值得一提的内容：

- 加密：
   - PublicKey采用base64编码，请先解码。
   - 您加密的usr/pass应该以base64编码，并转换为文本而不是字节。 请更深入地研究我的代码，看看它是如何工作的。
- 解码器
   - 使用```BytesIO``` 方法将包含 gif 的字节流转换为文件。
   - 采用 Genius 方法对 4 帧 gif 进行组合和去噪：据观察，**数量**像素至少会出现在 3 帧中，而**噪声**像素小于 2。这提供了一种超级准确的方法来对图片进行去噪。 这是代码片段，尝试理解：
     ```python
     img_merge = Image.new(mode='L',size=(width,height),color=255)
     for pos in [(x,y) for x in range(width) for y in range(height)]:
         if sum([img.getpixel(pos) < 254 for img in img_list]) >= 3:
            img_merge.putpixel(pos,0)
     ``` 
     ![org](images/captcha_code.gif) ![processed](images/captcha_code_processed.png)
- 网络
   - 一个常见的假UA是必不可少的！ HustPass 已阻止 python-requests 的默认UA。
