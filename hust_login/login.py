import requests
from logging import root as log
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json
import re
from base64 import b64encode, b64decode
from .decaptcha import decaptcha


def HustLogin(username:str, password:str, headers:dict=None) -> requests.Session:# 以便ide进行类型检查与代码补全
    '''
    PARAMETERS:\n
    username -- Username of pass.hust.edu.cn  e.g. U2022XXXXX\n
    password -- Password of pass.hust.edu.cn\n
    headers  -- Headers you want to use, optional
    '''
    # 输入类型检查
    if not isinstance(username, str) or not isinstance(password, str):
        raise TypeError('HUSTPASS: CHECK YOUR UID AND PWD TYPE')
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
    else:
        if not isinstance(headers, dict):
            raise TypeError('HUSTPASS: CHECK YOUR HEADERS TYPE')
    # 输入有效检查
    if len(username)==0 or len(password)==0:
        raise ValueError('HUSTPASS: YOUR UID OR PWD IS EMPTY')
    try:
        headers['User-Agent']
    except:
        raise ValueError('HUSTPASS: YOUR HEADERS DO NOT INCLUDE UA')
    # 建立session
    log.info('setting up session...')
    r = requests.session()
    r.headers.update(headers)
    # 请求网站HTML
    login_html = r.get('https://pass.hust.edu.cn/cas/login')
    # 检查是否需要输入验证码
    # NOTE:未取得不使用验证码的网页样本，这个判断可能不符合预期
    captcha_check = re.search(
        '<div class="ide-code-box">(.*)</div>', login_html.text, re.S) is not None 
    if captcha_check:
        # 请求验证码图片
        captcha_img = r.get('https://pass.hust.edu.cn/cas/code', stream=True)
        log.info('captcha detected, trying to decaptcha...')
    # 请求公钥并加密用户名密码
    log.debug('encrypting u/p...')
    pub_key = RSA.import_key(b64decode(json.loads(
        r.post('https://pass.hust.edu.cn/cas/rsa').text)['publicKey']))
    cipher = PKCS1_v1_5.new(pub_key)
    encrypted_u = b64encode(cipher.encrypt(username.encode())).decode()
    encrypted_p = b64encode(cipher.encrypt(password.encode())).decode()
    # 定位form
    form = re.search(
        '<form id="loginForm" (.*)</form>', login_html.text, re.S).group(0)# 忽略换行符
    # 抓取ticket
    nonce = re.search(
        '<input type="hidden" id="lt" name="lt" value="(.*)" />', form).group(1)
    # 抓取execution
    execution = re.search(
        '<input type="hidden" name="execution" value="(.*)" />', form).group(1)
    post_params = {
        "rsa": None,
        "ul": encrypted_u,
        "pl": encrypted_p,
        "code": None if not captcha_check else decaptcha(captcha_img.content).strip(),
        "phoneCode": None,
        "lt": nonce,
        "execution": execution,
        "_eventId": "submit"
    }
    log.debug('posting login-form...')
    resp = r.post(
        "https://pass.hust.edu.cn/cas/login",
        data=post_params,
        allow_redirects=False
    )
    try:
        resp.headers['Location']
    except:
        raise ConnectionRefusedError("---HustPass Failed---")
    log.info("---HustPass Succeed---")
    log.debug('Thank you for using hust_login')
    return r

def CheckLoginStatu(session:requests.Session) -> bool:
    '''
    Check login statu\n
    Return False if is not logged in
    '''
    ret = session.get('https://one.hust.edu.cn')
    if ret.status_code != 200:
        log.warning('HUSTPASS: check login failed, code:{}'.format(ret.status_code))
        return False
    return True